import pytest

from doksit.utils.parsers import BUILTIN_TYPE_REGEX, parse_return_annotation

from tests.test_data.module import Foo, function, another_function


@pytest.mark.parametrize("type,result", [
    ("<class 'str'>", "str"),
    ("<class 'int'>", "int"),
    ("<class 'list'>", "list")
])
def test_builtin_type_regex(type, result):
    assert BUILTIN_TYPE_REGEX.search(type).group(1) == result


@pytest.mark.parametrize("object_name,result", [
    (Foo.method, "List[str]"),
    (function, "int"),
    (another_function, "Union[str, int]")
])
def test_parse_return_annotation(object_name, result):
    assert parse_return_annotation(object_name) == result


