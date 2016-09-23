"""
This module contains all the necessary functions for running the following
command:

    $ doksit api PACKAGE_DIRECTORY
"""

import collections
import importlib
import inspect
import os
import re

from typing import Any

from doksit.utils.data_types import MyOrderedDict
from doksit.utils.inspectors import get_line_numbers, get_repository_url
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

    for line in file_content:
        if line.startswith("class "):
            classes[CLASS_REGEX.search(line).group(1)] = []  # No methods yet

        if line.lstrip().startswith("def "):
            if METHOD_REGEX.search(line):
                method_name = METHOD_REGEX.search(line).group(1)

                if method_name == "__init__" or \
                        not method_name.startswith("_"):
                    classes[classes.last()].append(method_name)

            elif FUNCTION_REGEX.search(line):
                function_name = FUNCTION_REGEX.search(line).group(1)

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

    repository_url = get_repository_url()

    def insert_source_url(is_module: bool=False, object_name: Any=None):
        """
        Insert into documentation below each objects their link to source code.

        This works only for those who are using Git and GitHub, otherwise
        a blank line will be inserted.

        Arguments:
            is_module (bool, optional, default False):
                Whether the source link will be for module only or for objects
                inside it.
            object_name (Any, optional, default None):
                Reference to an object.

        Example: (markdown)
            ([source](https://github.com/.../blob/master/doksit/api.py))

            # or for objects (will be highlighted)

            ([source](.../api.py#L1-L10))
        """
        nonlocal documentation
        nonlocal file_path
        nonlocal repository_url

        if repository_url:
            source_url = "([source]({repository_url}{file_path}{lines}))\n\n"

            if is_module:
                documentation += source_url.format(**locals(), lines="")
            else:
                documentation += source_url.format(
                    **locals(), lines=get_line_numbers(object_name))
        else:
            documentation += "\n"

    insert_source_url(is_module=True)

    imported_module = importlib.import_module(module_path)
    module_docstring = inspect.getdoc(imported_module) or ""

    if module_docstring:
        documentation += markdown_docstring(module_docstring) + "\n\n"

    for class_name in classes:
        documentation += "### class {class_name}\n".format(**locals())

        imported_class = getattr(imported_module, class_name)

        insert_source_url(object_name=imported_class)

        class_docstring = inspect.getdoc(imported_class) or ""

        if class_docstring:
            documentation += markdown_docstring(class_docstring) + "\n\n"

        for method_name in classes[class_name]:
            method_object = getattr(imported_class, method_name)

            if method_name == "__init__":
                method_name = r"\_\_init\_\_"

            documentation += "#### method {method_name}\n".format(
                **locals())

            insert_source_url(object_name=method_object)

            method_docstring = inspect.getdoc(method_object) or ""
            method_parameters = collections.OrderedDict(
                inspect.signature(method_object).parameters)

            if method_docstring:
                documentation += markdown_docstring(
                    method_docstring, method_parameters) + "\n\n"

    for function_name in functions:
        documentation += "### function {function_name}\n".format(
            **locals())

        imported_function = getattr(imported_module, function_name)

        insert_source_url(object_name=imported_function)

        function_docstring = inspect.getdoc(imported_function) or ""
        function_parameters = collections.OrderedDict(
            inspect.signature(imported_function).parameters)

        if function_docstring:
            documentation += markdown_docstring(
                function_docstring, function_parameters) + "\n\n"

    return documentation
