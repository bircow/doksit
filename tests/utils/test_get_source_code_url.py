from doksit.utils.inspectors import get_source_code_url

from tests.test_data import module


def test_get_source_code_url():
    assert "tests/test_data/module.py" in get_source_code_url(module)
    assert "module.py#L12-L101" in get_source_code_url(module, module.Foo)
