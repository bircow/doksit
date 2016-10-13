"""
Description.
"""

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
        if r"\_\_init\_\_" in line:
            line = line.replace(r"\_\_init\_\_", "__init__")

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
    return START + "97;40;1m" + line.strip("*") + END


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


def color_documentation(documentation: str) -> str:
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
    split_documentation = documentation.split("\n")
    split_documentation[0] = START + "31;40;1m" + split_documentation[0] + END
    modules_documentation = split_documentation[1:]

    for index, module in enumerate(modules_documentation, start=1):
        split_documentation[index] = _color_module_documentation(module)

    return "\n".join(split_documentation)
