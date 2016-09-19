import os

import pytest


@pytest.fixture(scope="session")
def check_directory():
    """
    Check if a user is inside the 'tests' directory or not. 

    If not, change the directory to it for successful running tests.
    """
    if os.path.relpath(".", "..") != "tests":
        os.chdir("tests/")
