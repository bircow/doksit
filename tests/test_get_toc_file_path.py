import os
import os.path

from doksit.helpers import get_toc_file_path


def test_get_toc_file_path_in_docs_folder():
    path = os.path.join(os.getcwd(), "_toc.md")

    assert get_toc_file_path(True) == path


def test_get_toc_file_path_outside_docs_folder():
    path = os.path.join(os.getcwd(), "docs", "_toc.md")

    assert get_toc_file_path(False) == path
