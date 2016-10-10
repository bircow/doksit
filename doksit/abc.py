"""
Here are defined abstract base classes.
"""

import abc
import inspect
import re
import subprocess

from typing import Any, List, Optional, Tuple

from doksit.data_types import MyOrderedDict

REPOSITORY_URL_REGEX = re.compile(r"origin\t([\S]+) ")
BRANCH_NAME_REGEX = re.compile(r"\* (.+)\n")

PARAMETER_REGEX = re.compile(r"[\w_]+:?([\w_\[\]\.]+)?=?(.+)?")

BUILTIN_TYPE_REGEX = re.compile(r"<class '([\w]+)'>")

CLASS_REGEX = re.compile(r"^class (\w+):?|\(")
METHOD_REGEX = re.compile(r"^    def ([\w_]+)\((self|cls)")
STATIC_METHOD_REGEX = re.compile(r"    def ([\w_]+)\(")
FUNCTION_REGEX = re.compile(r"^def ([\w_]+)")


class Base:
    """
    Base is the lowest class with predefined abtract methods and useful normal
    methods which may be used for writing other api documentation generator
    based on different docstring style than is Doksit / Google style.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_api_documentation(self):
        """
        Abstract `get_api_documentation` method which will return parsed
        API reference documentation in Markdown format.
        """
        pass

    @property
    def repository_url(self) -> Optional[str]:
        """
        GitHub repository URL if a user is using Git with GitHub, else
        nothing.

        Example:
            "https://github.com/nait-aul/doksit"
        """
        return self._get_repository_url()

    @property
    def current_branch(self) -> Optional[str]:
        """
        Name of current active branch name if a user is using Git, else
        nothing.

        Example:
            "master"
        """
        return self._get_current_branch()

    @property
    def repository_prefix(self) -> Optional[str]:
        """
        GitHub repository URL including suffix `/blob/<branch_name>/`.

        This attribute will be used as a prefix with a file path to create
        absolute URL to the given file to see its content.

        Example:
            "https://github.com/nait-aul/doksit/blob/master/"
        """
        if self.repository_url is not None and self.current_branch is not \
                None:
            return self.repository_url + "/blob/" + self.current_branch + "/"
        else:
            return None

    @staticmethod
    def _get_repository_url() -> Optional[str]:
        """
        Get an absolute URL path to a Github repository.

        If a user is not using Git & GitHub, then nothing will be raised
        and returned only `None` value.

        Returns:
            The absolute URL path to the GitHub repository or nothing.

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
            return repository_url[:-4]

        return repository_url

    @staticmethod
    def _get_current_branch() -> Optional[str]:
        """
        Get current active branch name.

        If a user is not using Git & GitHub, then nothing will be raised
        and returned will be only `None` value.

        Returns:
            The current active branch name or nothing.

        Example:
            "master"
        """
        try:
            current_branch = subprocess.check_output(
                ["git", "branch"], universal_newlines=True)
        except subprocess.CalledProcessError:
            return None

        return BRANCH_NAME_REGEX.search(current_branch).group(1)

    @staticmethod
    def _get_line_numbers(object_name: Any) -> str:
        """
        Find on which lines is the given object defined / located.

        Arguments:
            object_name:
                For which object (class, method, function) to get the line
                numbers.

        Note:
            There is a problem for defined CLI commands (functions) using a
            `click` package, because it will raise `TypeError. Therefore it
            will be silenced and returned only `#`.

        Returns:
            Range, where the object definition starts and ends or only `#` if
            the `TypeError` was raised.

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

        If this method is called for an object, then a suffix for GitHub line
        highlights will be added.

        Arguments:
            module:
                Module object.
            object_name:
                Class / method / function object.

        Returns:
            The absolute URL path or empty string if a user isn't using Git &
            GitHub.

        Example:
            "https://.../nait-aul/doksit/blob/master/doksit/api.py#L1-L10"
        """
        repository_prefix = self.repository_prefix

        if repository_prefix is not None:
            module_path = module.__name__.replace(".", "/") + ".py"
            url = "[source](" + str(repository_prefix) + module_path

            if object_name is not None:
                url += self._get_line_numbers(object_name)

            return url + ")\n\n"
        else:
            return ""

    @staticmethod
    def parse_parameters(object_name: Any) -> Optional[dict]:
        """
        Parse parameters from the given function / method object to human
        readable format.

        Arguments:
            object_name:
                For which function / method to get its parameters.

        If a user doesn't use annotations, then is expected that he / she
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

                if not annotation:
                    return None

                if annotation.startswith("typing."):
                    # Annotation is for example `typing.List`, but this form
                    # user didn't write. He / she wrote eg. `List[str]`, which
                    # is internally in Python `typing.List<~T>[str]`.

                    bad_annotation = str(parameters[parameter].annotation)

                    # 'typing.' may be found multiple times (eg. using
                    # combination of Union, Optional etc.)

                    annotation = bad_annotation.replace("typing.", "") \
                        .replace("<~T>", "")

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
    def parse_return_annotation(object_name: Any) -> Optional[str]:
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
            # No return annotation found.

            return None
        else:
            if BUILTIN_TYPE_REGEX.search(return_annotation):
                return BUILTIN_TYPE_REGEX.search(return_annotation).group(1)

            elif return_annotation.startswith("typing."):
                # 'typing.' may be found multiple times.

                return return_annotation.replace("typing.", "") \
                    .replace("<~T>", "")

            else:  # Eg. user defined class object.
                return return_annotation

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
