import inspect

import pytest

from doksit.utils.parsers import (
    _bold_header, ARGUMENT_REGEX, _markdown_arguments_section,
    _markdown_attributes_section, LANGUAGE_REGEX, _markdown_example_section,
    _markdown_note_section, _markdown_raises_section,
    _markdown_returns_section, _markdown_todo_section,
    _markdown_warning_section, _markdown_yields_section,
    get_markdowned_docstring)

from tests.test_data.module import Foo, function


def test_bold_header():
    assert _bold_header("Note:") == "**Note:**"
    assert _bold_header("Raises:") == "**Raises:**\n"


@pytest.mark.parametrize("line", [
    "    foo:",
    "    foo (str):",
    "    foo (str, optional, default 'Foo')"
])
def test_ARGUMENT_REGEX_for_the_arguments_section(line):
    assert ARGUMENT_REGEX.search(line).group(1) == "foo"


def test_markdown_arguments_section():
    """
    Method `Foo.__init__` has following arguments section:

        Arguments:
            x:
                Description of
                'x'.
            y:
                Description of 'y'.
            z:
                Description of 'z'.

    and following parameters:

        x: str, y: float = 1.0, z: List[int] = []
    """
    method_docstring = inspect.getdoc(Foo.__init__)
    split_docstring = method_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_arguments = \
        _markdown_arguments_section(2, copy, Foo.__init__)
    joined_docstring = "\n".join(markdowned_arguments)

    expected_result_draft = [
        "**Arguments:**\n",
        "- x (str):",
        "    - Description of",
        "      'x'.",
        "- y (float, optional, default 1.0):",
        "    - Description of 'y'.",
        "- z (List[int], optional, default []):",
        "    - Description of 'z'."
    ]
    expected_result = "\n".join(expected_result_draft)

    assert expected_result in joined_docstring


def test_attributes_section():
    """
    Class `Foo` has following attributes:

        Attributes:
            foo (str):
                Foo is the attribute.
            bar (int):
                Bar is another
                attribute.
    """
    class_docstring = inspect.getdoc(Foo)
    split_docstring = class_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_attributess = _markdown_attributes_section(7, copy)
    joined_docstring = "\n".join(markdowned_attributess)

    expected_result_draft = [
        "**Attributes:**\n",
        "- foo (str):",
        "    - Foo is the attribute.",
        "- bar (int):",
        "    - Bar is another",
        "      attribute.",
    ]
    expected_result = "\n".join(expected_result_draft)

    assert expected_result in joined_docstring


@pytest.mark.parametrize("line", [
    "Example: (markdown)",
    "Example: (bash)"
])
def test_programming_LANGUAGE_REGEX_for_the_example_section(line):
    assert LANGUAGE_REGEX.search(line).group(1) in ["markdown", "bash"]


def test_markdown_example_section():
    """
    Method `Foo.method` has following example section:

        Example: (markdown)
            # Heading
    """
    method_docstring = inspect.getdoc(Foo.method)
    split_docstring = method_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_example = _markdown_example_section(10, copy)
    joined_docstring = "\n".join(markdowned_example)

    expected_result_draft = [
        "Example:\n",
        "```markdown",
        "# Heading",
        "```"
    ]
    expected_result = "\n".join(expected_result_draft)

    assert expected_result in joined_docstring


def test_markdown_another_example_section():
    """
    Function `Function` has following example section:

        Example:
            # This is an example code.

            # This part is after line break.
    """
    function_docstring = inspect.getdoc(function)
    split_docstring = function_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_example = _markdown_example_section(11, copy)
    joined_docstring = "\n".join(markdowned_example)

    expected_result_draft = [
        "Example:\n",
        "```python",
        "# This is an example code.",
        "",
        "# This part is after line break.",
        "```"
    ]
    expected_result = "\n".join(expected_result_draft)

    assert expected_result in joined_docstring


def test_markdown_note_section():
    """
    Class `Foo` has following note section:

        Note:
            This is a note.
    """
    class_docstring = inspect.getdoc(Foo)
    split_docstring = class_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_note = _markdown_note_section(4, copy)

    assert "**Note:**" in markdowned_note


def test_markdown_raises_section():
    """
    Method `Foo.__init__` has following raises section:

        Raises:
            AssertionError:
                Assertion failed.
            TypeError:
                TypeError
                description.
            ValueError:
                1. Invalid argument for
                    'x'.
                2. Invalid argument for 'y'.
                3. Invalid argument for 'z'.
    """
    method_docstring = inspect.getdoc(Foo.__init__)
    split_docstring = method_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_raises = _markdown_raises_section(11, copy)
    joined_docstring = "\n".join(markdowned_raises)

    expected_result_draft = [
        "**Raises:**\n",
        "- AssertionError:",
        "    - Assertion failed.",
        "- TypeError:",
        "    - TypeError",
        "      description.",
        "- ValueError:",
        "    1. Invalid argument for",
        "       'x'.",
        "    2. Invalid argument for 'y'.",
        "    3. Invalid argument for 'z'."
    ]
    expected_result = "\n".join(expected_result_draft)

    assert expected_result in joined_docstring


def test_markdown_returns_section():
    """
    Method `Foo.static_method` has following returns section:

        Returns:
            str:
                Return description
                over two lines.
    """
    method_docstring = inspect.getdoc(Foo.static_method)
    split_docstring = method_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_returns = _markdown_returns_section(2, copy, Foo.static_method)
    joined_docstring = "\n".join(markdowned_returns)

    expected_result_draft = [
        "**Returns:**\n",
        "- str:",
        "    - Return description",
        "      over two lines.",
    ]
    expected_result = "\n".join(expected_result_draft)

    assert expected_result in joined_docstring


def test_markdown_todo_section():
    """
    CLass `Foo` has following todo section:

        Todo:
            - one thing
            - two
                things
    """
    class_docstring = inspect.getdoc(Foo)
    split_docstring = class_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_todo = _markdown_todo_section(14, copy)
    joined_docstring = "\n".join(markdowned_todo)

    expected_result_draft = [
        "**Todo:**\n",
        "- [ ] one thing",
        "- [ ] two",
        "      things"
    ]
    expected_result = "\n".join(expected_result_draft)

    assert expected_result in joined_docstring


def test_markdown_warning_section():
    """
    Method `Foo.method` has following warning section:

        Warning:
            This is a warning.
    """
    method_docstring = inspect.getdoc(Foo.method)
    split_docstring = method_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_warning = _markdown_warning_section(4, copy)

    assert "**Warning:**" in markdowned_warning


def test_markdown_yields_section():
    """
    Function `functions` has following yields section:

        Yields:
            Integer.

    and this return annotation:

        int
    """
    function_docstring = inspect.getdoc(function)
    split_docstring = function_docstring.split("\n")

    copy = list(split_docstring)
    markdowned_yields = _markdown_yields_section(8, copy, function)
    joined_docstring = "\n".join(markdowned_yields)

    expected_result_draft = [
        "**Yields:**\n",
        "- int:",
        "    - Integer"
    ]
    expected_result = "\n".join(expected_result_draft)

    assert expected_result in joined_docstring


def test_get_markdowned_docstring():
    """
    Class `Foo` has following docstring:

        This is a brief description.

        This is a long description.

        Note:
            This is a note.

        Attributes:
            foo (str):
                Foo is the attribute.
            bar (int):
                Bar is another
                attribute.

        Todo:
            - one thing
            - two
                things
    """
    markdowned_docstring = get_markdowned_docstring(Foo)

    expected_result_draft = [
        "This is a brief description.",
        "",
        "This is a long description.",
        "",
        "**Note:**",
        "    This is a note.",
        "",
        "**Attributes:**\n",
        "- foo (str):",
        "    - Foo is the attribute.",
        "- bar (int):",
        "    - Bar is another",
        "      attribute.",
        "",
        "**Todo:**\n",
        "- [ ] one thing",
        "- [ ] two",
        "      things"
    ]
    expected_result = "\n".join(expected_result_draft)

    print(markdowned_docstring)
    assert expected_result in markdowned_docstring
