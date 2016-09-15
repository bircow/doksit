from doksit.utils.inspectors import get_line_numbers

from tests.test_data.module import Foo, function


def test_get_object_line_numbers():
    assert get_line_numbers(Foo) == "#L12-L91"
    assert get_line_numbers(function) == "#L98-L116"
