import os
import subprocess
import re
import tempfile

import pytest

import yaml

from doksit.cli import api
from doksit.models import (
    Base, BRANCH_NAME_REGEX, CLASS_REGEX, FUNCTION_REGEX, METHOD_REGEX,
    REPOSITORY_URL_REGEX, STATIC_METHOD_REGEX, VARIABLE_REGEX
)

from tests.test_data import module
from tests.test_data.module import Foo

base = Base()


def test_get_api_documentation():
    assert not base.get_api_documentation()


###############################################################################


def test_valid_config_load():
    with open(".doksit.yml", "w") as file:
        file.write("docstring: doksit")

    assert base.config == {"docstring": "doksit"}

    os.remove(".doksit.yml")


def test_invalid_config_load():
    with open(".doksit.yml", "w") as file:
        file.write("blabla: blabla:")

    with pytest.raises(yaml.YAMLError):
        base.config

    os.remove(".doksit.yml")


def test_config():
    assert not base.config


###############################################################################


@pytest.mark.parametrize("data", [
    "* dev\n",
    "  master\n* dev\n  nait"
])
def test_branch_name_regex(data):
    assert BRANCH_NAME_REGEX.search(data).group(1) == "dev"


def test_current_branch():
    assert base.current_branch


@pytest.mark.usefixtures("change_temporarily_directory")
def test_not_found_current_branch():
    assert not base.current_branch


###############################################################################


def test_has_template():
    assert not base.has_template

    with open("docs/_api.md", "w") as file:
        file.write("blabla")

    assert base.has_template

    os.remove("docs/_api.md")


###############################################################################


def test_repository_prefix():
    prefix = base.repository_prefix

    assert "https://github.com/nait-aul/doksit/blob/" in prefix
    assert base.current_branch in prefix


@pytest.mark.usefixtures("change_temporarily_directory")
def test_not_found_repository_prefix():
    assert not base.repository_prefix


###############################################################################


def test_repository_url_regex():
    data = (
        "origin\thttps://github.com/nait-aul/doksit (fetch)\n"
        "origin\thttps://github.com/nait-aul/doksit (push)\n"
    )
    expected_output = "https://github.com/nait-aul/doksit"

    assert REPOSITORY_URL_REGEX.search(data).group(1) == expected_output


def test_repository_url():
    assert "https://github.com/nait-aul/doksit" in base.repository_url


@pytest.mark.usefixtures("change_temporarily_directory")
def test_not_found_repository_url():
    assert not base.repository_url


def test_clone_repository_and_get_repository_url():
    current_directory = os.getcwd()
    has_git = True

    with tempfile.TemporaryDirectory() as temporary_directory:
        os.chdir(temporary_directory)

        try:
            repository = "https://github.com/nait-aul/doksit.git"
            subprocess.call(["git", "clone", repository, "."])
            repository_url = base.repository_url

        except subprocess.CalledProcessError:
            has_git = False

        os.chdir(current_directory)

    if has_git:
        assert repository_url
        assert "nait-aul/doksit.git/blob/" not in repository_url


###############################################################################


def test_get_line_numbers():
    assert base.get_line_numbers(Foo) == "#L12-L113"


def test_get_invalid_line_numbers():
    """
    For buggy CLI commands (functions) using the `click` package.
    """
    assert base.get_line_numbers(api) == "#"


###############################################################################


@pytest.mark.parametrize("pattern", [
    "https://github.com/nait-aul/doksit/blob/",
    base.current_branch,
    "tests/test_data/module.py"
])
def test_get_source_code_url_for_module(pattern):
    url = base.get_source_code_url(module)

    assert pattern in url


@pytest.mark.parametrize("pattern", [
    "[source](",
    "https://github.com/nait-aul/doksit/blob/",
    base.current_branch,
    "tests/test_data/module.py#L12-L113",
    ")"
])
def test_get_source_code_url_for_object(pattern):
    url = base.get_source_code_url(module, Foo)

    assert pattern in url


@pytest.mark.usefixtures("change_temporarily_directory")
def test_get_blank_source_code_url():
    assert not base.get_source_code_url(module)


###############################################################################


def test_find_files():
    expected_file_paths = [
        "test_data/blank.py",
        "test_data/module.py",
        "test_data/subpackage/module.py",
        "test_data/subpackage/subpackage/module.py",
    ]

    assert base.find_files("test_data") == expected_file_paths


@pytest.mark.parametrize("text", [
    "{{ module.py }}",
    "{{module.py}}"
])
def test_variable_regex(text):
    assert VARIABLE_REGEX.search(text).group(1) == "module.py"


def test_find_files_in_template():
    content = """# API Reference

    {{ module.py }}
    {{ subpackage/module.py }}
    """

    with open("docs/_api.md", "w") as file:
        file.write(content)

    expected_file_paths = [
        "test_data/module.py",
        "test_data/subpackage/module.py"
    ]

    assert base.find_files("test_data") == expected_file_paths

    os.remove("docs/_api.md")


def test_find_invalid_file_paths_in_template():
    content = """# API Reference

    {{ module.py }}
    {{ subpackage/blablabla.py }}
    """

    with open("docs/_api.md", "w") as file:
        file.write(content)

    with pytest.raises(ValueError):
        base.find_files("test_data")

    os.remove("docs/_api.md")


###############################################################################


@pytest.mark.parametrize("line", [
    "class Foo:",
    "class Foo(object):",
    "class Foo(Bar, object):",
])
def test_regex_for_classes(line):
    assert CLASS_REGEX.search(line).group(1) == "Foo"


@pytest.mark.parametrize("line", [
    "    def sample_method(cls):",
    "    def sample_method(cls, arg1, arg2, ...):",
    "    def sample_method(self):",
    "    def sample_method(self, arg1, arg2, ...):"
])
def test_regex_for_methods(line):
    assert METHOD_REGEX.search(line).group(1) == "sample_method"


@pytest.mark.parametrize("line", [
    "    def static_method():",
    "    def static_method(x, y)"
])
def test_regex_for_static_methods(line):
    assert STATIC_METHOD_REGEX.search(line).group(1) == "static_method"


@pytest.mark.parametrize("line", [
    "def function_name():",
    "def function_name(arg1, arg2, ...):"
])
def test_regex_for_functions(line):
    assert FUNCTION_REGEX.search(line).group(1) == "function_name"


def test_read_file():
    """
    The file is located here in the 'test_data/module.py'.
    Expected result is:
        (
            "test_data/module.py",
            OrderedDict([
                ('Foo', ['__init__', 'method', 'static_method']),
                ('Bar', [])
            ]),
            ['function', 'another_function']
        )
    """
    result = base.read_file("test_data/module.py")

    assert result[0] == "test_data/module.py"
    assert list(result[1].keys()) == ["Foo", "Bar"]
    assert result[1]["Foo"] == [
        "__init__", "method", "static_method", "variable"
    ]
    assert result[1]["Bar"] == []
    assert result[2] == ["function", "another_function"]
