"""
Here are defined highlighters (`--smooth` and `--colored` flags) for the
generated API documentation.
"""

import re

from click import style

from doksit.models import Base

HEADINGS = (
    "# ",
    "## ",
    "### class",
    "#### constructor",
    "#### property",
    "#### method",
    "### function"
)
HEADERS = (
    "**Arguments:**",
    "**Attributes:**",
    "**Note:**",
    "**Raises:**",
    "**Returns:**",
    "**Todo:**",
    "**Warning:**",
    "**Yields:**"
)


class SmoothHighlighter(Base):
    """
    Class for the `--smooth` flag of the `doksit api` command.
    """

    __slots__ = ("documentation")

    def __init__(self, documentation: str) -> None:
        """
        Initialize an instance of `SmoothHiglihter` class.

        Arguments:
            documentation:
                Generated API documentation.
        """
        self.documentation = documentation

    def get_api_documentation(self) -> str:
        """
        Returns:
            Smooth API documentation output.
        """
        split_doc = self.documentation.split("\n")
        is_example_section = False

        for line_number, line in enumerate(split_doc):
            if line.startswith("```"):
                if is_example_section:
                    is_example_section = False
                else:
                    is_example_section = True

            elif not is_example_section:
                if line.startswith(HEADINGS):
                    split_doc[line_number] = style(line, bold=True)

                elif line in HEADERS:
                    split_doc[line_number] = style(line.strip("*"), bold=True)

                elif line.startswith("[source](http"):
                    if split_doc[line_number - 2].startswith("\x1b[1m## "):
                        # Links to a module will be removed, because they are
                        # duplicate with Python module path + 1 blank line.

                        del split_doc[line_number]
                        del split_doc[line_number]
                    else:
                        split_doc[line_number] = self._modify_link(line)

        return "\n".join(split_doc)

    def _modify_link(self, line: str) -> str:
        """
        Change URL to an Unix file path.

        Arguments:
            line:
                Line containing URL to source codes on GitHub.

        Returns:
            File path to a module with optional object location.

        Example:
            "-> doksit.api#L1-L10"
        """
        line = line.replace("[source](", "") \
            .replace(self.repository_prefix, "")

        return "-> " + line[:-1]  # Last character is ")"


START = "\x1b["
END = "\x1b[K\x1b[0m"

INLINE_CODE_REGEX = re.compile(r"`[^`]+`")


class ColoredHighlighter(SmoothHighlighter):
    """
    Class for the `--colored` flag of the `doksit api` command.

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
    """

    def __init__(self, *args) -> None:
        """
        Initialize an instance of `ColoredHiglihter` class.

        Arguments:
            *args:
                Same arguments like for the `SmoothHiglighter` constructor.
        """
        super().__init__(*args)

    def get_api_documentation(self) -> str:
        """
        Returns:
            Colored API documentation output.
        """
        split_doc = self.documentation.split("\n")
        is_example_section = False

        for line_number, line in enumerate(split_doc):
            if line.startswith("```"):
                split_doc[line_number] = START + "30;107m" + line + END

                if is_example_section:
                    is_example_section = False

                    del split_doc[line_number]

                    # Fix foreground and background color for the line now
                    # placed in this index.

                    split_doc[line_number] = \
                        self._color_rest(split_doc[line_number])
                else:
                    is_example_section = True

            elif is_example_section:
                split_doc[line_number] = START + "30;107m" + line + END

            elif not is_example_section:
                if line.startswith(HEADINGS):
                    split_doc[line_number] = self._color_heading(line)

                elif line.startswith(HEADERS):
                    split_doc[line_number] = self._color_header(line)

                elif line.startswith("[source](http"):
                    if "34;40;1m" in split_doc[line_number - 2]:  # Module.
                        # Links to a module will be removed, because they are
                        # duplicate with Python module path.

                        del split_doc[line_number]
                        del split_doc[line_number]  # Blank line.

                        # Fix foreground and background color for the line now
                        # placed in this index.

                        split_doc[line_number] = \
                            self._color_rest(split_doc[line_number])
                    else:
                        split_doc[line_number] = self._modify_link(line)

                else:
                    split_doc[line_number] = self._color_rest(line)

        return "\n".join(split_doc)

    @staticmethod
    def _color_heading(line: str) -> str:
        """
        Color the given heading.

        Arguments:
            line:
                Line with a heading.

        Legend of used ANSI escape sequences:

        - 31;40;1m
            - bold red foreground, black background (title)
        - 34;40;1m
            - bold blue foreground, black background (modules)
        - 32;40;1m
            - bold green foreground, black background (classes)
        - 33;40;1m
            - bold yellow foreground, black background (methods)
        - 36;40;1m
            - bold cyan foreground, black background (functions)

        Returns:
            The colored heading.
        """
        if line.startswith(HEADINGS[0]):
            return START + "31;40;1m" + line + END

        elif line.startswith(HEADINGS[1]):
            return START + "34;40;1m" + line + END

        elif line.startswith(HEADINGS[2]):
            return START + "32;40;1m" + line + END

        elif line.startswith(HEADINGS[3]) \
                or line.startswith(HEADINGS[4]) \
                or line.startswith(HEADINGS[5]):
            return START + "33;40;1m" + line + END

        elif line.startswith(HEADINGS[6]):
            return START + "36;40;1m" + line + END

    @staticmethod
    def _color_header(line: str) -> str:
        """
        Color the giving header.

        Arguments:
            line:
                Line with a header.

        Legend of used ANSI escape sequences:

        - 97;40;1m
            - bold white foreground, black background

        Returns:
            The colored header.
        """
        return START + "97;40;1m" + line.strip("*") + END

    def _modify_link(self, line: str) -> str:
        """
        Change URL to an Unix file path and color that line.

        Arguments:
            line:
                Line containing URL to source codes on GitHub.

        Legend of used ANSI escape sequences:

        - 97;40m
            - white foreground, black background

        Returns:
            Colored file path to a module with optional object location.

        Example:
            "-> doksit/api.py#L10-L20"  # Without colors here.
        """
        line = line \
            .replace("[source](", "") \
            .replace(self.repository_prefix, "")

        return START + "97;40m" + "-> " + line[:-1] + END  # -1 is ")".

    def _color_rest(self, line: str) -> str:
        """
        Color the rest of text in the API documentation.

        Arguments:
            line:
                Content on a line.

        Legend of used ANSI escape sequences:

        - 97;40m
            - white foreground, black background

        Returns:
            The highlighted line.
        """
        if "`" in line:
            line = self._color_inline_code(line)

        return START + "97;40m" + line + END

    @staticmethod
    def _color_inline_code(line: str) -> str:
        """
        Color inline code(s) like in the example sections (same foreground
        and background colors).

        Arguments:
            line:
                Line containing an inline code(s).

        Legend of used ANSI escape sequences:

        - 30;107m
            - black foreground, white background (inline code)
        - 97;40m
            - white foreground, black background (rest of text)

        Returns:
            The colored inline code in that line.
        """
        inline_codes = INLINE_CODE_REGEX.findall(line)

        for inline_code in inline_codes:
            colored_inline_code = START + "30;107m" + inline_code \
                + START + "97;40m"  # For the rest of text.

            line = line \
                .replace(inline_code, colored_inline_code) \
                .replace("`", "", 2)

        return line
