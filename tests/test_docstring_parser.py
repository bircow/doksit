import pytest

from doksit.models import BUILTIN_TYPE_REGEX, DocstringParser

from tests.test_data.module import (
    Foo, function, another_function, _hidden_function
)

parser = DocstringParser()


@pytest.mark.parametrize("docstring", [
    [
        "Arguments:",
        "    x:",
        "        Description of",
        "        'x'.",
        "    y:",
        "        Description of 'y'.",
        "    z:",
        "        Description of 'z'.",
        ""
    ],
    [
        "Args:",
        "    x (str): Description of",
        "        'x'.",
        "    y (float, optional, default 1.0): Description of 'y'.",
        "    z (List[int], optional): Description of 'z'.",
        ""
    ]
])
def test_markdown_arguments_section(docstring):
    expected_output = [
        "**Arguments:**\n",
        "- x (str):",
        "    - Description of",
        "      'x'.",
        "- y (float, optional, default 1.0):",
        "    - Description of 'y'.",
        "- z (List[int], optional):",
        "    - Description of 'z'.",
        ""
    ]
    output = parser.markdown_arguments_section(0, docstring, Foo.__init__)

    assert output == expected_output


###############################################################################


def test_markdown_attributes_section():
    data = [
        "Attributes:",
        "    one_a:",
        "        Attribute description.",
        "    one_b (str):",
        "        Attribute description.",
        "    two_a:",
        "        Attribute description",
        "        over two lines.",
        "    two_b (str):",
        "        Attribute description",
        "        over two lines.",
        "    three_a: Attribute description.",
        "    three_b (str): Attribute description.",
        "    four_a: Attribute description",
        "        over two lines.",
        "    four_b (str): Attribute description",
        "        over two lines.",
        ""
    ]
    expected_output = [
        "**Attributes:**\n",
        "- one_a:",
        "    - Attribute description.",
        "- one_b (str):",
        "    - Attribute description.",
        "- two_a:",
        "    - Attribute description",
        "      over two lines.",
        "- two_b (str):",
        "    - Attribute description",
        "      over two lines.",
        "- three_a:",
        "    - Attribute description.",
        "- three_b (str):",
        "    - Attribute description.",
        "- four_a:",
        "    - Attribute description",
        "      over two lines.",
        "- four_b (str):",
        "    - Attribute description",
        "      over two lines.",
        ""
    ]
    output = parser.markdown_attributes_section(0, data)

    assert output == expected_output

###############################################################################


def test_markdown_example_section():
    data = [
        "Example:",
        "    print(True)",
        "",
        "    # Line after the break line.",
        "",
        "    def f():",
        "        pass"
    ]
    expected_output = [
        "Example:",
        "\n```python",
        "print(True)",
        "",
        "# Line after the break line.",
        "",
        "def f():",
        "    pass",
        "```"
    ]
    output = parser.markdown_example_section(0, data)

    assert output == expected_output


def test_markdown_example_section_with_specified_language():
    data = [
        "Example: (markdown)",
        "    ..."
    ]
    expected_output = [
        "Example:",
        "\n```markdown",
        "...",
        "```",
    ]
    output = parser.markdown_example_section(0, data)

    assert output == expected_output


def test_markdown_example_section_before_another_section():
    data = [
        "Example: (markdown)",
        "    ...",
        "",
        "This is a paragraph."
    ]
    expected_output = [
        "Example:",
        "\n```markdown",
        "...",
        "```",
        "",
        "This is a paragraph."
    ]
    output = parser.markdown_example_section(0, data)

    assert output == expected_output


def test_markdown_example_section_with_blank_line_after_it():
    data = [
        "Example: (markdown)",
        "    ...",
        ""
    ]
    expected_output = [
        "Example:",
        "\n```markdown",
        "...",
        "```",
        ""
    ]
    output = parser.markdown_example_section(0, data)

    assert output == expected_output


###############################################################################


def test_markdown_note_section():
    data = [
        "Note:",
        "    Note description",
        "    over two lines."
    ]
    expected_output = [
        "**Note:**",
        "    Note description",
        "    over two lines."
    ]
    output = parser.markdown_note_section(0, data)

    assert output == expected_output

###############################################################################


def test_markdown_raises_section():
    data = [
        "Raises:",
        "    AssertionError:",
        "        Reason.",
        "    ImportError:",
        "        Long reason.",
        "    KeyError: Reason.",
        "    TypeError: Long",
        "        reason.",
        "    ValueError:",
        "        1. reason",
        "        2. long",
        "           reason",
        ""
    ]
    expected_output = [
        "**Raises:**\n",
        "- AssertionError:",
        "    - Reason.",
        "- ImportError:",
        "    - Long reason.",
        "- KeyError:",
        "    - Reason.",
        "- TypeError:",
        "    - Long",
        "      reason.",
        "- ValueError:",
        "    1. reason",
        "    2. long",
        "       reason",
        ""
    ]
    output = parser.markdown_raises_section(0, data)

    assert output == expected_output


###############################################################################


@pytest.mark.parametrize("docstring", [
    [
        "Returns:",
        "    Return description",
        "    over two lines.",
        ""
    ],
    [
        "Returns:",
        "    str: Return description",
        "    over two lines.",
        ""
    ],
    [
        "Returns:",
        "    str:",
        "        Return description",
        "        over two lines.",
        ""
    ]
])
def test_markdown_returns_section(docstring):
    expected_output = [
        "**Returns:**\n",
        "- str:",
        "    - Return description",
        "      over two lines.",
        ""
    ]
    output = parser.markdown_yields_section(0, docstring, Foo.static_method)

    assert output == expected_output


###############################################################################


@pytest.mark.parametrize("docstring", [
    [
        "Todo:",
        "    - first item",
        "    - second item",
        "      over two lines",
        ""
    ],
    [
        "Todo:",
        "    * first item",
        "    * second item",
        "      over two lines",
        ""
    ]
])
def test_markdown_todo_section(docstring):
    expected_output = [
        "**Todo:**\n",
        "- [ ] first item",
        "- [ ] second item",
        "      over two lines",
        ""
    ]
    output = parser.markdown_todo_section(0, docstring)

    assert output == expected_output


###############################################################################


def test_markdown_warning_section():
    data = [
        "Warning:",
        "    Note description",
        "    over two lines."
    ]
    expected_output = [
        "**Warning:**",
        "    Note description",
        "    over two lines."
    ]
    output = parser.markdown_warning_section(0, data)

    assert output == expected_output


###############################################################################


@pytest.mark.parametrize("docstring", [
    [
        "Yields:",
        "    Return description",
        "    over two lines.",
        ""
    ],
    [
        "Yields:",
        "    int: Return description",
        "    over two lines.",
        ""
    ],
    [
        "Yields:",
        "    int:",
        "        Return description",
        "        over two lines.",
        ""
    ]
])
def test_markdown_yields_section(docstring):
    expected_output = [
        "**Yields:**\n",
        "- int:",
        "    - Return description",
        "      over two lines.",
        ""
    ]
    output = parser.markdown_yields_section(0, docstring, function)

    assert output == expected_output


###############################################################################


def test_parse_parameters_with_annotations():
    output = parser._parse_parameters(Foo.__init__)

    assert "self" not in output
    assert output["x"] == "x (str):"
    assert output["y"] == "y (float, optional, default 1.0):"
    assert output["z"] == "z (List[int], optional):"


def test_parse_parameters_without_annotations():
    output = parser._parse_parameters(Foo.method)

    assert output["a"] == "a (None):"
    assert output["b"] == "b (None):"


def test_parse_parameters_for_args_and_kwargs_values():
    output = parser._parse_parameters(Foo.static_method)

    assert output["*args"] == "*args (Any):"
    assert output["**kwargs"] == "**kwargs (Any):"


###############################################################################


@pytest.mark.parametrize("type,result", [
    ("<class 'str'>", "str"),
    ("<class 'int'>", "int"),
    ("<class 'list'>", "list"),
    ("<class 'requests.models.Response'>", "requests.models.Response"),
    ("<class 'tests.test_data.module.Foo'>", "tests.test_data.module.Foo")
])
def test_builtin_type_regex(type, result):
    assert BUILTIN_TYPE_REGEX.search(type).group(1) == result


@pytest.mark.parametrize("object_name,result", [
    (Foo.method, "List[str]"),
    (Foo.static_method, "str"),
    (function, "int"),
    (another_function, "Union[str, int]"),
    (_hidden_function, "tests.test_data.module.Foo")
])
def test_parse_return_annotation(object_name, result):
    assert parser._parse_return_annotation(object_name) == result


def test_parse_missing_return_annotation():
    assert parser._parse_return_annotation(Foo._protected) == "None"
