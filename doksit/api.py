"""
This module contains all the necessary objects for running the following
command:

    $ doksit api PACKAGE_DIRECTORY
"""

import inspect
import importlib
import re

from typing import Any, List, Optional

from doksit.abc import Base
from doksit.data_types import MyOrderedDict

ARGUMENT_REGEX = re.compile(r"^    ([\w_\*]+)")
LANGUAGE_REGEX = re.compile(r"Example: \((\w+)\)")


class DoksitStyle(Base):
    """
    Description.
    """
    __slots__ = ("package_path", "title")

    def __init__(self, package_path: str, title: str) -> None:
        self.package_path = package_path
        self.title = title

    def get_api_documentation(self) -> str:
        """
        Todo
        """
        api_documentation = ["# " + self.title]
        file_paths = self.find_files(self.package_path)

        for file in file_paths:
            file_metadata = self.read_file(file)
            file_documentation = self._get_documentation(file_metadata)

            if file_documentation is not None:
                api_documentation.append(file_documentation)

        return "\n".join(api_documentation)

    def _get_documentation(self, file_metadata: tuple) -> Optional[str]:
        """
        Join all object (module, classes, method, functions) docstrings into
        one big documentation for the given file.

        If the file doesn't have any defined classes or functions, then no
        documentation will be created.

        Arguments:
            file_metadata:
                Returned data from the 'doksit.abc.Base.read_file' method.

        Returns:
            The documentation for the given file in Markdown format or nothing
            (the Python file is likely empty).

        Example: (markdown)
            ## package_name.module_name

            This is a markdowned module docstring.

            ### class class_name

            ([source](absolute_url_path_to_file_and_higlighted_code_block))

            This is a markdowned class docstring.

            #### method method_name

            ([source](...))

            This is a markdowned method docstring.

            ### function function_name

            ([source](...))

            This is a markdowned function docstring.
        """
        file_path, classes, functions = file_metadata

        if not classes and not functions:
            return None

        module_path = file_path.replace("/", ".").rstrip(".py")
        imported_module = importlib.import_module(module_path)

        documentation = ""
        documentation += self.get_module_documentation(imported_module)
        documentation += self.get_class_documentation(imported_module, classes)
        documentation += self.get_function_documentation(imported_module,
                                                         functions)

        return documentation

    def get_module_documentation(self, module: Any) -> str:
        """
        Get parsed module documentation for the given module.

        Arguments:
            module:
                Module object.

        Returns:
            The parsed module documentation.

        Example: (markdown)
            ## package_name.module_name

            [source](https://github.com/.../blob/master/doksit/api.py)

            This is a module docstring.
        """
        module_name = module.__name__
        module_documentation = "\n## {module_name}\n\n" \
            .format(module_name=module_name)
        module_documentation += self.get_source_code_url(module)
        module_documentation += self.get_markdowned_docstring(module)

        return module_documentation

    def get_class_documentation(self, module: Any, classes: MyOrderedDict) \
            -> str:
        """
        Get parsed class documentation for all the given classes.

        Arguments:
            module:
                Module object
            classes:
                Class names with method names.

        Returns:
            The classes documentation.

        Example: (markdown)
            ### class class_name_a

            [source](https://github.com/.../api.py#L1-L10)

            This is a class docstring.

            #### method method_name

            ...

            ### class class_name_b

            ...
        """
        classes_documentation = ""

        for class_name in classes:
            classes_documentation += "\n\n### class {class_name}\n\n" \
                .format(class_name=class_name)

            class_object = getattr(module, class_name)
            classes_documentation += \
                self.get_source_code_url(module, class_object)
            classes_documentation += \
                self.get_markdowned_docstring(class_object)

            for method_name in classes[class_name]:
                method_object = getattr(class_object, method_name)
                classes_documentation += \
                    self.get_method_documentation(module, method_object,
                                                  method_name)

        return classes_documentation

    def get_method_documentation(self,
                                 module: Any,
                                 method: Any,
                                 method_name: str) -> str:
        """
        Get parsed method documentation for the given method.

        Arguments:
            module:
                Module object.
            method:
                Method object.
            method_name:
                Namae of method.

        Note:
            It would be to easy to get a method name via
            `method_object.__name__`, but this option is not possible for
            propoerty method.

        Returns:
            The method documentation.

        Example: (markdown)
            #### method method_name

            [source](https://github.com/.../api.py#L4-L10)

            This is a method docstring.
        """
        if method_name == "__init__":
            method_name = r"\_\_init\_\_"

        method_documentation = "\n\n#### method {method_name}\n\n" \
            .format(method_name=method_name)
        method_documentation += self.get_source_code_url(module, method)
        method_documentation += self.get_markdowned_docstring(method)

        return method_documentation

    def get_function_documentation(self, module: Any, functions: List[str]) \
            -> str:
        """
        Get parsed function documentation for all the given functions.

        Arguments:
            module:
                Module object
            functions:
                List of function names.

        Returns:
            The classes documentation.

        Example: (markdown)
            ### function function_name_a

            [source](https://github.com/.../api.py#L12-L16)

            This is a function docstring.

            ### function function_name_b
        """
        functions_documentation = ""

        for function_name in functions:
            functions_documentation += "\n\n### function {function_name}\n\n" \
                .format(function_name=function_name)

            function_object = getattr(module, function_name)
            functions_documentation += \
                self.get_source_code_url(module, function_object)
            functions_documentation += \
                self.get_markdowned_docstring(function_object)

        return functions_documentation

    def get_markdowned_docstring(self, object_name: Any) -> str:
        """
        Get the object docstring and convert it to Markdown format.

        Arguments:
            object_name:
                For which object (module, class, method, function) to get its
                docstring.

        Returns:
            The markdowned docstring or empty string (the object
            doesn't have any docstring.)

        Example: (markdown)
            This is a brief object description.

            This is a long paragraph.

            **Arguments:**

            - foo (str):
                - Foo description.
            - bar (int, optional, default 1):
                - Bar description.

            **Returns:**

            - bool:
                - True if something.
        """
        docstring = inspect.getdoc(object_name)

        if not docstring:
            return ""

        split_docstring = docstring.split("\n")

        headers = {
            "Arguments:": self._markdown_arguments_section,
            "Attributes:": self._markdown_attributes_section,
            "Note:": self._markdown_note_section,
            "Raises:": self._markdown_raises_section,
            "Returns:": self._markdown_returns_section,
            "Todo:": self._markdown_todo_section,
            "Warning:": self._markdown_warning_section,
            "Yields:": self._markdown_yields_section
        }

        # Function for "Example:" header is handled separately, because
        # it may be also "Example: (markdown)".

        for line_number, line in enumerate(split_docstring):
            if line.startswith("Example:"):
                split_docstring = \
                    self._markdown_example_section(line_number,
                                                   split_docstring)

            elif line in ["Arguments:", "Returns:", "Yields:"]:
                split_docstring = headers[line](line_number, split_docstring,
                                                object_name)

            elif line in headers:
                split_docstring = headers[line](line_number, split_docstring)

        return "\n".join(split_docstring)

    @staticmethod
    def _bold_header(header: str) -> str:
        """
        Make the header bold and for some add a new line at the end of it.

        Arguments:
            header (str):
                Line in a docstring with a header.

        Example: (markdown)
            Arguments: -> **Arguments:**\n
            Note:      -> **Note:**

        Returns:
            str:
                Bold header with / without the new line at the end.
        """
        bold_header = "**" + header + "**"
        headers_with_new_line = (
            "Arguments:",
            "Attributes:",
            "Raises:",
            "Returns:",
            "Todo:",
            "Yields:"
        )

        # Headers without the new line at the end are:
        #
        # "Note:",
        # "Warning:"

        if header in headers_with_new_line:
            bold_header += "\n"

        return bold_header

    def _markdown_arguments_section(self,
                                    line_number: int,
                                    docstring: List[str],
                                    object_name: Any=None) -> List[str]:
        """
        Markdown the `Arguments` section.

        Arguments:
            line_number (int):
                Where the `Arguments` section starts.
            docstring (List[str]):
                Split docstring.
            object_name (Any)
                Function / method object for getting its parameters annotation.

        Example: (markdown)
                Arguments:
                    foo:
                        Argument description.
                    bar:
                        Argument description
                        over two lines.

                # or

                Arguments:
                    foo (int):
                        Argument description.
                    bar (str, optional, default "bar")
                        Argument description
                        over two lines.

            converts to:

                **Arguments:**

                - foo (int)
                    - Argument description.
                - bar (str, optional, default "bar")
                    - Argument description
                      over two lines.

        Note:
            If a user didn't write the parameter annotation, then it will be
            automatically inserted.

        Returns:
            List[str]:
                Updated split docstring with the markdowned `Arguments`
                section.
        """
        # Codes below will be shared with `_markdown_attributes_section`, but
        # some of them will be only for this function.

        arguments_header = docstring[line_number]
        docstring[line_number] = self._bold_header(arguments_header)

        arguments_content = docstring[(line_number + 1):]
        is_first_line_description = False
        is_arguments_section = True if object_name is not None else False

        if is_arguments_section:
            parsed_parameters = self.parse_parameters(object_name)

        for number, line in enumerate(arguments_content,
                                      start=line_number + 1):
            if line.startswith("        "):
                if is_first_line_description:
                    docstring[number] = line.replace("        ", "    - ")

                    is_first_line_description = False
                else:
                    docstring[number] = line.replace("        ", "      ")

            elif line.startswith("    "):
                if is_arguments_section and parsed_parameters is not None:
                    argument_name = ARGUMENT_REGEX.search(line).group(1)

                    if argument_name.startswith("*"):  # Eg, *args or **kwargs
                        argument_name = argument_name.lstrip("*")

                    docstring[number] = "- " + parsed_parameters[argument_name]
                else:
                    docstring[number] = line.replace("    ", "- ")

                # Next line should be an attribute description.

                is_first_line_description = True

            elif line == "":  # End of the `Arguments` section.
                break

        return docstring

    def _markdown_attributes_section(self,
                                     line_number: int,
                                     docstring: List[str]) -> List[str]:
        """
        Markdown the `Attributes` section.

        Arguments:
            line_number (int):
                Where the `Attributes` section starts.
            docstring (List[str]):
                Split docstring.

        Example: (markdown)
                Attributes:
                    foo (int):
                        Attribute description.
                    bar (str):
                        Attribute description
                        over two lines.

            converts to:

                **Attributes:**

                - foo (int):
                    - Attribute description.
                - bar (str):
                    - Attribute description
                      over two lines.

        Returns:
            List[str]:
                Updated split docstring with the markdowned `Attributes`
                section.
        """
        # Codes are same like for the `Arguments` section (apart from the ones
        # for `Arguments` section only).

        return self._markdown_arguments_section(line_number, docstring)

    @staticmethod
    def _markdown_example_section(line_number: int, docstring: List[str]) \
            -> List[str]:
        """
        Markdown the `Example` section.

        Arguments:
            line_number (int):
                Where the `Example` section starts.
            docstring (List[str]):
                Split docstring.

        Example: (markdown)
                Example:
                    print(True)

                    # Line after the beak line.

                # or

                Example: (markdown)
                    ...

            converts to:

                Example:

                ```python
                print(True)

                # Line after the break line.
                ```

                # or

                Example:

                ```markdown
                ...
                ```

        Returns:
            List[str]:
                Updated split docstring with the markdowned `Example` section.
        """
        example_header = docstring[line_number]

        if LANGUAGE_REGEX.search(example_header):
            language = LANGUAGE_REGEX.search(example_header).group(1)

            docstring[line_number] = "Example:"
        else:
            language = "python"

        example_content = docstring[(line_number + 1):]

        for number, line in enumerate(example_content, start=line_number + 1):
            if line.startswith("        "):  # A code indendation.
                docstring[number] = line[4:]

            elif line.startswith("    "):
                docstring[number] = line.lstrip(" ")

            elif line == "":
                # Attention, may be a line break also, not only end of the
                # `Example` section.

                if docstring[number + 1].startswith("    "):
                    continue
                else:
                    example_end = number - 1
                    break

        line_with_language = "\n```{language}".format(language=language)
        docstring.insert(line_number + 1, line_with_language)

        try:
            assert example_end
        except NameError:
            example_end = len(docstring)

        docstring.insert(example_end + 1, "```")

        # + 1 because new item was added.

        return docstring

    def _markdown_note_section(self, line_number: int, docstring: List[str]) \
            -> List[str]:
        """
        Markdown the `Note` section.

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
            List[str]:
                Updated split docstring with the markdowned `Note` section.
        """
        note_header = docstring[line_number]
        docstring[line_number] = self._bold_header(note_header)

        return docstring

    def _markdown_raises_section(self,
                                 line_number: int,
                                 docstring: List[str]) -> List[str]:
        """
        Markdown the `Raises` section.

        Arguments:
            line_number (int):
                Where the `Raises` section starts.
            docstring (List[str]):
                Split docstring.

        Example: (markdown)
                Raises:
                    AssertionError:
                        Reason.
                    TypeError:
                        Long
                        reason.
                    ValueError:
                        1. reason
                        2. long
                            reason

            converts to:

                **Raises:**

                - AssertionError:
                    - Reason.
                - TypeError:
                    - Long
                      reason.
                - ValueError:
                    1. reason
                    2. long
                       reason

        Returns:
            List[str]:
                Updated split docstring with the markdowned `Raises` section.
        """
        raises_header = docstring[line_number]
        docstring[line_number] = self._bold_header(raises_header)

        raises_content = docstring[(line_number + 1):]
        is_first_line_description = False

        for number, line in enumerate(raises_content, start=line_number + 1):
            if line.startswith("            "):
                docstring[number] = line.replace("            ", "       ")

            elif line.startswith("        "):
                # Attention, may be also ordered (numbered) error description.

                if line.lstrip(" ")[0].isdigit():
                    docstring[number] = line.replace("        ", "    ")

                    continue

                if is_first_line_description:
                    docstring[number] = line.replace("        ", "    - ")

                    is_first_line_description = False
                else:
                    docstring[number] = line.replace("        ", "      ")

            elif line.startswith("    "):
                docstring[number] = line.replace("    ", "- ")

                # Next line should be an error description.

                is_first_line_description = True

            elif line.startswith(""):  # End of the `Raises` section.
                break

        return docstring

    def _markdown_returns_section(self,
                                  line_number: int,
                                  docstring: List[str],
                                  object_name: Any) -> List[str]:
        """
        Markdown the `Returns` section.

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

                # or

                Returns:
                    str:
                        Return description
                        over two lines.

            converts to:

                **Returns:**

                - str:
                    - Return description
                      over two lines.

        Note:
            If a user didn't write the return annotation, then it will be
            automatically inserted.

        Returns:
            List[str]:
                Updated split docstring with the markdowned `Returns` section.
        """
        returns_header = docstring[line_number]
        docstring[line_number] = self._bold_header(returns_header)

        returns_start = line_number + 1

        if docstring[returns_start].endswith(":"):
            docstring[returns_start] = \
                docstring[returns_start].replace("    ", "- ")
            docstring[returns_start + 1] = \
                docstring[returns_start + 1].replace("        ", "    - ")

            returns_rest = docstring[(line_number + 3):]

            for number, line in enumerate(returns_rest, start=line_number + 3):
                if line == "":  # End of the `Returns` section
                    break
                else:
                    docstring[number] = line.replace("        ", "      ")

        else:
            docstring[returns_start] = \
                docstring[returns_start].replace("    ", "    - ")

            returns_rest = docstring[(line_number + 2):]

            for number, line in enumerate(returns_rest, start=line_number + 2):
                if line == "":  # End of the `Returns` section
                    break
                else:
                    docstring[number] = line.replace("    ", "      ")

            return_annotation = str(self.parse_return_annotation(object_name))
            docstring.insert(returns_start, "- " + return_annotation + ":")

        return docstring

    def _markdown_todo_section(self, line_number: int, docstring: List[str]) \
            -> List[str]:
        """
        Markdown the `Todo` section.

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

            converts to:

                **Todo:**:

                - [ ] one item
                - [ ] two items
                      over two lines

        Returns:
            List[str]:
                Updated split docstring with the markdowned `Todo` section.
        """
        todo_header = docstring[line_number]
        docstring[line_number] = self._bold_header(todo_header)

        todo_content = docstring[(line_number + 1):]

        for number, line in enumerate(todo_content, start=line_number + 1):
            if line.startswith("    -"):
                docstring[number] = line.replace("    -", "- [ ]")

            elif line.startswith("        "):
                docstring[number] = line.replace("        ", "      ")

            elif line == "":  # End of the `Todo` section.
                break

        return docstring

    def _markdown_warning_section(self,
                                  line_number: int,
                                  docstring: List[str]) -> List[str]:
        """
        Markdown the `Warning` section.

        Arguments:
            line_number (int):
                Where the `Warning` section starts.
            docstring (List[str]):
                Split docstring.

        Example: (markdown)
                Warning:
                    Warning description.

            converts to:

                **Warning:**
                    Warning description.

        Returns:
            List[str]:
                Updated split docstring with the markdowned `Warning` section.
        """
        warning_header = docstring[line_number]
        docstring[line_number] = self._bold_header(warning_header)

        return docstring

    def _markdown_yields_section(self,
                                 line_number: int,
                                 docstring: List[str],
                                 object_name: Any) -> List[str]:
        """
        Markdown the `Yields` section.

        Arguments:
            line_number (int):
                Where the `Yields` section starts.
            docstring (List[str]):
                Split docstring.
            object_name (Any)
                Function / method object for getting its yield annotation.

        Example: (markdown)
                Yields:
                    Yield description
                    over two lines.

                # or

                Yields:
                    int:
                        Yield description
                        over two lines.

            converts to:

                **Yields:**

                - int:
                    - Yield description.
                      over two lines.

        Note:
            If a user didn't write the return annotation, then it will be
            automatically inserted.

        Returns:
            List[str]:
                Updated split docstring with the markdowned `Yields` section.
        """
        # Codes are same like for the `Retuns` section, only header name is
        # different.

        return self._markdown_returns_section(line_number, docstring,
                                              object_name)
