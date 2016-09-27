import sys

from doksit.api import get_documentation, read_file

# IMPORTANT:
#
# Add current directory to the Python sys path, othwerise this test fails.

sys.path.append(".")


def test_get_documentation_for_sample_file():
    """
    Sample file (module) is 'test_data.module'.
    """
    file_metadata = read_file("test_data/module.py")
    file_documentation = get_documentation(file_metadata)

    assert "test_data.module" in file_documentation
    assert "This is a module docstring, right?" in file_documentation
    assert "class Foo" in file_documentation
    assert "method method" in file_documentation
    assert "function another_function" in file_documentation

    # NOTE:
    #
    # Below is invalid URL because missing parent folder 'tests' in it
    # (test is run inside that folder), but result is expected (right).

    assert "https://github.com/nait-aul/doksit/blob/master/" \
        "test_data/module.py#L12-L101" in file_documentation

    assert "method _protected" not in file_documentation
    assert "method __private" not in file_documentation
    assert "method __magic__" not in file_documentation
    assert "function _hidden_function" not in file_documentation
