import inspect
import os
import re
import sys
from typing import List, Tuple

from doksit.utils import OrderedDict

file_paths = []


def find_files(directory_path: str) -> None:
    """
    Get relative paths for all python files in the given directory and
    subdirectories.

    Relative paths will be inserted into global variable 'file_paths'.

    Example:
        ["package/module.py", "package/subpackage/module.py"]

    Files in '__pycache__' directories are excluded. The same goes for
    '__init__.py' and '__main__.py'.

    Arguments:
        directory_path:
            Relative directory path.
    """
    for entry in os.scandir(directory_path):
        if entry.is_dir() and entry.name != "__pycache__":
            find_files(entry.path)
        elif entry.is_file() and entry.name.endswith(".py") \
                and entry.name not in ["__init__.py", "__main__.py"]:
            file_paths.append(entry.path)


class_regex = re.compile("^class (\w+):?|\(")
method_regex = re.compile("^    def ([\w_]+)\((self|cls)")
function_regex = re.compile("^def ([\w_]+)")


def read_file(file_path: str) -> Tuple[str, OrderedDict, List[str]]:
    """
    Get names for classes including methods inside and functions.

    Unlike Pydoc the Doksit cares about order of objects specified above in the
    given file + also omits magic methods except the '__init__'.

    Arguments:
        file_path:
            Relative file path.

    Returns:
        3-tuple, where first item is relative file path, second is ordered
        dict with class names and methods and third is list of function names.

    Example:
        ("package.module", OrderedDict({"Foo": ["__init__", "method_name"]),
        ["function_name"])
    """
    absolute_path = os.getcwd() + "/" + file_path

    classes = OrderedDict()
    functions = []

    with open(absolute_path) as f:
        file = f.readlines()

    for line in file:
        if line.startswith("class"):
            classes[class_regex.search(line).group(1)] = []

        if line.lstrip().startswith("def"):
            if method_regex.search(line):
                method_name = method_regex.search(line).group(1)

                if method_name == "__init__" or \
                        not method_name.startswith("_"):
                    classes[classes.last()].append(method_name)

            if function_regex.search(line):
                functions.append(function_regex.search(line).group(1))

    return file_path, classes, functions


output = "# API Rereference\n\n"


def get_documentation(file_metadata: tuple) -> None:
    """
    Create documentation for objects from the given file (module), if there
    are any.

    The documentation will be inserted into global variable 'output' which
    contains entire documentation for the given package.

    Arguments:
        file_metadata:
            Returned data from the 'read_file' function from 'doksit.main'.
    """
    file_path, classes, functions = file_metadata
    module = file_path.replace("/", ".").rstrip(".py")

    if not classes and not functions:
        return

    global output
    output += "## {}\n\n".format(module)

    if classes:
        for class_name in classes:
            exec("from {0} import {1} as cls".format(module, class_name))

            imported_class = locals()["cls"]
            class_docstring = inspect.getdoc(imported_class) or ""

            output += "### class {0}.{1}\n\n".format(module, class_name)
            output += class_docstring + "\n\n"

            for method_name in classes[class_name]:
                method_object = getattr(imported_class, method_name)
                method_docstring = inspect.getdoc(method_object)

                output += "#### .{}()\n\n".format(method_name)
                output += method_docstring + "\n\n"

    if functions:
        for function_name in functions:
            exec("from {0} import {1} as func".format(module, function_name))

            imported_function = locals()["func"]
            function_docstring = inspect.getdoc(imported_function) or ""

            output += "### function {0}.{1}\n\n".format(module, function_name)
            output += function_docstring + "\n\n"


def main() -> None:
    find_files(sys.argv[1])

    for file in reversed(file_paths):
        get_documentation(read_file(file))

    print(output[:-2])
