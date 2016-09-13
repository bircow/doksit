import os

import pytest


@pytest.mark.usefixtures("check_directory")
def test_doksit_command():
    os.system("python -m doksit test_data/ > tmp.md")

    with open("tmp.md") as f:
        first_line = f.readline()

    assert first_line == "# API Reference\n"

    os.system("rm tmp.md")
