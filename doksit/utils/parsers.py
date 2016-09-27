"""
Here are defined parsers.
"""

import inspect
import re

from typing import Any, Union

PARAMETER_REGEX = re.compile(r"[\w_]+:?([\w_\[\]\.]+)?=?(.+)?")


def parse_parameters(object_name: Any) -> Union[dict, None]:
    """
    Parse the given parameters from a function / method to human readable
    format.

    Arguments:
        object_name:
            For which object (function / method) to get its parameters.

    If a user doesn't use annotations, then is expected that he / she writes
    explicitly data types and default values for parameters in the `Arguments:`
    section himself / herself and thus there is nothing to parse.

    Returns:
        Parameter names with its parsed variant or nothing (no annotation
        found).

    Example:
        {"foo": "foo (str):", "bar": "bar (int, optional, default 0):"}
    """
    parameters = inspect.signature(object_name).parameters
    output = {}

    for parameter in parameters:
        if parameter in ["self", "cls"]:
            continue
        else:
            to_parse = str(parameters[parameter])
            annotation, default_value = \
                PARAMETER_REGEX.search(to_parse).groups()

            if not annotation:
                return

            elif annotation.startswith("typing."):
                # Annotation is for example `typing.List`, but this form
                # user didn't write. He / she wrote eg. `List[str]`, which is
                # internally in Python `typing.List<~T>[str]`.

                bad_annotation = str(parameters[parameter].annotation)

                # 'typing.' may be found multiple times.

                annotation = bad_annotation.replace("typing.", "").replace(
                    "<~T>", "")

            output[parameter] = "{parameter} ({annotation}".format(
                parameter=parameter, annotation=annotation)

            if default_value:
                if default_value == "None":
                    output[parameter] += ", optional"
                else:
                    output[parameter] += ", optional, default " \
                        "{default_value}".format(default_value=default_value)

            output[parameter] = output[parameter] + "):"

    return output


BUILTIN_TYPE_REGEX = re.compile(r"<class '([\w]+)'>")


def parse_return_annotation(object_name: Any) -> Union[str, None]:
    """
    Parse the return annotation of a function / method to human readable
    format.

    Arguments:
        object_name (Any):
            For which object (function / method) to get its return annotation.

    Returns:
        The parsed return annotation or nothing (no annotation found).

    Example:
        "List[str]"
    """
    return_annotation = str(inspect.signature(object_name).return_annotation)

    if return_annotation == "<class 'inspect._empty'>":  # No annotation found.
        return
    else:
        if BUILTIN_TYPE_REGEX.search(return_annotation):
            return BUILTIN_TYPE_REGEX.search(return_annotation).group(1)

        elif return_annotation.startswith("typing."):
            # 'typing.' may be found multiple times.

            return return_annotation.replace("typing.", "").replace("<~T>", "")

        else:
            return return_annotation


ARGUMENT_REGEX = re.compile(r"^    ([\w_\*]+)")
LANGUAGE_REGEX = re.compile(r"Example: \((\w+)\)")


def markdown_docstring(object_name: Any) -> Union[str, None]:
    """
    Get the object docstring and convert it to Markdown format.

    Arguments:
        object_name:
            For which object to get its docstring.

    Returns:
        Docstring in the Markdown format or nothing (object doesn't have
        docstring.)

    Example:
        This is a brief object description.

        This is a long paragraph.

        **Arguments**:

        - foo (str):
            - Foo description.
        - bar (int, optional, default 1):
            - Bar description.

        **Returns:**

        - bool:
            - True if something.
    """
    docstring = inspect.getdoc(object_name) or ""

    if not docstring:
        return
    else:
        splited_docstring = docstring.split("\n")

    def bold_header(line_number: int, line: str):
        """
        Make the found header bold and for some add new line at the end.

        Arguments:
            line_number (int):
                Current line number (index) of outer variable
                `splited_docstring`.
            line (str):
                Content at the given line number.

        Example: (markdown)
            Note: -> **Note:**

        List of supported headers for bolding:

        - Arguments
        - Attributes
        - Note
        - Raises
        - Returns
        - Todo
        - Warning
        - Yields

        Exception:

        - Example
        """
        nonlocal splited_docstring

        headers_with_new_line = [
            "Arguments:",
            "Attributes:",
            "Raises:",
            "Returns:",
            "Todo:",
            "Yields:"
        ]

        if line in headers_with_new_line:
            splited_docstring[line_number] = "**" + line + "**\n"
        else:
            splited_docstring[line_number] = "**" + line + "**"

    def markdown_description_sections(line_number, line):
        """
        Markdown the `Arguments:` or the `Attributes` or the `Raises` section.

        Note:
            They share very similar codes for markdowning, therefore they are
            handled in the same function.

        Example: (markdown)
                Arguments:
                    foo:
                        Argument description.
                    bar:
                        Argument description
                        over two lines.

            converts to:

                **Arguments:**:

                - foo (str):
                    - Argument description.
                - bar (int, optional, default 10):
                    - Argument description
                over two lines.

            ---

                Attributes:
                    attribute_name (type):
                        Attribute description.
                    another_one (type):
                        Long attribute description
                        over two lines.

            converts to:

                **Attributes:**:

                - attribute_name (type):
                    - Attribute description.
                - another_one (type):
                    - Long attribute description
                over two lines.

            ---

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
        """
        bold_header(line_number, line)

        nonlocal splited_docstring
        section = splited_docstring[(line_number + 1):]
        lines = 0
        is_first_line_description = False
        is_arguments_section = line if line == "Arguments:" else False

        if is_arguments_section:
            parsed_parameters = parse_parameters(object_name)

        for row in section:
            if row == "":  # End of `Arguments / Attributes / Raises` section.
                break

            elif row.startswith("            "):  # Only the `Raises` section.
                lines += 1
                splited_docstring[line_number + lines] = row.lstrip(" ")

            elif row.startswith("        "):
                lines += 1

                # In the 'Raises' section may be the first character after
                # spaces a number. If so, there is no need to add a bullet
                # point.

                try:
                    assert line == "Raises:"
                    int(row.lstrip(" ")[0])

                    splited_docstring[line_number + lines] = \
                        "    " + row.lstrip(" ")
                    continue
                except (AssertionError, ValueError):
                    pass

                if is_first_line_description:
                    splited_docstring[line_number + lines] = \
                        "    - " + row.lstrip(" ")

                    is_first_line_description = False
                else:
                    splited_docstring[line_number + lines] = \
                        row.lstrip(" ")

            elif row.startswith("    "):
                lines += 1

                if is_arguments_section and parsed_parameters:
                    argument_name = \
                        ARGUMENT_REGEX.search(row).group(1)

                    if argument_name.startswith("*"):  # Eg. *args or **kwargs
                        argument_name = argument_name.lstrip("*")

                    splited_docstring[line_number + lines] = \
                        "- " + parsed_parameters[argument_name]

                else:
                    splited_docstring[line_number + lines] = \
                        "- " + row.lstrip(" ")

                # Next row should be an attribute / argument / error
                # description.

                is_first_line_description = True

    def markdown_example(line_number):
        """
        Markdown the `Example:` section.

        Example:
                Example:
                    print(True)

                    # Line after break line

            converts to:

                Example:

                ```python
                print(True)

                # Line after break line
                ```

        User may also define different language, like:

            Example: (markdown)

        Then it will be automatically rewritten to:

            Example:

            ```markdown
        """
        nonlocal splited_docstring
        example_line = splited_docstring[line_number]

        if LANGUAGE_REGEX.search(example_line):
            language = LANGUAGE_REGEX.search(example_line).group(1)

            splited_docstring[line_number] = "Example:"
        else:
            language = "python"

        example_section = splited_docstring[(line_number + 1):]
        lines = 0

        for code in example_section:
            if code == "":
                # May be end of the 'Example' section or just a line break
                # in the codes.

                if example_section[lines + 1].startswith("    "):
                    lines += 1
                    continue
                else:
                    break

            elif code.startswith("        "):
                lines += 1
                splited_docstring[line_number + lines] = code[4:]

            elif code.startswith("    "):
                lines += 1
                splited_docstring[line_number + lines] = code.lstrip(" ")

        line_with_language = "\n```{language}".format(language=language)
        splited_docstring.insert(line_number + 1, line_with_language)
        splited_docstring.insert(line_number + 1 + lines + 1, "```")

    def markdown_returns_or_yields(line_number, line):
        """
        Markdown the `Returns` or `Yields` section.

        Example: (markdown)
                Returns:
                    Return description.

            converts to:

                **Returns:**

                - str
                    - Return description.
        """
        bold_header(line_number, line)

        nonlocal splited_docstring
        first_line_description = splited_docstring[line_number + 1]
        new_first_line_description = "    - " + first_line_description[4:]
        splited_docstring[line_number + 1] = new_first_line_description

        return_annotation = parse_return_annotation(object_name)

        if return_annotation:
            return_type_line = "- " + return_annotation
            splited_docstring.insert(line_number + 1, return_type_line)

    def markdown_todo(line_number, line):
        """
        Markdown the `Todo:` section.

        Example: (markdown)
                Todo:
                    - one item
                    - two items
                        over two lines

            converts to:

                **Todo:**:

                - [ ] one item
                - [ ] two items
                over two lines
        """
        bold_header(line_number, line)

        nonlocal splited_docstring
        todo_section = splited_docstring[(line_number + 1):]
        lines = 0

        for todo in todo_section:
            if todo == "":  # End of 'Todo' section
                break

            elif todo.startswith("        "):
                lines += 1
                splited_docstring[line_number + lines] = todo.lstrip(" ")

            elif todo.startswith("    -"):
                lines += 1
                splited_docstring[line_number + lines] = \
                    todo.replace("    -", "- [ ]")

    functions = {
        "Arguments:": markdown_description_sections,
        "Attributes:": markdown_description_sections,
        "Note:": bold_header,
        "Raises:": markdown_description_sections,
        "Returns:": markdown_returns_or_yields,
        "Todo:": markdown_todo,
        "Warning:": bold_header,
        "Yields:": markdown_returns_or_yields
    }

    for line_number, line in enumerate(splited_docstring):
        if line.startswith("Example:"):  # May be also 'Example: (markdown)'.
            markdown_example(line_number)

        elif line in functions:
            functions[line](line_number, line)

    return "\n".join(splited_docstring)
