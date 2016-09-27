from doksit.utils.inspectors import (
    REPOSITORY_URL_REGEX, BRANCH_NAME_REGEX, _get_repository_url)


def test_repository_url_regex():
    data = "origin\thttps://github.com/nait-aul/doksit (fetch)\n" \
        "origin\thttps://github.com/nait-aul/doksit (push)\n"
    expected_output = "https://github.com/nait-aul/doksit"

    assert REPOSITORY_URL_REGEX.search(data).group(1) == expected_output


def test_branch_name_regex():
    data = "  master\n* dev\n  nait"

    assert BRANCH_NAME_REGEX.search(data).group(1) == "dev"


def test_get_url_to_github_repository():
    assert "doksit/" in _get_repository_url()
