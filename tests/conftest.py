import os

import pytest


@pytest.fixture(scope="session")
def check_test_directory():
    """
    If a user run tests from project root directory, then change directory
    to 'tests' for successful running.

    Plus add blank directory "docs/" for the same reason.
    """
    if os.path.relpath(".", "..") != "tests" and "setup.py" in os.listdir():
        os.chdir("tests/")

        if "docs" not in os.listdir():
            os.mkdir("docs")


@pytest.fixture
def change_temporarily_directory():
    current_directory = os.getcwd()
    os.chdir("../..")

    yield

    os.chdir(current_directory)
