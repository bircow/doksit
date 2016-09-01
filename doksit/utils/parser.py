def markdown_docstring(docstring: str) -> str:
    """
    Read the given docstring and convert it to Markdown.

    Arguments:
        docstring:
            Docstring of class / method / function.

    Returns:
        Docstring in Markdown format.
    """
    splited_docstring = docstring.split("\n")

    for line_number, line in enumerate(splited_docstring):
        if line.startswith("Arguments:"):
            splited_docstring[line_number] = "**Arguments:**\n"

        elif line.startswith("Attributes:"):
            """
            Convert

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
            Convert

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
            Convert

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
            Convert

                Todo:
                    - one
                    - two

            to:

                **Todo:**:

                - [ ] one
                - [ ] two
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

        elif line.startswith("Yields:"):
            splited_docstring[line_number] = "**Yields:**"

    return "\n".join(splited_docstring)
