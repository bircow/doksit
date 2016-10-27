import os

import pytest

from doksit.exceptions import MissingTocFile
from doksit.helpers import check_for_toc_file


def test_check_for_toc_file():
    with open("docs/_toc.md", "w") as file:
        file.write("# Blabla")

    assert check_for_toc_file(False) is None

    os.remove("docs/_toc.md")


def test_check_for_toc_file_with_raised_error():
    with pytest.raises(MissingTocFile) as error:
        check_for_toc_file(False)

    assert str(error.value) == "Cannot find the `_toc.md` file."
