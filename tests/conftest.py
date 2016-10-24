import os

import pytest

from doksit.api import DoksitStyle
from doksit.models import Base


@pytest.fixture(scope="session")
def check_test_directory():
    """
    If a user run tests from project root directory, then change directory
    to 'tests' for successful running.

    Plus add blank directory "docs/" for the same reason, if it's missing.
    """
    if os.path.relpath(".", "..") != "tests" and "setup.py" in os.listdir():
        os.chdir("tests/")

        if "docs" not in os.listdir():
            os.mkdir("docs")


@pytest.fixture
def change_temporarily_directory():
    """
    For testing methods in non-git environment.
    """
    current_directory = os.getcwd()
    os.chdir("../..")

    yield

    os.chdir(current_directory)


@pytest.fixture(scope="session")
def documentation():
    """
    Generate sample documentation from test data.
    """
    doksit = DoksitStyle("test_data", "API")

    return doksit.get_api_documentation()


@pytest.fixture
def enable_alphabetical_order():
    with open(".doksit.yml", "w") as file:
        file.write("order: a-z")

    yield

    os.remove(".doksit.yml")


@pytest.fixture
def enable_reference_links():
    with open(".doksit.yml", "w") as file:
        file.write("links:\n  github: https://github.com")

    yield

    os.remove(".doksit.yml")


@pytest.fixture(scope="session")
def file_metadata():
    return Base.read_file("test_data/module.py")
