import pytest

from doksit.api import CLASS_REGEX, METHOD_REGEX, FUNCTION_REGEX, read_file


@pytest.mark.parametrize("line", [
    "class Foo:",
    "class Foo(object):",
    "class Foo(Bar, object):",
])
def test_regex_for_classes(line):
    assert CLASS_REGEX.search(line).group(1) == "Foo"


@pytest.mark.parametrize("line", [
    "    def sample_method(cls):",
    "    def sample_method(cls, arg1, arg2, ...):",
    "    def sample_method(self):",
    "    def sample_method(self, arg1, arg2, ...):"
])
def test_regex_for_methods(line):
    assert METHOD_REGEX.search(line).group(1) == "sample_method"


@pytest.mark.parametrize("line", [
    "def function_name():",
    "def function_name(arg1, arg2, ...):"
])
def test_regex_for_functions(line):
    assert FUNCTION_REGEX.search(line).group(1) == "function_name"


def test_read_sample_file():
    """
    The file is located here in the 'test_data/module.py'.

    Expected result is:

        (
            "test_data/module.py",
            OrderedDict([('Foo', ['__init__', 'method']), ('Bar', [])]),
            ['function', 'another_function']
        )
    """
    result = read_file("test_data/module.py")

    assert result[0] == "test_data/module.py"
    assert list(result[1].keys()) == ["Foo", "Bar"]
    assert result[1]["Foo"] == ["__init__", "method"]
    assert result[1]["Bar"] == []
    assert result[2] == ["function", "another_function"]
