"""
Here are defined parsers.
"""

import inspect
import re

from typing import Any, List, Union

PARAMETER_REGEX = re.compile(r"[\w_]+:?([\w_\[\]\.]+)?=?(.+)?")


def parse_parameters(object_name: Any) -> Union[dict, None]:
    """
    Parse parameters from the given function / method object to human readable
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
        {"foo": "foo (str):", "bar": "bar (int, optional, default 1):"}
    """
    parameters = inspect.signature(object_name).parameters
    parsed_parameters = {}

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

            parsed_parameters[parameter] = "{parameter} ({annotation}" \
                .format(parameter=parameter, annotation=annotation)

            if default_value:
                if default_value == "None":
                    parsed_parameters[parameter] += ", optional"
                else:
                    parsed_parameters[parameter] += ", optional, default " \
                        "{default_value}".format(default_value=default_value)

            parsed_parameters[parameter] += "):"

    return parsed_parameters


BUILTIN_TYPE_REGEX = re.compile(r"<class '([\w]+)'>")


def parse_return_annotation(object_name: Any) -> Union[str, None]:
    """
    Parse return annotation from the given function / method object to human
    readable format.

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


def _bold_header(header: str) -> str:
    """
    Make the header bold and for some add a new line at the end of it.

    Arguments:
        header (str):
            Line in a docstring with a header.

    Example: (markdown)
        Arguments: -> **Arguments:**\n
        Note:      -> **Note:**

    Returns:
        str:
            Bold header with / without the new line at the end.
    """
    bold_header = "**" + header + "**"
    headers_with_new_line = (
        "Arguments:",
        "Attributes:",
        "Raises:",
        "Returns:",
        "Todo:",
        "Yields:"
    )

    # Headers without the new line at the end are:
    #
    # "Note:",
    # "Warning:"

    if header in headers_with_new_line:
        bold_header += "\n"

    return bold_header


ARGUMENT_REGEX = re.compile(r"^    ([\w_\*]+)")


def _markdown_arguments_section(line_number: int, docstring: List[str],
                                object_name: Any=None) -> List[str]:
    """
    Markdown the `Arguments` section.

    Arguments:
        line_number (int):
            Where the `Arguments` section starts.
        docstring (List[str]):
            Split docstring.
        object_name (Any)
            Function / method object for getting its parameters annotation.

    Example: (markdown)
            Arguments:
                foo:
                    Argument description.
                bar:
                    Argument description
                    over two lines.

            # or

            Arguments:
                foo (int):
                    Argument description.
                bar (str, optional, default "bar")
                    Argument description
                    over two lines.

        converts to:

            **Arguments:**

            - foo (int)
                - Argument description.
            - bar (str, optional, default "bar")
                - Argument description
                  over two lines.

    Note:
        If a user didn't write the parameter annotation, then it will be
        automatically inserted.

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Arguments` section.
    """
    # Codes below will be shared with `_markdown_attributes_section`, but
    # some of them will be only for this function.

    arguments_header = docstring[line_number]
    docstring[line_number] = _bold_header(arguments_header)

    arguments_content = docstring[(line_number + 1):]
    is_first_line_description = False
    is_arguments_section = True if object_name is not None else False

    if is_arguments_section:
        parsed_parameters = parse_parameters(object_name)

    for number, line in enumerate(arguments_content, start=line_number + 1):
        if line.startswith("        "):
            if is_first_line_description:
                docstring[number] = line.replace("        ", "    - ")

                is_first_line_description = False
            else:
                docstring[number] = line.replace("        ", "      ")

        elif line.startswith("    "):
            if is_arguments_section and parsed_parameters is not None:
                argument_name = ARGUMENT_REGEX.search(line).group(1)

                if argument_name.startswith("*"):  # Eg, *args or **kwargs
                    argument_name = argument_name.lstrip("*")

                docstring[number] = "- " + parsed_parameters[argument_name]
            else:
                docstring[number] = line.replace("    ", "- ")

            # Next line should be an attribute description.

            is_first_line_description = True

        elif line == "":  # End of the `Arguments` section.
            break

    return docstring


def _markdown_attributes_section(line_number: int, docstring: List[str]) \
        -> List[str]:
    """
    Markdown the `Attributes` section.

    Arguments:
        line_number (int):
            Where the `Attributes` section starts.
        docstring (List[str]):
            Split docstring.

    Example: (markdown)
            Attributes:
                foo (int):
                    Attribute description.
                bar (str):
                    Attribute description
                    over two lines.

        converts to:

            **Attributes:**

            - foo (int):
                - Attribute description.
            - bar (str):
                - Attribute description
                  over two lines.

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Attributes` section.
    """
    # Codes are same like for the `Arguments` section (apart from the ones for
    # `Arguments` section only).

    return _markdown_arguments_section(line_number, docstring)


LANGUAGE_REGEX = re.compile(r"Example: \((\w+)\)")


def _markdown_example_section(line_number: int, docstring: List[str]) \
        -> List[str]:
    """
    Markdown the `Example` section.

    Arguments:
        line_number (int):
            Where the `Example` section starts.
        docstring (List[str]):
            Split docstring.

    Example: (markdown)
            Example:
                print(True)

                # Line after the beak line.

            # or

            Example: (markdown)
                ...

        converts to:

            Example:

            ```python
            print(True)

            # Line after the break line.
            ```

            # or

            Example:

            ```markdown
            ...
            ```

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Example` section.
    """
    example_header = docstring[line_number]

    if LANGUAGE_REGEX.search(example_header):
        language = LANGUAGE_REGEX.search(example_header).group(1)

        docstring[line_number] = "Example:"
    else:
        language = "python"

    example_content = docstring[(line_number + 1):]

    for number, line in enumerate(example_content, start=line_number + 1):
        if line.startswith("        "):  # A code indendation.
            docstring[number] = line[4:]

        elif line.startswith("    "):
            docstring[number] = line.lstrip(" ")

        elif line == "":
            # Attention, may be a line break also, not only end of the
            # `Example` section.

            if docstring[number + 1].startswith("    "):
                continue
            else:
                example_end = number - 1
                break

    line_with_language = "\n```{language}".format(language=language)
    docstring.insert(line_number + 1, line_with_language)

    try:
        assert example_end
    except NameError:
        example_end = len(docstring)

    docstring.insert(example_end + 1, "```")  # + 1 because new item was added.

    return docstring


def _markdown_note_section(line_number: int, docstring: List[str]) \
        -> List[str]:
    """
    Markdown the `Note` section.

    Arguments:
        line_number (int):
            Where the `Note` section starts.
        docstring (List[str]):
            Split docstring.

    Example: (markdown)
            Note:
                Note description.

        converts to:

            **Note:**
                Note description.

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Note` section.
    """
    note_header = docstring[line_number]
    docstring[line_number] = _bold_header(note_header)

    return docstring


def _markdown_raises_section(line_number: int, docstring: List[str]) \
        -> List[str]:
    """
    Markdown the `Raises` section.

    Arguments:
        line_number (int):
            Where the `Raises` section starts.
        docstring (List[str]):
            Split docstring.

    Example: (markdown)
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

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Raises` section.
    """
    raises_header = docstring[line_number]
    docstring[line_number] = _bold_header(raises_header)

    raises_content = docstring[(line_number + 1):]
    is_first_line_description = False

    for number, line in enumerate(raises_content, start=line_number + 1):
        if line.startswith("            "):
            docstring[number] = line.replace("            ", "       ")

        elif line.startswith("        "):
            # Attention, may be ordered (numbered) error description.

            try:
                int(line.lstrip(" ")[0])

                docstring[number] = line.replace("        ", "    ")
                continue
            except ValueError:
                pass

            if is_first_line_description:
                docstring[number] = line.replace("        ", "    - ")

                is_first_line_description = False
            else:
                docstring[number] = line.replace("        ", "      ")

        elif line.startswith("    "):
            docstring[number] = line.replace("    ", "- ")

            # Next line should be an error description.

            is_first_line_description = True

        elif line.startswith(""):  # End of the `Raises` section.
            break

    return docstring


def _markdown_returns_section(line_number: int, docstring: List[str],
                              object_name: Any) -> List[str]:
    """
    Markdown the `Returns` section.

    Arguments:
        line_number (int):
            Where the `Returns` section starts.
        docstring (List[str]):
            Split docstring.
        object_name (Any)
            Function / method object for getting its return (yield) annotation.

    Example: (markdown)
            Returns:
                Return description
                over two lines.

            # or

            Returns:
                str:
                    Return description
                    over two lines.

        converts to:

            **Returns:**

            - str:
                - Return description
                  over two lines.

    Note:
        If a user didn't write the return annotation, then it will be
        automatically inserted.

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Returns` section.
    """
    returns_header = docstring[line_number]
    docstring[line_number] = _bold_header(returns_header)

    returns_start = line_number + 1

    if docstring[returns_start].endswith(":"):
        docstring[returns_start] = \
            docstring[returns_start].replace("    ", "- ")
        docstring[returns_start + 1] = \
            docstring[returns_start + 1].replace("        ", "    - ")

        returns_rest = docstring[(line_number + 3):]

        for number, line in enumerate(returns_rest, start=line_number + 3):
            if line == "":  # End of the `Returns` section
                break
            else:
                docstring[number] = line.replace("        ", "      ")

    else:
        docstring[returns_start] = \
            docstring[returns_start].replace("    ", "    - ")

        returns_rest = docstring[(line_number + 2):]

        for number, line in enumerate(returns_rest, start=line_number + 2):
            if line == "":  # End of the `Returns` section
                break
            else:
                docstring[number] = line.replace("    ", "      ")

        return_annotation = str(parse_return_annotation(object_name))
        docstring.insert(returns_start, "- " + return_annotation + ":")

    return docstring


def _markdown_todo_section(line_number: int, docstring: List[str]) \
        -> List[str]:
    """
    Markdown the `Todo` section.

    Arguments:
        line_number (int):
            Where the `Todo` section starts.
        docstring (List[str]):
            Split docstring.

    Example: (markdown)
            Todo:
                - first item
                - second item
                    over two lines

        converts to:

            **Todo:**:

            - [ ] one item
            - [ ] two items
                  over two lines

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Todo` section.
    """
    todo_header = docstring[line_number]
    docstring[line_number] = _bold_header(todo_header)

    todo_content = docstring[(line_number + 1):]

    for number, line in enumerate(todo_content, start=line_number + 1):
        if line.startswith("    -"):
            docstring[number] = line.replace("    -", "- [ ]")

        elif line.startswith("        "):
            docstring[number] = line.replace("        ", "      ")

        elif line == "":  # End of the `Todo` section.
            break

    return docstring


def _markdown_warning_section(line_number: int, docstring: List[str]) \
        -> List[str]:
    """
    Markdown the `Warning` section.

    Arguments:
        line_number (int):
            Where the `Warning` section starts.
        docstring (List[str]):
            Split docstring.

    Example: (markdown)
            Warning:
                Warning description.

        converts to:

            **Warning:**
                Warning description.

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Warning` section.
    """
    warning_header = docstring[line_number]
    docstring[line_number] = _bold_header(warning_header)

    return docstring


def _markdown_yields_section(line_number: int, docstring: List[str],
                             object_name: Any) -> List[str]:
    """
    Markdown the `Yields` section.

    Arguments:
        line_number (int):
            Where the `Yields` section starts.
        docstring (List[str]):
            Split docstring.
        object_name (Any)
            Function / method object for getting its return (yield) annotation.

    Example: (markdown)
            Yields:
                Yield description
                over two lines.

            # or

            Yields:
                int:
                    Yield description
                    over two lines.

        converts to:

            **Yields:**

            - int:
                - Yield description.
                  over two lines.

    Note:
        If a user didn't write the return annotation, then it will be
        automatically inserted.

    Returns:
        List[str]:
            Updated split docstring with the markdowned `Yields` section.
    """
    # Codes are same like for the `Retuns` section, only header name is
    # different.

    return _markdown_returns_section(line_number, docstring, object_name)


def get_markdowned_docstring(object_name: Any) -> str:
    """
    Get the object docstring and convert it to Markdown format.

    Arguments:
        object_name:
            For which object to get its docstring.

    Returns:
        The markdowned docstring or empty string (the object
        doesn't have any docstring.)

    Example:
        This is a brief object description.

        This is a long paragraph.

        **Arguments:**

        - foo (str):
            - Foo description.
        - bar (int, optional, default 1):
            - Bar description.

        **Returns:**

        - bool:
            - True if something.
    """
    docstring = inspect.getdoc(object_name)

    if not docstring:
        return ""

    split_docstring = docstring.split("\n")

    headers = {
        "Arguments:": _markdown_arguments_section,
        "Attributes:": _markdown_attributes_section,
        "Note:": _markdown_note_section,
        "Raises:": _markdown_raises_section,
        "Returns:": _markdown_returns_section,
        "Todo:": _markdown_todo_section,
        "Warning:": _markdown_warning_section,
        "Yields:": _markdown_yields_section
    }

    # Function for "Example:" header is handled separately, because
    # it may be also "Example: (markdown)".

    for line_number, line in enumerate(split_docstring):
        if line.startswith("Example:"):
            split_docstring = \
                _markdown_example_section(line_number, split_docstring)

        elif line in ["Arguments:", "Returns:", "Yields:"]:
            # These headers need another argument.

            split_docstring = \
                headers[line](line_number, split_docstring, object_name)

        elif line in headers:
            split_docstring = headers[line](line_number, split_docstring)

    markdowned_docstring = "\n".join(split_docstring)

    return markdowned_docstring
