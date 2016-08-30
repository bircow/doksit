import os
import re
import sys
from typing import List, Tuple

from doksit.utils import OrderedDict

class_regex = re.compile("^class (\w+):?|\(")
method_regex = re.compile("^    def ([\w_]+)")
function_regex = re.compile("^def ([\w_]+)")


def read_file(file_path: str) -> Tuple[OrderedDict, List[str]]:
    """Get names for classes including methods inside and functions.

    Unlike Pydoc the Doksit cares about order of objects specified above in the
    given file + omits magic methods except the '__init__'.

    Arguments:
        file_path:
            Relative file path.

    Returns:
        First item contains ordered dict with class names (key) and its
        methods (value). Second items contains function names.
    """
    path = os.getcwd() + "/" + file_path

    classes = OrderedDict()
    functions = []

    with open(path) as f:
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

    return classes, functions


file_paths = []


def find_files(directory_path: str) -> None:
    """Get relative paths for all python files in the given directory and
    subdirectories.

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


def main():
    find_files(sys.argv[1])

    for file in reversed(file_paths):
        read_file(file)
