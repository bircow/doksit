import pytest

from doksit.models import Base
from doksit.utils.highlighters import ColoredHighlighter, INLINE_CODE_REGEX

COLORED = ColoredHighlighter("blabla")


def test_get_colored_api_documentation(documentation):
    colored = ColoredHighlighter(documentation)
    colored_doc = colored.get_api_documentation()

    assert colored_doc
    assert "\x1b[31;40;1m# API" in colored_doc
    assert "**Note**" not in colored_doc
    assert "[source](" not in colored_doc


###############################################################################


@pytest.mark.parametrize("text,color", [
    ("# API", "31;40;1m"),
    ("## module", "34;40;1m"),
    ("### class", "32;40;1m"),
    ("#### constructor", "33;40;1m"),
    ("#### property", "33;40;1m"),
    ("#### method", "33;40;1m"),
    ("### function", "36;40;1m")
])
def test_color_heading(text, color):
    colored_heading = COLORED._color_heading(text)

    print(colored_heading)
    assert text in colored_heading
    assert color in colored_heading


###############################################################################


def test_color_header():
    text = "**Note:**"
    colored_header = COLORED._color_header(text)

    assert "*" not in colored_header
    assert "97;40;1m" in colored_header


###############################################################################


def test_modify_link():
    original_link = \
        "[source](" + Base().repository_prefix + "test_data/module.py)"
    modified_link = "-> test_data/module.py"
    colored_link = COLORED._modify_link(original_link)

    assert modified_link in colored_link
    assert "97;40m" in colored_link


###############################################################################


def test_color_rest():
    text = "This is a sample line."
    colored_line = COLORED._color_rest(text)

    assert colored_line == "\x1b[97;40m" + text + "\x1b[K\x1b[0m"


def test_color_rest_with_inline_code_in():
    text = "This is a line with `code`."
    colored_line = COLORED._color_rest(text)

    assert "`" not in colored_line
    assert "30;107m" in colored_line
    assert "97;40m" in colored_line


###############################################################################

@pytest.mark.parametrize("code", [
    "This is a `code`",
    "`doksit.api.DoksitStyle`",
    "Multiple codes `a` and `b`"
])
def test_inline_code_regex(code):
    assert INLINE_CODE_REGEX.findall(code)


def test_color_inline_code():
    sample_line = "This is a line with `code`."
    colored_line = COLORED._color_inline_code(sample_line)

    assert "`" not in colored_line
    assert "30;107m" in colored_line
