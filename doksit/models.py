"""
Here are defined base classes.
"""

import abc
import inspect
import os
import os.path
import re
import subprocess

from typing import Any, Dict, List, Optional, Tuple

import yaml

from doksit.data_types import MyOrderedDict
from doksit.helpers import validate_file_path

REPOSITORY_URL_REGEX = re.compile(r"origin\t([\S]+) ")
BRANCH_NAME_REGEX = re.compile(r"\* (.+)\n")

CLASS_REGEX = re.compile(r"^class (\w+):?|\(")
METHOD_REGEX = re.compile(r"^    def ([\w_]+)\((self|cls)")
STATIC_METHOD_REGEX = re.compile(r"    def ([\w_]+)\(")
FUNCTION_REGEX = re.compile(r"^def ([\w_]+)")


class Base:
    """
    Base is the lowest class with predefined abtract methods and useful normal
    methods which may be used for writing other API documentation generator
    based on different docstring style than is Doksit / Google style.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_api_documentation(self):
        """
        Abstract method for getting final parsed API documentation, which may
        be displayed to an user.
        """
        pass

    @property
    def config(self) -> Dict[str, Any]:
        """
        Get parsed content of `.doksit.yml` file if it exists or return `None`.

        Example:
            {"docstring": "doksit"}

        Raises:
            yaml.YAMLError:
                Invalid syntax in the config file.
        """
        try:
            with open(".doksit.yml") as file:
                file_content = file.read()
        except FileNotFoundError:
            return None

        return yaml.load(file_content)

    @property
    def current_branch(self) -> Optional[str]:
        """
        Get a current branch name.

        This works only for those who are using Git. If the Git is not used,
        , then `None` will be returned.

        Example:
            "master"
        """
        try:
            current_branch = subprocess.check_output(
                ["git", "branch"], universal_newlines=True)
        except subprocess.CalledProcessError:
            return None

        return BRANCH_NAME_REGEX.search(current_branch).group(1)

    @property
    def has_template(self) -> bool:
        """
        Whether an user has a template (`docs/_api.md`) or not.
        """
        return os.path.isfile("docs/_api.md")

    @property
    def repository_prefix(self) -> Optional[str]:
        """
        Get GitHub repository URL including suffix `/blob/<branch_name>/`.

        This attribute will be used as a prefix (user must have GitHub) with
        a file path to create an absolute URL to the given file to see its
        content.

        Example:
            "https://github.com/nait-aul/doksit/blob/master/"
        """
        if self.repository_url is not None and self.current_branch is not \
                None:
            return self.repository_url + "/blob/" + self.current_branch + "/"
        else:
            return None

    @property
    def repository_url(self) -> Optional[str]:
        """
        Get an absolute URL path to a Github repository.

        If an user is not using Git & GitHub, then no error will be raised
        and returned only `None`.

        Example:
            "https://github.com/nait-aul/doksit"
        """
        try:
            remote_repository = subprocess.check_output(
                ["git", "remote", "-v"], universal_newlines=True)
        except subprocess.CalledProcessError:
            return None

        repository_url = \
            REPOSITORY_URL_REGEX.search(remote_repository).group(1)

        if repository_url.endswith(".git"):
            repository_url = repository_url[:-4]

        return repository_url

    @staticmethod
    def get_line_numbers(object_name: Any) -> str:
        """
        Find on which lines is the given object defined / located.

        Arguments:
            object_name:
                For which class, method, function to get the line numbers.

        Note:
            There is a problem for defined CLI commands (functions) using a
            `click` package. It will raise `TypeError. Therefore it
            will be silenced and returned only `#`.

        Returns:
            Range, where the object definition starts and ends.

        Example:
            "#L10-L25"
        """
        try:
            source_lines, starting_line = inspect.getsourcelines(object_name)
        except TypeError:
            return "#"

        ending_line = starting_line + len(source_lines) - 1

        return "#L{starting_line}-L{ending_line}" \
            .format(starting_line=starting_line, ending_line=ending_line)

    def get_source_code_url(self, module: Any, object_name: Any=None) -> str:
        """
        Get an absolute path to the source file / object on GiHub.

        If this method is called for an object, then a suffix (object location)
        will be added for using GitHub feature line highlights.

        Arguments:
            module:
                Module object.
            object_name:
                Class / method / function object.

        Returns:
            The absolute URL path or empty string if an user isn't using Git &
            GitHub.

        Example:
            "https://.../nait-aul/doksit/blob/master/doksit/api.py#L1-L10"
        """
        repository_prefix = self.repository_prefix

        if repository_prefix is not None:
            module_path = module.__name__.replace(".", "/") + ".py"
            url = "[source](" + str(repository_prefix) + module_path

            if object_name is not None:
                url += self.get_line_numbers(object_name)

            return url + ")\n\n"
        else:
            return ""

    def find_files(self, package: str) -> List[str]:
        """
        Browse the given package directory and find all Python files.

        Note:
            Files in the `__pycache__` subdirectories are excluded. The same
            goes for the `__init__.py` and `__main__.py` files.

        Arguments:
            package:
                Relative path to the Python package directory.

        Returns:
            List of found Python files (their relative paths).

        Example:
            ["package/module.py", "package/subpackage/module.py"]
        """
        file_paths = []

        if self.has_template:
            with open("docs/_api.md") as file:
                file_content = file.read()

            path_regex = re.compile(r"{{ ?([\S]+) ?}}")
            found_paths = path_regex.findall(file_content)

            for file in found_paths:
                file_paths.append(os.path.join(package, file))

            validated_paths = tuple(map(validate_file_path, file_paths))

            if False in validated_paths:
                which_file_path = validated_paths.index(False)
                invalid_file_path = found_paths[which_file_path]

                raise ValueError("Invalid file path '{file_path}' in the "
                                 "'docs/_api.md' template.".format(
                                     file_path=invalid_file_path))
        else:
            ignored_files = ("__init__.py", "__main__.py")

            for root, _, files in os.walk(package):
                if os.path.basename(root) != "__pycache__":
                    for file in sorted(files):
                        if file.endswith(".py") and file not in ignored_files:
                            file_paths.append(os.path.join(root, file))

        return file_paths

    @staticmethod
    def read_file(file_path: str) -> Tuple[str, MyOrderedDict, List[str]]:
        """
        Find classes with methods and functions in the given file exactly in
        the order as they are defined.

        Note:
            Protected / prohibited methods / functions will be skipped. The
            same goes for magic methods except the `__init__`.

        Arguments:
            file_path:
                Relative path to a Python file.

        Returns:
            The relative file path, classes with methods and list of functions.

        Example:
            (
                "package/module.py",
                MyOrderedDict([("Foo", ["__init__", "method_name"])]),
                ["function_name"]
            )
        """
        with open(file_path) as file:
            file_content = file.readlines()

        classes = MyOrderedDict()
        functions = []

        for line_number, line in enumerate(file_content):
            if line.startswith("class "):
                classes[CLASS_REGEX.search(line).group(1)] = []

            elif line.lstrip().startswith("def "):
                if METHOD_REGEX.search(line):
                    method_name = METHOD_REGEX.search(line).group(1)

                    if method_name == "__init__" or \
                            not method_name.startswith("_"):
                        classes[classes.last()].append(method_name)

                elif FUNCTION_REGEX.search(line):
                    function_name = FUNCTION_REGEX.search(line).group(1)

                    if not function_name.startswith("_"):
                        functions.append(function_name)

                else:
                    previous_line = file_content[line_number - 1].lstrip()

                    if previous_line == "@staticmethod\n":
                        method_name = STATIC_METHOD_REGEX.search(line).group(1)

                        if not method_name.startswith("_"):
                            classes[classes.last()].append(method_name)

        return file_path, classes, functions


ARGUMENT_REGEX = re.compile(r"([\w_\*]+)")
BUILTIN_TYPE_REGEX = re.compile(r"<class '([\S]+)'>")
LANGUAGE_REGEX = re.compile(r"Example: \((\w+)\)")
PARAMETER_REGEX = re.compile(r"[\w_]+:?([\w_\[\]\.]+)?=?(.+)?")


class DocstringParser:
    """
    Parser for both Google (Napoleon) docstring style and upgraded Doksit
    layer on top of it.
    """

    def markdown_arguments_section(self, line_number: int,
                                   docstring: List[str],
                                   object_name: Any=None) -> List[str]:
        """
        Markdown the `Arguments` section.

        Arguments:
            line_number (int):
                Where the `Arguments` section starts.
            docstring (List[str]):
                Split docstring.
            object_name (Any):
                Function / method object for getting its parameters annotation.

        Example: (markdown)
                Arguments:
                    one:
                        Argument description.
                    two:
                        Argument description
                        over two lines.
                    three: Argument description.
                    four: Arguments description
                        over two lines.

            or

                Arguments:
                    one (int):
                        Argument description.
                    two (str, optional, default "foo")
                        Argument description
                        over two lines.
                    three (int): Argument description.
                    four (str, optional, default "foo"): Argument description
                        over two lines.

            converts to:

                **Arguments:**

                - one (int):
                    - Argument description.
                - two (str, optional, default "foo"):
                    - Argument description
                      over two lines.
                - three (int):
                    - Argument description.
                - four (str, optional, default, "foo"):
                    - Argument description
                      over two lines.

        Note:
            If an user didn't write the argument data type, then it will be
            automatically inserted.

        Returns:
            Updated split docstring with the markdowned `Arguments`
            section.
        """
        # Codes below are shared with `markdown_attributes_section` method, but
        # some of them will be only for this method.

        docstring[line_number] = "**" + docstring[line_number] + "**\n"

        insert_text = []
        is_first_line_description = False
        is_arguments_section = True if object_name is not None else False

        if is_arguments_section:
            parsed_parameters = self._parse_parameters(object_name)

            # An user may use short header variant "Args:", but for output
            # is better explicit "Arguments:" header.

            docstring[line_number] = "**Arguments:**\n"

        for number, line in enumerate(docstring[line_number + 1:],
                                      start=line_number + 1):
            if line.startswith(" " * 8):  # Argument description.
                lstrip_line = line.lstrip(" ")

                if is_first_line_description:
                    docstring[number] = "    - " + lstrip_line
                    is_first_line_description = False
                else:
                    docstring[number] = " " * 6 + lstrip_line

            elif line.startswith(" " * 4):  # Line with argument name.
                lstrip_line = line.lstrip(" ")

                if line.endswith(":"):
                    docstring[number] = "- " + lstrip_line
                    is_first_line_description = True  # For the next line.

                elif ":" in lstrip_line:
                    colon_index = lstrip_line.index(":")
                    docstring[number] = "- " + lstrip_line[:colon_index + 1]

                    insert_text.append((number + 1,
                                        lstrip_line[colon_index + 2:]))

                if is_arguments_section and ":" in lstrip_line and "(" not in \
                        lstrip_line:
                    argument_name = ARGUMENT_REGEX.search(line).group(1)
                    docstring[number] = "- " + parsed_parameters[argument_name]

            elif line == "":  # End of the `Arguments` section.
                break

        if insert_text:
            for index, text in reversed(insert_text):
                docstring.insert(index, "    - " + text)

        return docstring

    def markdown_attributes_section(self, line_number: int,
                                    docstring: List[str]) -> List[str]:
        """
        Markdown the `Attributes:` section.

        The principle is almost the same as for the `Arguments:` section
        including arguments (see its documentation). The difference is that
        you have to write data types for each attribute yourself.
        """
        return self.markdown_arguments_section(line_number, docstring)

    @staticmethod
    def markdown_example_section(line_number: int, docstring: List[str]) \
            -> List[str]:
        """
        Markdown the `Example:` section.

        Warning:
            Don't use docstring headers like `Arguments:`, `Todo:` etc. at the
            start of line in the `Example:` section, otherwise Doksit will
            be broken.

        Arguments:
            line_number (int):
                Where the `Example` section starts.
            docstring (List[str]):
                Split docstring.

        Example: (markdown)
                Example:
                    print(True)

                    # Line after the break line.

            or

                Example: (markdown)
                    ...

            converts to:

                Example:

                ```python
                print(True)

                # Line after the break line.
                ```

            or

                Example:

                ```markdown
                ...
                ```

        Returns:
            Updated split docstring with the markdowned `Example` section.
        """
        example_header = docstring[line_number]

        if LANGUAGE_REGEX.search(example_header):
            language = LANGUAGE_REGEX.search(example_header).group(1)

            docstring[line_number] = "Example:"
        else:
            language = "python"

        for number, line in enumerate(docstring[line_number + 1:],
                                      start=line_number + 1):
            if line.startswith("     "):  # Indendation in the codes.
                docstring[number] = line[4:]

            elif line.startswith("    "):
                docstring[number] = line.lstrip(" ")

            elif line == "":  # End of the `Example` section or a line break.
                try:
                    if docstring[number + 1].startswith("    "):
                        continue
                    else:
                        example_end = number - 1
                        break
                except IndexError:
                    example_end = number - 1

        line_with_language = "\n```{language}".format(language=language)
        docstring.insert(line_number + 1, line_with_language)

        try:
            assert example_end
        except NameError:
            example_end = len(docstring)

        docstring.insert(example_end + 2, "```")  # New line was inserted.

        return docstring

    @staticmethod
    def markdown_note_section(line_number: int, docstring: List[str]) \
            -> List[str]:
        """
        Markdown the `Note:` section.

        Arguments:
            line_number (int):
                Where the `Note` section starts.
            docstring (List[str]):
                Split docstring.

        Example: (markdown)
                Note:
                    Note description.

            converts to:

                **Note:**
                    Note description.

        Returns:
            Updated split docstring with the markdowned `Note` section.
        """
        docstring[line_number] = "**" + docstring[line_number] + "**"

        return docstring

    @staticmethod
    def markdown_raises_section(line_number: int, docstring: List[str]) \
            -> List[str]:
        """
        Markdown the `Raises:` section.

        Arguments:
            line_number (int):
                Where the `Raises` section starts.
            docstring (List[str]):
                Split docstring.

        Example: (markdown)
                Raises:
                    AssertionError:
                        Reason.
                    ImportError:
                        Long reason.
                    KeyError: Reason.
                    TypeError: Long
                        reason.
                    ValueError:
                        1. reason
                        2. long
                           reason

            converts to:

                **Raises:**

                - AssertionError:
                    - Reason.
                - ImportError:
                    - Long
                      reason.
                - KeyError:
                    - Reason.
                - TypeError:
                    - Long
                      reason.
                - ValueError:
                    1. reason
                    2. long
                       reason

        Note:
            Be careful with numbered error descriptions (one error type may
            occur multiple times, eg. validation in the `__init__` method and
            not separately in setters), you may use it maximally 9x times, then
            a parser stops work.

        Returns:
            Updated split docstring with the markdowned `Raises` section.
        """
        docstring[line_number] = "**" + docstring[line_number] + "**\n"

        is_first_line_description = False
        insert_text = []  # For descriptions on the same line as error names.

        for number, line in enumerate(docstring[line_number + 1:],
                                      start=line_number + 1):
            if line.startswith(" " * 11):
                docstring[number] = " " * 7 + line.lstrip(" ")

            elif line.startswith(" " * 8):
                lstrip_line = line.lstrip(" ")

                if lstrip_line[0].isdigit() and lstrip_line[1] == ".":
                    docstring[number] = " " * 4 + lstrip_line
                else:
                    if is_first_line_description:
                        docstring[number] = "    - " + lstrip_line
                        is_first_line_description = False
                    else:
                        docstring[number] = " " * 6 + lstrip_line

            elif line.startswith(" " * 4):
                lstrip_line = line.lstrip(" ")

                if line.endswith(":"):
                    docstring[number] = "- " + lstrip_line
                    is_first_line_description = True  # For the next line.

                elif ":" in lstrip_line:
                    colon_index = lstrip_line.index(":")
                    docstring[number] = "- " + lstrip_line[:colon_index + 1]

                    insert_text.append((number + 1,
                                        lstrip_line[colon_index + 2:]))

            elif line.startswith(""):  # End of the `Raises` section.
                break

        if insert_text:
            for index, text in reversed(insert_text):
                docstring.insert(index, "    - " + text)

        return docstring

    def markdown_returns_section(self, line_number: int, docstring: List[str],
                                 object_name: Any) -> List[str]:
        """
        Markdown the `Returns:` section.

        Arguments:
            line_number (int):
                Where the `Returns` section starts.
            docstring (List[str]):
                Split docstring.
            object_name (Any)
                Function / method object for getting its return annotation.

        Example: (markdown)
                Returns:
                    Return description
                    over two lines.

            or

                Returns:
                    str:
                        Return description
                        over two lines.

            or

                Returns:
                    str: Return description
                    over two lines.

            converts to:

                **Returns:**

                - str:
                    - Return description
                      over two lines.

        Note:
            If an user didn't write the return annotation, then it will be
            automatically inserted.

        Returns:
            Updated split docstring with the markdowned `Returns` section.
        """
        docstring[line_number] = "**" + docstring[line_number] + "**\n"

        return_first_line = docstring[line_number + 1]  # Not `Return:` header.

        if return_first_line.endswith(":"):  # 2nd option from the docstring.
            docstring[line_number + 1] = "- " + return_first_line.lstrip(" ")
            docstring[line_number + 2] = \
                "    - " + docstring[line_number + 2].lstrip(" ")

            docstring = self._align_rest_return(docstring, line_number + 3)

        elif ":" in return_first_line:  # 3rd option from the docstring.
            colon_index = return_first_line.find(":")
            return_annotation = return_first_line[:colon_index + 1][4:]
            return_description = return_first_line[colon_index + 2:]
            docstring[line_number + 1] = "- " + return_annotation

            docstring = self._align_rest_return(docstring, line_number + 2)
            docstring.insert(line_number + 2, "    - " + return_description)

        else:  # 1st option from the docstring.
            docstring[line_number + 1] = \
                "    - " + return_first_line.lstrip(" ")
            docstring = self._align_rest_return(docstring, line_number + 2)

            return_annotation = self._parse_return_annotation(object_name)
            docstring.insert(line_number + 1, "- " + return_annotation + ":")

        return docstring

    @staticmethod
    def _align_rest_return(docstring: List[str], start: int) -> List[str]:
        """
        Arguments:
            docstring (List[str]):
                Original object docstring.
            start (int):
                Where the multine description starts.

        Returns:
            List[str]:
                Updated original docstring.
        """
        for line_number, line in enumerate(docstring[start:], start=start):
            if line == "":  # End of the `Returns:` section.
                break
            else:
                docstring[line_number] = " " * 6 + line.lstrip(" ")

        return docstring

    @staticmethod
    def markdown_todo_section(line_number: int, docstring: List[str]) \
            -> List[str]:
        """
        Markdown the `Todo:` section.

        Arguments:
            line_number (int):
                Where the `Todo` section starts.
            docstring (List[str]):
                Split docstring.

        Example: (markdown)
                Todo:
                    - first item
                    - second item
                      over two lines

            or

                Todo:
                    * first item
                    * second item
                      over two lines

            converts to:

                **Todo:**:

                - [ ] one item
                - [ ] two items
                      over two lines

        Returns:
            Updated split docstring with the markdowned `Todo` section.
        """
        docstring[line_number] = "**" + docstring[line_number] + "**\n"

        for number, line in enumerate(docstring[line_number + 1:],
                                      start=line_number + 1):
            if line.startswith("    -"):
                docstring[number] = line.replace("    -", "- [ ]")

            elif line.startswith("    *"):
                docstring[number] = line.replace("    *", "- [ ]")

            elif line.startswith(" " * 4):
                docstring[number] = " " * 6 + line.lstrip(" ")

            elif line == "":  # End of the `Todo` section.
                break

        return docstring

    def markdown_warning_section(self, line_number: int,
                                 docstring: List[str]) -> List[str]:
        """
        Markdown the `Warning:` section.

        The principle is the same as for the `Note:` section including
        arguments (see its documentation).
        """
        return self.markdown_note_section(line_number, docstring)

    def markdown_yields_section(self, line_number: int, docstring: List[str],
                                object_name: Any) -> List[str]:
        """
        Markdown the `Yields:` section.

        The principle is the same as for the `Returns:` section including
        arguments (see its documentation).
        """
        return self.markdown_returns_section(line_number, docstring,
                                             object_name)

    @staticmethod
    def _parse_parameters(object_name: Any) -> dict:
        """
        Parse parameters from the given function / method object to human
        readable format.

        Arguments:
            object_name:
                For which function / method to get its parameters.

        If an user doesn't use annotations, then is expected that he / she
        writes explicitly data types and default values for each parameter in
        the `Arguments:` section himself / herself and thus there is nothing to
        parse.

        Returns:
            Parameter names with its parsed variant or nothing (no annotation
            found).

        Example:
            {
                "foo": "foo (str):",
                "bar": "bar (float, optional)",  # Default is None.
                "baz": "baz (int, optional, default 1):"
            }
        """
        parameters = inspect.signature(object_name).parameters
        parsed_parameters = {}

        for parameter in parameters:
            if parameter not in ["self", "cls"]:
                to_parse = str(parameters[parameter])
                annotation, default_value = \
                    PARAMETER_REGEX.search(to_parse).groups()

                if annotation is None:
                    annotation = "None"

                if annotation.startswith("typing."):
                    # Annotation is for example `typing.List`, but this form
                    # user didn't write. He / she wrote eg. `List[str]`, which
                    # is internally in Python `typing.List<~T>[str]`.

                    bad_annotation = str(parameters[parameter].annotation)
                    annotation = bad_annotation.replace("typing.", "") \
                        .replace("<~T>", "")

                if to_parse.startswith("**"):  # Eg. **kwargs
                    parameter = "**" + parameter

                elif to_parse.startswith("*"):
                    parameter = "*" + parameter

                parsed_parameters[parameter] = "{parameter} ({annotation}" \
                    .format(parameter=parameter, annotation=annotation)

                if default_value:
                    if default_value == "None":
                        parsed_parameters[parameter] += ", optional"
                    else:
                        parsed_parameters[parameter] += \
                            ", optional, default {default_value}" \
                            .format(default_value=default_value)

                parsed_parameters[parameter] += "):"

        return parsed_parameters

    @staticmethod
    def _parse_return_annotation(object_name: Any) -> str:
        """
        Parse return annotation from the given function / method object to
        human readable format.

        Arguments:
            object_name (Any):
                For which function / method to get its return annotation.

        Returns:
            The parsed return annotation or nothing (no annotation found).

        Example:
            "List[str]"
        """
        return_annotation = \
            str(inspect.signature(object_name).return_annotation)

        if return_annotation == "<class 'inspect._empty'>":
            return "None"
        else:
            if BUILTIN_TYPE_REGEX.search(return_annotation):
                # Or defined own class like <class 'requests.models.Response'.

                return BUILTIN_TYPE_REGEX.search(return_annotation).group(1)

            elif return_annotation.startswith("typing."):
                return return_annotation.replace("typing.", "") \
                    .replace("<~T>", "")
