"""
This module contains all the necessary objects for running the following
command:

    $ doksit api PACKAGE_DIRECTORY
"""

import inspect
import importlib
import sys

from typing import Any, List, Optional

from doksit.models import Base, DocstringParser
from doksit.data_types import MyOrderedDict


class DoksitStyle(Base, DocstringParser):
    """
    Main class for generating API documentation from docstrings written
    in Doksit style (Google + almost all Napoleon + Doksit layer).
    """
    __slots__ = ("package", "title")

    def __init__(self, package: str, title: str) -> None:
        """
        Initialize an instance of DoksitStyle class.

        Arguments:
            package:
                Name of Python package.
            title:
                Title for the API documentation output.
        """
        self.package = package
        self.title = title

    def get_api_documentation(self) -> str:
        """
        Get markdowned API documentation.
        """
        file_paths = self.find_files(self.package)

        if self.has_template:
            with open("docs/_api.md") as file:
                file_content = file.read()

            for file_number, file in enumerate(file_paths):
                file_metadata = self.read_file(file)
                file_documentation = self._get_documentation(file_metadata)

                if file_documentation is not None:
                    if file_number == 0:
                        file_documentation = file_documentation[1:]  # `\n`.

                    file_path = \
                        "{{ " + file.replace(self.package + "/", "", 1) + " }}"
                    file_content = \
                        file_content.replace(file_path, file_documentation)

            return file_content
        else:
            api_documentation = ["# " + self.title]

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

        try:
            imported_module = importlib.import_module(module_path)
        except ImportError:
            sys.path.append(".")
            imported_module = importlib.import_module(module_path)

        if self.alphabetically:
            classes = self._order_classes(imported_module, classes)
            functions = sorted(functions)

        documentation = ""
        documentation += self.get_module_documentation(imported_module)
        documentation += self.get_class_documentation(imported_module, classes)
        documentation += self.get_function_documentation(imported_module,
                                                         functions)

        return documentation

    @property
    def alphabetically(self) -> bool:
        """
        True, if objects and their docstring should be sorted in the API
        documentation alphabetically, otherwise False.
        """
        if self.config is not None:
            order = self.config.get("order", None)

            if order is not None:
                if order == "a-z" or order == "alphabetically":
                    return True

        return False

    @staticmethod
    def _order_classes(module: Any, classes: MyOrderedDict) -> MyOrderedDict:
        """
        Order alphabetically classes.

        About methods, they will be sorted in the following order:

        1. constructor
        2. properties
        3. methods
        """
        classes = MyOrderedDict(sorted(classes.items()))

        for class_name in classes:
            original_methods = classes[class_name]
            sorted_methods = []

            if "__init__" in original_methods:
                sorted_methods.append("__init__")
                original_methods.remove("__init__")

            class_object = getattr(module, class_name)
            properties = []
            methods = []

            for method_name in original_methods:
                method_object = getattr(class_object, method_name)

                if isinstance(method_object, property):
                    properties.append(method_name)
                else:
                    methods.append(method_name)

            if properties:
                sorted_methods += sorted(properties)

            if methods:
                sorted_methods += sorted(methods)

            classes[class_name] = sorted_methods

        return classes

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

    def get_method_documentation(self, module: Any, method: Any,
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
            method_documentation = "\n\n#### constructor\n\n"

        elif isinstance(method, property):
            method_documentation = "\n\n#### property {method_name}\n\n" \
                .format(method_name=method_name)

        else:
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
            "Args:": self.markdown_arguments_section,
            "Arguments:": self.markdown_arguments_section,
            "Attributes:": self.markdown_attributes_section,
            "Note:": self.markdown_note_section,
            "Raises:": self.markdown_raises_section,
            "Returns:": self.markdown_returns_section,
            "Todo:": self.markdown_todo_section,
            "Warning:": self.markdown_warning_section,
            "Yields:": self.markdown_yields_section
        }

        # Method for "Example:" header is handled separately, because
        # it may be also "Example: (markdown)".

        for line_number, line in enumerate(split_docstring):
            if line.startswith("Example:"):
                split_docstring = \
                    self.markdown_example_section(line_number,
                                                  split_docstring)

            elif line in ["Args:", "Arguments:", "Returns:", "Yields:"]:
                split_docstring = headers[line](line_number, split_docstring,
                                                object_name)

            elif line in headers:
                split_docstring = headers[line](line_number, split_docstring)

        return "\n".join(split_docstring)
