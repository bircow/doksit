from doksit.utils.inspectors import (
    REPOSITORY_URL_REGEX, BRANCH_NAME_REGEX, _get_repository_url,
    _get_line_numbers, get_source_code_url)

from tests.test_data import module
from tests.test_data.module import Foo, function


def test_repository_url_regex():
    data = "origin\thttps://github.com/nait-aul/doksit (fetch)\n" \
        "origin\thttps://github.com/nait-aul/doksit (push)\n"
    expected_output = "https://github.com/nait-aul/doksit"

    assert REPOSITORY_URL_REGEX.search(data).group(1) == expected_output


def test_branch_name_regex():
    data = "  master\n* dev\n  nait"

    assert BRANCH_NAME_REGEX.search(data).group(1) == "dev"


def test_get_url_to_github_repository():
    assert "doksit" in _get_repository_url()


def test_get_object_line_numbers():
    assert _get_line_numbers(Foo) == "#L12-L106"
    assert _get_line_numbers(function) == "#L113-L131"


def test_get_source_code_url():
    assert "tests/test_data/module.py" in get_source_code_url(module)
    assert "module.py#L12-L106" in get_source_code_url(module, module.Foo)
