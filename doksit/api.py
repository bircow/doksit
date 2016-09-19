"""
This module contains all the necessary functions for running the following
command:

    $ doksit api PACKAGE_DIRECTORY
"""

import collections
import inspect
import os
import re

from typing import List

from doksit.utils.data_types import MyOrderedDict
from doksit.utils.inspectors import get_line_numbers
from doksit.utils.parsers import markdown_docstring

file_paths = []


def find_files(directory_path: str) -> List[str]:
    """
    Browse the given directory and find all python files (get their relative
    paths).

    Note:
        Files in the `__pycache__` directories are excluded. The same goes for
        the `__init__.py` and `__main__.py` files.

    Arguments:
        directory_path:
            Relative path to the Python package directory.

    Returns:
        List of found Python files (their relative paths).

    Example:
        ["package/module.py", "package/subpackage/module.py"]
    """
    scanned_directory = os.scandir(directory_path)

    # Entries in the 'scanned_directory' are unorered (mixed files and
    # directories), but I want to first loop over files and then over
    # directories.

    founded_files = []
    founded_subdirectories = []

    for entry in scanned_directory:
        if entry.is_dir() and entry.name != "__pycache__":
            founded_subdirectories.append(entry.path)

        elif entry.is_file() and entry.name.endswith(".py") \
                and entry.name not in ["__init__.py", "__main__.py"]:
            founded_files.append(entry.path)

    global file_paths
    file_paths += sorted(founded_files)

    for subdirectory in sorted(founded_subdirectories):
        find_files(subdirectory)

    return file_paths


class_regex = re.compile("^class (\w+):?|\(")
method_regex = re.compile("^    def ([\w_]+)\((self|cls)")
function_regex = re.compile("^def ([\w_]+)")


def read_file(file_path: str):
    """
    Find in the given file classes, their methods and functions exactly in the
    order as they are defined.

    Note:
        Protected / prohibited methods / functions will be skipped. The same
        goes for magic methods except the `__init__`.

    Arguments:
        file_path:
            Relative path to a Python file, eg. `directory/file.py`

    Returns:
        3-tuple, where first item is the relative file path, second is ordered
        dict with class names and their methods and third is list of function
        names.

    Example:
        (
            "package/module.py",
            MyOrderedDict([("Foo", ["__init__", "method_name"])]),
            ["function_name"]
        )
    """
    absolute_path = os.getcwd() + "/" + file_path

    with open(absolute_path) as f:
        file = f.readlines()

    classes = MyOrderedDict()
    functions = []

    for line in file:
        if line.startswith("class "):
            classes[class_regex.search(line).group(1)] = []  # No methods yet

        if line.lstrip().startswith("def "):
            if method_regex.search(line):
                method_name = method_regex.search(line).group(1)

                if method_name == "__init__" or \
                        not method_name.startswith("_"):
                    classes[classes.last()].append(method_name)

            elif function_regex.search(line):
                function_name = function_regex.search(line).group(1)

                if not function_name.startswith("_"):
                    functions.append(function_name)

    return file_path, classes, functions


def get_documentation(file_metadata: tuple):
    """
    Create markdowned documentation for the given Python file.

    If the file doesn't have any defined classes or functions, then no
    documentation will be created.

    Arguments:
        file_metadata:
            Returned data from the 'doksit.api.read_file' function.

    Returns:
        The markdowned documentation for the given file.

    Example: (markdown)
        ## package.module

        This is a markdowned module docstring.

        ### class class_name

        This is a markdowned class docstring.

        #### method method_name

        This is a markdowned method docstring.

        ### function function_name

        This is a markdowned function docstring.
    """
    file_path, classes, functions = file_metadata

    if not classes and not functions:
        return

    module_path = file_path.replace("/", ".").rstrip(".py")
    documentation = "## {module_path}\n\n".format(module_path=module_path)

    exec("import {module_path} as mdl".format(module_path=module_path))

    imported_module = locals()["mdl"]
    module_docstring = inspect.getdoc(imported_module) or ""

    if module_docstring:
        markdowned_docstring = markdown_docstring(module_docstring)
        documentation += markdowned_docstring + "\n\n"

    if classes:
        for class_name in classes:
            exec("from {module_path} import {class_name} as cls".format(
                module_path=module_path, class_name=class_name))

            imported_class = locals()["cls"]
            class_docstring = inspect.getdoc(imported_class) or ""
            class_location = get_line_numbers(imported_class)

            documentation += "### class {class_name}\n".format(
                class_name=class_name)
            documentation += "...{}\n\n".format(class_location)

            if class_docstring:
                markdowned_docstring = markdown_docstring(class_docstring)
                documentation += markdowned_docstring + "\n\n"

            for method_name in classes[class_name]:
                method_object = getattr(imported_class, method_name)
                method_docstring = inspect.getdoc(method_object) or ""
                method_parameters = inspect.signature(method_object).parameters
                method_parameters = collections.OrderedDict(method_parameters)
                method_location = get_line_numbers(method_object)

                if method_name == "__init__":
                    method_name = "\_\_init\_\_"

                documentation += "#### method {method_name}\n".format(
                    method_name=method_name)
                documentation += "...{}\n\n".format(method_location)

                if method_docstring:
                    if method_parameters:
                        markdowned_docstring = markdown_docstring(
                            method_docstring, method_parameters)
                    else:
                        markdowned_docstring = markdown_docstring(
                            method_docstring)

                    documentation += markdowned_docstring + "\n\n"

    if functions:
        for function_name in functions:
            exec("from {module_path} import {function_name} as func".format(
                module_path=module_path, function_name=function_name))

            imported_function = locals()["func"]
            function_docstring = inspect.getdoc(imported_function) or ""
            function_parameters = \
                inspect.signature(imported_function).parameters
            function_parameters = collections.OrderedDict(function_parameters)
            function_location = get_line_numbers(imported_function)

            documentation += "### function {function_name}\n".format(
                function_name=function_name)
            documentation += "...{}\n\n".format(function_location)

            if function_docstring:
                if function_parameters:
                    markdowned_docstring = markdown_docstring(
                        function_docstring, function_parameters)
                else:
                    markdowned_docstring = \
                        markdown_docstring(function_docstring)

                documentation += markdowned_docstring + "\n\n"

    return documentation
