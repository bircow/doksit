"""
This module contains all the necessary functions for running the following
command:

    $ doksit api PACKAGE_DIRECTORY
"""

import importlib
import os
import re

from typing import Any, List, Tuple, Union

from doksit.utils.data_types import MyOrderedDict
from doksit.utils.inspectors import get_source_code_url
from doksit.utils.parsers import get_docstring


def find_files(package_path: str) -> List[str]:
    """
    Browse the given package directory and find all Python files.

    Note:
        Files in the `__pycache__` subdirectories are excluded. The same goes
        for the `__init__.py` and `__main__.py` files.

    Arguments:
        package_path:
            Relative path to the Python package directory.

    Returns:
        List of found Python files (their relative paths).

    Example:
        ["package/module.py", "package/subpackage/module.py"]
    """
    file_paths = []

    def get_file_paths(directory_path: str):
        """
        Get all Python files in the given directory and result appends to
        the nonlocal variable `file_paths`.

        Arguments:
            directory_path (str):
                Path to the given directory.
        """
        scanned_directory = os.scandir(directory_path)

        found_files = []
        found_subdirectories = []

        for entry in scanned_directory:
            if entry.is_dir() and entry.name != "__pycache__":
                found_subdirectories.append(entry.path)

            elif entry.is_file() and entry.name.endswith(".py") \
                    and entry.name not in ["__init__.py", "__main__.py"]:
                found_files.append(entry.path)

        nonlocal file_paths
        file_paths += sorted(found_files)

        for subdirectory in sorted(found_subdirectories):
            get_file_paths(subdirectory)

    get_file_paths(package_path)

    return file_paths


CLASS_REGEX = re.compile(r"^class (\w+):?|\(")
METHOD_REGEX = re.compile(r"^    def ([\w_]+)\((self|cls)")
STATIC_METHOD_REGEX = re.compile(r"    def ([\w_]+)\(")
FUNCTION_REGEX = re.compile(r"^def ([\w_]+)")


def read_file(file_path: str) -> Tuple[str, MyOrderedDict, List[str]]:
    """
    Find classes with methods and functions in the given file exactly in the
    order as they are defined.

    Note:
        Protected / prohibited methods / functions will be skipped. The same
        goes for magic methods except the `__init__`.

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
    absolute_path = os.getcwd() + "/" + file_path

    with open(absolute_path) as file:
        file_content = file.readlines()

    classes = MyOrderedDict()
    functions = []

    for line_number, line in enumerate(file_content):
        if line.startswith("class "):
            classes[CLASS_REGEX.search(line).group(1)] = []  # No methods yet

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


def _module_documentation(module: Any) -> str:
    """
    Get documentation for the given module.

    Arguments:
        module:
            Module object.

    Returns:
        The module documentation.

    Example: (markdown)
        ## package_name.module_name

        [source](https://github.com/nait-aul/doksit/blob/master/doksit/api.py)

        This is a module docstring.
    """
    module_name = module.__name__
    module_documentation = "## {module_name}\n\n" \
        .format(module_name=module_name)
    module_documentation += get_source_code_url(module)
    module_documentation += get_docstring(module)

    return module_documentation


def _classes_documentation(module: Any, classes: MyOrderedDict) -> str:
    """
    Get documentation for the given classes.

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

        classes_documentation += get_source_code_url(module, class_object)
        classes_documentation += get_docstring(class_object)

        for method_name in classes[class_name]:
            method_object = getattr(class_object, method_name)

            classes_documentation += \
                _method_documentation(module, method_object)

    return classes_documentation


def _method_documentation(module: Any, method: Any) -> str:
    """
    Get documentation for the given method.

    Arguments:
        module:
            Module object.
        method:
            Method object.

    Returns:
        The method documentation.

    Example: (markdown)
        #### method method_name

        [source](https://github.com/.../api.py#L4-L10)

        This is a method docstring.
    """
    method_name = method.__name__

    if method_name == "__init__":
        method_name = r"\_\_init\_\_"

    method_documentation = "\n\n#### method {method_name}\n\n" \
        .format(method_name=method_name)
    method_documentation += get_source_code_url(module, method)
    method_documentation += get_docstring(method)

    return method_documentation


def _functions_documentation(module: Any, functions: List[str]) \
        -> str:
    """
    Get documentation for the given functions.

    Arguments:
        module:
            Module object
        classes:
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

        functions_documentation += get_source_code_url(module, function_object)
        functions_documentation += get_docstring(function_object)

    return functions_documentation


def get_documentation(file_metadata: tuple) -> Union[str, None]:
    """
    Join all objects docstrings into one big documentation for the given file.

    If the file doesn't have any defined classes or functions, then no
    documentation will be created.

    Arguments:
        file_metadata:
            Returned data from the 'doksit.api.read_file' function.

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
        return

    module_path = file_path.replace("/", ".").rstrip(".py")
    imported_module = importlib.import_module(module_path)

    documentation = ""
    documentation += _module_documentation(imported_module)
    documentation += _classes_documentation(imported_module, classes)
    documentation += _functions_documentation(imported_module, functions)

    return documentation
