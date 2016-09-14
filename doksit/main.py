import collections
import inspect
import os
import re
from typing import List, Tuple

from doksit.cli import parser as cli_parser
from doksit.utils.data_types import MyOrderedDict
from doksit.utils.parsers import markdown_docstring

file_paths = []


def find_files(directory_path: str) -> None:
    """
    Get ordered relative paths for all python files in the given directory and
    subdirectories.

    These relative paths will be inserted into global variable 'file_paths'.

    Example:
        ["package/module.py", "package/subpackage/module.py"]

    Files in '\_\_pycache\_\_' directories are excluded. The same goes for
    '\_\_init__.py' and '\_\_main\_\_.py' files.

    Arguments:
        directory_path:
            Relative directory path.
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


class_regex = re.compile("^class (\w+):?|\(")
method_regex = re.compile("^    def ([\w_]+)\((self|cls)")
function_regex = re.compile("^def ([\w_]+)")


def read_file(file_path: str) -> Tuple[str, MyOrderedDict, List[str]]:
    """
    Get names for classes and methods inside and functions if there are any.

    Unlike Pydoc the Doksit cares about order of objects specified above in the
    given file + omits magic methods except the '\_\_init\_\_'.

    Arguments:
        file_path:
            Relative file path.

    Returns:
        3-tuple, where first item is relative file path, second is ordered
        dict with class names and methods and third is list of function names.

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
            classes[class_regex.search(line).group(1)] = []

        if line.lstrip().startswith("def "):
            if method_regex.search(line):
                method_name = method_regex.search(line).group(1)

                if method_name == "__init__" or \
                        not method_name.startswith("_"):
                    classes[classes.last()].append(method_name)

            elif function_regex.search(line):
                function_name = function_regex.search(line).group(1)

                if not function_name.startswith("_"):
                    functions.append(function_regex.search(line).group(1))

    return file_path, classes, functions


output = "# API Reference\n\n"


def get_documentation(file_metadata: tuple) -> str:
    """
    Create documentation for objects from the given file (module), if there
    are any.

    In other words, if the file is empty then documentation won't be created
    for it.

    The documentation will be inserted into global variable 'output' which
    contains entire documentation for the given package.

    Arguments:
        file_metadata:
            Returned data from the 'read_file' function from the 'doksit.main'.

    Returns:
        Updated global variable 'output'. It's needed for successful
        unittest of this function.
    """
    file_path, classes, functions = file_metadata
    module_name = file_path.replace("/", ".").rstrip(".py")

    if not classes and not functions:
        return

    global output
    output += "## {}\n\n".format(module_name)

    exec("import {} as mdl".format(module_name))

    imported_module = locals()["mdl"]
    module_docstring = inspect.getdoc(imported_module) or ""

    if module_docstring:
        markdowned_docstring = markdown_docstring(module_docstring)

        output += markdowned_docstring + "\n\n"

    if classes:
        for class_name in classes:
            exec("from {0} import {1} as cls".format(module_name, class_name))

            imported_class = locals()["cls"]
            class_docstring = inspect.getdoc(imported_class) or ""

            output += "### class {}\n\n".format(class_name)

            if class_docstring:
                markdowned_docstring = markdown_docstring(class_docstring)

                output += markdowned_docstring + "\n\n"

            for method_name in classes[class_name]:
                method_object = getattr(imported_class, method_name)
                method_docstring = inspect.getdoc(method_object) or ""
                method_parameters = inspect.signature(method_object).parameters
                method_parameters = collections.OrderedDict(method_parameters)

                if method_name == "__init__":
                    method_name = "\_\_init\_\_"

                output += "#### method {}\n\n".format(method_name)

                if method_docstring:
                    if method_parameters:
                        markdowned_docstring = markdown_docstring(
                            method_docstring, method_parameters)
                    else:
                        markdowned_docstring = markdown_docstring(
                            method_docstring)

                    output += markdowned_docstring + "\n\n"

    if functions:
        for function_name in functions:
            exec("from {0} import {1} as func".format(
                module_name, function_name))

            imported_function = locals()["func"]
            function_docstring = inspect.getdoc(imported_function) or ""
            function_parameters = \
                inspect.signature(imported_function).parameters
            function_parameters = collections.OrderedDict(function_parameters)

            output += "### function {}\n\n".format(function_name)

            if function_docstring:
                if function_parameters:
                    markdowned_docstring = markdown_docstring(
                        function_docstring, function_parameters)
                else:
                    markdowned_docstring = \
                        markdown_docstring(function_docstring)

                output += markdowned_docstring + "\n\n"

    return output


def main() -> None:
    """
    Create documentation for the given Python package and print it.
    """
    package = cli_parser.parse_args()

    find_files(package.directory)

    for file in file_paths:
        get_documentation(read_file(file))

    print(output[:-2])  # Last line is '\n\n'.
