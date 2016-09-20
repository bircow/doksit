from doksit.utils.inspectors import get_repository_link


def test_get_url_to_github_repository():
    expectation = "https://github.com/nait-aul/doksit/blob/master/"
    assert get_repository_link() == expectation
