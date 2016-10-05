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
from doksit.utils.parsers import get_markdowned_docstring


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
    ignored_files = ["__init__.py", "__main__.py"]

    for root, _, files in os.walk(package_path):
        if os.path.basename(root) != "__pycache__":
            for file in files:
                if file.endswith(".py") and file not in ignored_files:
                    file_paths.append(os.path.join(root, file))

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
    module_documentation = "\n## {module_name}\n\n" \
        .format(module_name=module_name)
    module_documentation += get_source_code_url(module)
    module_documentation += get_markdowned_docstring(module)

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
        classes_documentation += get_markdowned_docstring(class_object)

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
    method_documentation += get_markdowned_docstring(method)

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
        functions_documentation += get_markdowned_docstring(function_object)

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


HEADINGS = (
    "## ",
    "### class ",
    "#### method ",
    "### function "
)

START = "\x1b["
END = "\x1b[K\x1b[0m"


def _color_heading(line: str) -> str:
    """
    Color the given Markdown heading.

    Arguments:
        line:
            Line with a heading.

    Legend of used ANSI escape sequences:

    - 34;40;1m
        - bold blue foreground, black background
    - 32;40;1m
        - bold green foreground, black background
    - 33;40;1m
        - bold yellow foreground, black background
    - 36;40;1m
        - bold cyan foreground, black background

    Returns:
        The colored heading.

    Example:
        "\x1b[34;40;1m## doksit.api\x1b[K\x1b[0m"
    """
    if line.startswith(HEADINGS[0]):
        return START + "34;40;1m" + line + END

    elif line.startswith(HEADINGS[1]):
        return START + "32;40;1m" + line + END

    elif line.startswith(HEADINGS[2]):
        return START + "33;40;1m" + line + END

    elif line.startswith(HEADINGS[3]):
        return START + "36;40;1m" + line + END


BOLD_HEADERS = (
    "**Arguments:**",
    "**Attributes:**",
    "**Note:**",
    "**Raises:**",
    "**Returns:**",
    "**Todo:**",
    "**Warning:**",
    "**Yields:**"
)


def _color_header(line: str) -> str:
    """
    Color the giving header.

    Arguments:
        line:
            Line with a header.

    Legend of used ANSI escape sequences:

    - 31;40;1m
        - bold red foreground, black background (only for the `Warning`
          header)
    - \x1b[21m\x1b[97m
        - deactivate bold foreground and change foreground color to white
    - 97;40;1m
        - bold white foreground, black background
    - \x1b[21m
        - deactivate bold foreground

    Returns:
        The colored header.

    Example:
        "\x1b[31;40;1mWarning:\x1b[21\x1b[97m\x1b[K"
    """
    line = line.strip("*")

    if line in ["Warning:"]:
        return START + "31;40;1m" + line + END
    else:
        return START + "97;40;1m" + line + END


def _color_module_documentation(documentation: str) -> str:
    """
    Color the given module documentation.

    Arguments:
        documentation:
            Module documentation.

    Note:
        What exactly will be colored is mentioned below in the
        `color_documentation` function.

    Legend of used ANSI escape sequences:

    - 30;107m
        - black foreground, white background
    - 97;40m
        - white foreground, black background

    Returns:
        The colored module documentation.
    """
    split_documentation = documentation.split("\n")
    is_example_section = False

    for line_number, line in enumerate(split_documentation):
        if line.startswith(HEADINGS) and not is_example_section:
            split_documentation[line_number] = _color_heading(line)

        elif line in BOLD_HEADERS and not is_example_section:
            split_documentation[line_number] = _color_header(line)

        elif line.startswith("```"):
            if is_example_section:
                is_example_section = False
            else:
                is_example_section = True

            split_documentation[line_number] = START + "30;107m" + line + END

        elif line == "":
            if is_example_section:
                split_documentation[line_number] = START + "30;107m" + END
            else:
                split_documentation[line_number] = START + "97;40m" + END
        else:
            if is_example_section:
                split_documentation[line_number] = \
                    START + "30;107m" + line + END
            else:
                split_documentation[line_number] = \
                    START + "97;40m" + line + END

    return "\n".join(split_documentation)


def color_documentation(documentation: List[str]) -> str:
    """
    Color some text patterns in the given API Reference documentation.

    Arguments:
        documentation:
            Generated API Reference documentation.

    List of text patterns to be colored:

    | Pattern | Foreground color | Background | Bold |
    | --- | --- | --- | --- |
    | title | red | black | yes |
    | modules | blue | black | yes |
    | classes | green | black | yes |
    | methods | yellow | black | yes |
    | functions | cyan | black | yes |
    | bold headers | white | black | yes |
    | warning header | red | black | yes |
    | codes | black | white | no |
    | rest of documentation | white | black | no |

    Returns:
        The colorful documentation.

    Example:
        # Here is a variant in list: (will be joined)

        [
            "<ansi_escape># API Reference<ansi_escape>",
            "",
            "<ansi_escape>## doksit.api<ansi_escape>",
            "..."
        ]
    """
    documentation[0] = START + "31;40;1m" + documentation[0] + END
    modules_documentation = documentation[1:]

    for index, module in enumerate(modules_documentation, start=1):
        documentation[index] = _color_module_documentation(module)

    return "\n".join(documentation[:])
