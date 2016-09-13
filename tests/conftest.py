import os

import pytest


@pytest.fixture(scope="session")
def check_directory():
    """
    Check if a user is inside 'tests' or not. If not, change the directory in
    subprocess
    """
    if os.path.relpath(".", "..") != "tests":
        os.chdir("tests/")
