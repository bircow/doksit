import pytest

from doksit.main import read_file, class_regex, method_regex, function_regex


@pytest.mark.parametrize("line", [
    "class Foo:",
    "class Foo(object):",
    "class Foo(Bar, object):",
])
def test_regex_for_classes(line):
    assert class_regex.search(line).group(1) == "Foo"


@pytest.mark.parametrize("line", [
    "    def sample_method(cls):",
    "    def sample_method(cls, arg1, arg2, ...):",
    "    def sample_method(self):",
    "    def sample_method(self, arg1, arg2, ...):"
])
def test_regex_for_methods(line):
    assert method_regex.search(line).group(1) == "sample_method"


@pytest.mark.parametrize("line", [
    "def function_name():",
    "def function_name(arg1, arg2, ...):"
])
def test_regex_for_functions(line):
    assert function_regex.search(line).group(1) \
        == "function_name"


def test_read_sample_file_from_sample_package():
    """    
    The file is located here in 'test_data/module.py'.

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
    assert not result[1]["Bar"]
    assert result[2] == ["function", "another_function"]
