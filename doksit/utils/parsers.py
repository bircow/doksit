import collections
import re

parameter_regex = re.compile("[\w_]+:?([\w_\[\]\.]+)?=?(.+)?")


def parse_parameters(parameters):
    """
    Parse the given parameters from a method / function to readable format.

    Arguments:
        parameters (OrderedDict):
            Method / function paramaters, which may look like `OrderedDict([
            ('parameter_name', <Parameter "parameter_name:int=1")])`

    If a user doesn't use annotations (doesn't want to or has Python 2.7, in
    which it's not possible), then is expected that he / she writes explicitly
    data types and default values for parameters in the `Arguments:` section
    himself / herself and thus there is nothing to parse.

    Returns:
        False if the user doesn't use the annotations or dictionary with the
        parameter names and their parsed variant, which will be used in the
        'markdown_docstring' function.

    Example:
        {"foo": "foo (str):", "bar": "bar (int, optional, default 0):"}
    """
    output = {}

    for parameter in parameters:
        if parameter in ["self", "cls"]:
            continue
        else:
            to_parse = str(parameters[parameter])
            annotation, default = \
                parameter_regex.search(to_parse).groups()

            if annotation is None:
                return False

            if annotation.startswith("typing."):
                # Annotation is for example `typing.List`, but this form
                # user didn't write. He / she wrote eg. `List[str]`, which is
                # internally in Python `typing.List<~T>[str]`

                bad_annotation = str(parameters[parameter].annotation)
                annotation = bad_annotation.lstrip("typing.").replace(
                    "<~T>", "")

            output[parameter] = "{0} ({1}".format(parameter, annotation)

            if default:
                output[parameter] = output[parameter] + ", optional" \
                    ", default {}".format(default)

            output[parameter] = output[parameter] + "):"

    return output


argument_regex = re.compile("    ([\w_\*]+):")


def markdown_docstring(docstring, parameters=collections.OrderedDict()):
    """
    Read the given docstring and convert it to Markdown.

    Arguments:
        docstring (str):
            Module / class / method / function docstring for markdowning.
        parameters (OrderedDict, optional, default {}):
            Method / function parameters which will be internally passed to the
            'parse_parameters' function.

    Returns:
        Docstring in the Markdown format.

    Example:
        This is a brif description of object.

        This is a long paragraph.

        **Arguments**:

        - foo (str):
            - Foo description.
        - bar (int, optional, default 1):
            - Bar description.

        **Returns:**
            True if something.
    """
    splited_docstring = docstring.split("\n")

    for line_number, line in enumerate(splited_docstring):
        if line.startswith("Arguments:"):
            """
            Convert for example:

                Arguments:
                    foo:
                        Argument description.
                    bar:
                        Argument description
                        over two lines.

            to:

                **Arguments:**:

                - foo (str):
                    - Argument description.
                - bar (int, optional, default 10):
                    - Argument description
                over two lines.
            """
            splited_docstring[line_number] = "**Arguments:**\n"

            arguments = splited_docstring[(line_number + 1):]
            lines = 0
            is_first_line_description = False

            parsed_parameters = parse_parameters(parameters)

            for argument in arguments:
                if argument == "":  # End of 'Arguments' section.
                    break

                elif argument.startswith("        "):
                    lines += 1

                    if is_first_line_description:
                        splited_docstring[line_number + lines] = \
                            "    - " + argument.lstrip(" ")

                        is_first_line_description = False
                    else:
                        splited_docstring[line_number + lines] = \
                            argument.lstrip(" ")

                elif argument.startswith("    "):
                    lines += 1

                    if parsed_parameters:
                        argument_name = argument_regex.search(argument).group(1)

                        if argument_name.startswith("*"):  # *args or **kwargs
                            argument_name = argument_name.lstrip("*")

                        parsed_argument = parsed_parameters[argument_name]
                        splited_docstring[line_number + lines] = \
                            "- " + parsed_argument
                    else:
                        splited_docstring[line_number + lines] = \
                            "- " + argument.lstrip(" ")

                    # Next line should be an argument description.

                    is_first_line_description = True

        elif line.startswith("Attributes:"):
            """
            Convert for example:

                Attributes:
                    attribute_name (type):
                        Attribute description.
                    another_one (type):
                        Long attribute description
                        over two lines.

            to:

                **Attributes:**:

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
                    x = 1
                    y = 2
                    print(x * y)

                    # Line after break line

                    class Foo:
                        pass

            to:

                Example:

                ```python
                x = 1
                y = 2
                print(x * y)

                # Line after break line

                class Foo:
                    pass
                ```
            """
            codes = splited_docstring[(line_number + 1):]
            lines = 0

            for code in codes:
                if code == "":
                    # Check if it's truly end of the 'Example' section or
                    # just line break in the codes.

                    if codes[lines + 1].startswith("    "):
                        lines += 1
                    else:
                        break

                elif code.startswith("        "):
                    lines += 1
                    splited_docstring[line_number + lines] = code[4:]

                elif code.startswith("    "):
                    lines += 1
                    splited_docstring[line_number + lines] = code.lstrip(" ")

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

                    # May be ordered (numbered) error description or not.

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

        elif line.startswith("Warning:"):
            splited_docstring[line_number] = "**Warning:**"

    return "\n".join(splited_docstring)
