import os
import os.path

import pytest

from doksit.models import Base
from doksit.toc import TableOfContents

toc = TableOfContents()


def test_create_bullet_point():
    heading = (1, "Super Heading", "#super-heading")
    url_path = "https://github.com/nait-aul/doksit/blob/master/docs/foo.md"
    bullet_point = toc.create_bullet_point(heading, url_path)

    assert bullet_point.startswith("- ")
    assert "[Super Heading]" in bullet_point
    assert url_path + heading[2] in bullet_point


@pytest.mark.parametrize("level,orig,encoded,bullet", [
    (2, "a", "a", "    - "),
    (3, "a", "a", "        - "),
    (4, "a", "a", "            - "),
    (5, "a", "a", "                - "),
    (6, "a", "a", "                    - "),
])
def test_create_bullet_point_for_other_heading_levels(level, orig, encoded,
                                                      bullet):
    heading = (level, orig, encoded)
    url_path = "https://github.com"
    bullet_point = toc.create_bullet_point(heading, url_path)

    assert bullet_point.startswith(bullet)


###############################################################################


def test_encode_heading():
    assert "#about-me" == toc.encode_heading("About Me")


###############################################################################


def test_find_headings():
    api_documentation_file = os.path.join(os.getcwd(), "docs", "example.md")
    result = toc.find_headings(api_documentation_file)

    assert (1, "F", "#f") in result
    assert (2, "Fo", "#fo") in result
    assert (3, "Foo", "#foo") in result
    assert (4, "Fooo", "#fooo") in result
    assert (5, "Foooo", "#foooo") in result
    assert (6, "Fooooo", "#fooooo") in result

    assert (1, "Fake title", "#fake-title") not in result
    assert (2, "Fake level heading", "#fake-level-heading") not in result


###############################################################################


def test_generate_file_toc():
    directory = os.path.join(os.getcwd(), "docs")
    file_path = "example.md"
    result = toc.generate_file_toc(directory, file_path)

    url = Base().repository_prefix + "docs/" + file_path

    assert "- [F](" + url + "#f" + ")" in result


###############################################################################


def test_generate_toc():
    with open("docs/_toc.md", "w") as file:
        file.write("# Title\n{{ example.md }}\n")

    result = toc.generate_toc(False)

    assert result is None

    with open("docs/README.md") as file:
        file_content = file.read()

    assert "# Title" in file_content
    assert "- [F]" in file_content

    os.remove("docs/README.md")
    os.remove("docs/_toc.md")


###############################################################################


def test_validate_file_path():
    directory = os.path.join(os.getcwd(), "docs")
    file_path = "api.md"
    result = toc.validate_file_path(directory, file_path)

    assert result == os.path.join(directory, file_path)


def test_validate_file_path_with_raised_error():
    directory = os.path.join(os.getcwd(), "docs")
    file_path = "blablabla.md"

    with pytest.raises(ValueError) as error:
        toc.validate_file_path(directory, file_path)

    error_message = (
        "Invalid file path '{{ blablabla.md }}' in the `docs/_toc.md`"
    )

    assert str(error.value) == error_message
