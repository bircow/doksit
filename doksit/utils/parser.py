from collections import OrderedDict
import re

parameter_regex = re.compile("[\w_]+:?([\w_\[\]\.]+)?=?(.+)?")


def parse_parameters(parameters: OrderedDict) -> dict:
    """
    Parse the given parameters (come from a method / function) to readable
    format.

    This function is used internally by 'markdown_docstring' method from
    'doksit.utils.parser' for markdowning a 'Arguments' section in a docstring.

    Arguments:
        parameters:
            Parameters of method / function with annotations and default
            values if any.

    Returns:
        Dictionary of parameters names with parsed string for documentation.

    Example:
        {"foo": "foo (str)", "bar": "bar (int, optional, default 0)"}
    """
    output = {}

    for parameter in parameters:
        if parameter in ["self", "cls"]:
            continue
        else:
            to_parse = str(parameters[parameter])
            annotation, default = \
                parameter_regex.search(to_parse).groups()

            if annotation.startswith("typing."):
                # Annotation is for example 'typing.List', but this form
                # user didn't write. He / she wrote eg. 'List[str]', which is
                # internally in Python 'typing.List<~T>[str]

                bad_annotation = str(parameters[parameter].annotation)
                annotation = bad_annotation.lstrip("typing.").replace(
                    "<~T>", "")

            output[parameter] = "{0} ({1}".format(parameter, annotation)

            if default:
                output[parameter] = output[parameter] + ", optional" \
                    ", default {}".format(default)

            output[parameter] = output[parameter] + ")"

    return output


def markdown_docstring(docstring: str,
                       parameters: OrderedDict = OrderedDict()) \
        -> str:
    """
    Read the given docstring and convert it to Markdown.

    This function is used internally by 'get_documentation' from 'doksit.main'.

    Arguments:
        docstring:
            Docstring of class / method / function.
        parameters:
            Parameters of method / function which will be passed to
            'parse_parameters' function from 'doksit.utils.parser'.

    Returns:
        Docstring in Markdown format.

    Example:
        This is a brif description of object.
        \n
        This is a long paragraph.
        \n
        **Arguments**:
        \n
        - foo (str):
            - Foo description.
        - bar (int, optional, 1):
            - Bar description.
        \n
        **Returns:**
            True if something.
    """
    splited_docstring = docstring.split("\n")

    for line_number, line in enumerate(splited_docstring):
        if line.startswith("Arguments:"):
            splited_docstring[line_number] = "**Arguments:**\n"

        elif line.startswith("Attributes:"):
            """
            Convert for example:

                Arguments:
                    attribute_name (type):
                        Attribute description.
                    another_one (type):
                        Long attribute description
                        over two lines.

            to:

                **Arguments:**:

                - attribute_name (type):
                    - Attribute description.
                - another_one (type):
                    - Long attribute description
                over two lines.
            """
            splited_docstring[line_number] = "**Attributes:**\n"

            attributes = splited_docstring[(line_number + 1):]
            lines = 0
            is_first_line_description = False

            for attribute in attributes:
                if attribute == "":  # End of 'Attributes' section.
                    break

                elif attribute.startswith("        "):
                    lines += 1

                    if is_first_line_description:
                        splited_docstring[line_number + lines] = \
                            "    - " + attribute.lstrip(" ")

                        is_first_line_description = False
                    else:
                        splited_docstring[line_number + lines] = \
                            attribute.lstrip(" ")

                elif attribute.startswith("    "):
                    lines += 1
                    splited_docstring[line_number + lines] = \
                        "- " + attribute.lstrip(" ")

                    # Next line should be an attribute description.

                    is_first_line_description = True

        elif line.startswith("Example:"):
            """
            Convert for example:

                Example:
                    >>> x = 1
                    >>> y = 2
                    >>> print(x * y)

            to:

                Example:

                ```python
                >>> x = 1
                >>> y = 2
                >>> print(x * y)
                ```
            """
            codes = splited_docstring[(line_number + 1):]
            lines = 0

            for code in codes:
                if code == "":  # End of 'Example' section.
                    break

                elif code.startswith("    "):
                    lines += 1
                    splited_docstring[line_number + lines] = code[4:]

            splited_docstring.insert((line_number + 1), "\n```python")
            splited_docstring.insert((line_number + 1 + lines + 1), "```")

        elif line.startswith("Note:"):
            splited_docstring[line_number] = "**Note:**"

        elif line.startswith("Raises:"):
            """
            Convert for example:

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

            to:

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
            splited_docstring[line_number] = "**Raises:**\n"

            errors = splited_docstring[(line_number + 1):]
            lines = 0
            is_first_line_description = False

            for error in errors:
                if error == "":  # End of 'Raises' section.
                    break

                elif error.startswith("            "):
                    lines += 1
                    splited_docstring[line_number + lines] = error.lstrip(" ")

                elif error.startswith("        "):
                    lines += 1

                    try:
                        int(error.lstrip(" ")[0])

                        splited_docstring[line_number + lines] = \
                            "    " + error.lstrip(" ")
                    except ValueError:
                        if is_first_line_description:
                            splited_docstring[line_number + lines] = \
                                "    - " + error.lstrip(" ")

                            is_first_line_description = False
                        else:
                            splited_docstring[line_number + lines] = \
                                error.lstrip(" ")

                elif error.startswith("    "):
                    lines += 1
                    splited_docstring[line_number + lines] = \
                        "- " + error.lstrip(" ")

                    # Next line should be an error description.

                    is_first_line_description = True

        elif line.startswith("Returns:"):
            splited_docstring[line_number] = "**Returns:**"

        elif line.startswith("Todo:"):
            """
            Convert for example:

                Todo:
                    - one item
                    - two items
                        over two lines

            to:

                **Todo:**:

                - [ ] one item
                - [ ] two items
                over two lines
            """
            splited_docstring[line_number] = "**Todo:**\n"

            todo_list = splited_docstring[(line_number + 1):]
            lines = 0

            for todo in todo_list:
                if todo == "":  # End of 'Todo' section
                    break

                elif todo.startswith("    -"):
                    lines += 1
                    splited_docstring[line_number + lines] = \
                        todo.replace("    -", "- [ ]")

                elif todo.startswith("        "):
                    lines += 1
                    splited_docstring[line_number + lines] = \
                        todo.lstrip(" ")

        elif line.startswith("Yields:"):
            splited_docstring[line_number] = "**Yields:**"

    return "\n".join(splited_docstring)
