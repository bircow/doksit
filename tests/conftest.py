import os

import pytest


@pytest.fixture(scope="session")
def check_directory():
    """
    If a user will run tests from project root directory, then change directory
    to 'tests' for successful running.
    """
    if os.path.relpath(".", "..") != "tests" and "setup.py" in os.listdir():
        os.chdir("tests/")
