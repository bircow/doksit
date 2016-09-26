"""
This module contains all the necessary functions for running the following
command:

    $ doksit api PACKAGE_DIRECTORY
"""

import importlib
import inspect
import os
import re

from typing import Any

from doksit.utils.data_types import MyOrderedDict
from doksit.utils.inspectors import get_line_numbers
from doksit.utils.parsers import markdown_docstring


def find_files(package_path: str):
    """
    Browse the given package directory and find all Python files (get their
    relative paths).

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
        Get all Python files in the given directory / subdirectory and result
        appends to nonlocal variable `file_paths`.

        Arguments:
            directory_path (str):
                Path to the given directory / subdirectory.
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


def get_documentation(file_metadata: tuple, repository_url: str=None):
    """
    Create markdowned documentation for the given Python file.

    If the file doesn't have any defined classes or functions, then no
    documentation will be created.

    Arguments:
        file_metadata:
            Returned data from the 'doksit.api.read_file' function.
        repository_url:
            Absolute path to the GitHub repository (prefix).

    Returns:
        The markdowned documentation for the given file or None (there is
        nothing to markdown).

    Example: (markdown)
        ## package.module

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
    documentation = "## {module_path}\n\n".format(**locals())

    def insert_source_url(object_name: Any=None, is_module: bool=False):
        """
        Insert into documentation below each objects their link to source code.

        This works only for those who are using Git and GitHub, otherwise
        a blank line will be inserted.

        Arguments:
            object_name (Any, optional, default None):
                Reference to an object (for getting the object location).
            is_module (bool, optional, default False):
                Whether the source link will be for module only or for objects
                inside it.

        Example: (markdown)
            ([source](https://github.com/.../blob/master/doksit/api.py))

            # or for classes / methods / functions (codes will be highlighted)

            ([source](.../api.py#L1-L10))
        """
        nonlocal documentation

        if repository_url:
            nonlocal file_path
            source_url = "([source]({repository_url}{file_path}{lines}))\n\n"

            if is_module:
                documentation += source_url.format(**locals(), lines="")
            else:
                documentation += source_url.format(
                    **locals(), lines=get_line_numbers(object_name))
        else:
            documentation += "\n"

    def insert_object_documentation(object_name: Any, is_function=False,
                                    is_module=False):
        """
        Insert into documentation a docstring for the given object + its
        link to source code.

        Arguments:
            object_name (Any):
                For which object to get its docstring.
            is_function (bool, optional, default False):
                Whether the object is a function or method.
            is_module (bool, optional, default False)

        """
        if is_module:
            insert_source_url(object_name, is_module=True)
        else:
            insert_source_url(object_name)

        object_docstring = inspect.getdoc(object_name) or ""
        nonlocal documentation

        if object_docstring:
            if not is_function:
                documentation += markdown_docstring(object_docstring) + "\n\n"
            else:
                documentation += markdown_docstring(
                    object_docstring, object_name) + "\n\n"

    imported_module = importlib.import_module(module_path)
    insert_object_documentation(imported_module, is_module=True)

    for class_name in classes:
        documentation += "### class {class_name}\n".format(**locals())

        imported_class = getattr(imported_module, class_name)
        insert_object_documentation(imported_class)

        for method_name in classes[class_name]:
            method_object = getattr(imported_class, method_name)

            if method_name == "__init__":
                method_name = r"\_\_init\_\_"

            documentation += "#### method {method_name}\n".format(
                **locals())
            insert_object_documentation(method_object, is_function=True)

    for function_name in functions:
        documentation += "### function {function_name}\n".format(
            **locals())

        imported_function = getattr(imported_module, function_name)
        insert_object_documentation(imported_function, is_function=True)

    return documentation
