import inspect
import sys

from doksit.api import (
    read_file, _module_documentation, _classes_documentation,
    _method_documentation, _functions_documentation, get_documentation)

from tests.test_data import module

# IMPORTANT:
#
# Add current directory to the Python sys path, othwerise this test fails.

sys.path.append(".")


def test_module_documentation():
    """
    Module 'module' has following docstring:

        This is a module docstring, right?

        Example:
            >>> print("Hello World!)
            Hello World!
    """
    module_documentation = _module_documentation(module)

    expected_output_draft = """
    This is a module docstring, right?

    Example:

    ```python
    >>> print("Hello World!)
    Hello World!
    ```
    """
    expected_output = inspect.cleandoc(expected_output_draft)

    assert "## tests.test_data.module" in module_documentation
    assert "tests/test_data/module.py" in module_documentation
    assert expected_output in module_documentation


def test_classes_documentation():
    """
    Class 'Foo' has following docstring:

        This is a brief description.

        This is a long description.

        Note:
            This is a note.

        Attributes:
            foo (str):
                Foo is the attribute.
            bar (int):
                Bar is another
                attribute.

        Todo:
            - one thing
            - two
                things
    """
    file_metadata = read_file("test_data/module.py")
    classes = file_metadata[1]
    classes_documentation = _classes_documentation(module, classes)

    expected_output_draft = """
    This is a brief description.

    This is a long description.

    **Note:**
        This is a note.

    **Attributes:**

    - foo (str):
        - Foo is the attribute.
    - bar (int):
        - Bar is another
          attribute.

    **Todo:**

    - [ ] one thing
    - [ ] two
          things
    """
    expected_output = inspect.cleandoc(expected_output_draft)

    assert "### class Foo" in classes_documentation
    assert "tests/test_data/module.py#L12-L106" in classes_documentation
    assert expected_output in classes_documentation


def test_method_documentation():
    """
    Method 'Foo.__init__' has following docstring:

        This is a brief description.

        Arguments:
            x:
                Description of
                'x'.
            y:
                Description of 'y'.
            z:
                Description of 'z'.

        Raises:
            AssertionError:
                Assertion failed.
            TypeError:
                TypeError
                description.
            ValueError:
                1. Invalid argument for
                    'x'.
                2. Invalid argument for 'y'.
                3. Invalid argument for 'z'.
    """
    method_documentation = _method_documentation(module, module.Foo.__init__)

    expected_output_draft = """
    This is a brief description.

    **Arguments:**

    - x (str):
        - Description of
          'x'.
    - y (float, optional, default 1.0):
        - Description of 'y'.
    - z (List[int], optional, default []):
        - Description of 'z'.

    **Raises:**

    - AssertionError:
        - Assertion failed.
    - TypeError:
        - TypeError
          description.
    - ValueError:
        1. Invalid argument for
           'x'.
        2. Invalid argument for 'y'.
        3. Invalid argument for 'z'.
    """
    expected_output = inspect.cleandoc(expected_output_draft)

    assert "#### method \_\_init\_\_" in method_documentation
    assert "tests/test_data/module.py#L34-L59" in method_documentation
    assert expected_output in method_documentation


def test_functions_documentation():
    """
    Function 'another_function' has following docstring:

        This is a brief oneline description.
    """
    file_metadata = read_file("test_data/module.py")
    functions = file_metadata[2]
    functions_documentation = _functions_documentation(module, functions)

    expected_output_draft = """This is a brief oneline description."""
    expected_output = inspect.cleandoc(expected_output_draft)

    assert "### function another_function" in functions_documentation
    assert "tests/test_data/module.py#L134-L136" in functions_documentation
    assert expected_output in functions_documentation


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
    assert "https://github.com/nait-aul/doksit" in file_documentation
    assert "test_data/module.py#L12-L106" in file_documentation
    assert "method _protected" not in file_documentation
    assert "method __private" not in file_documentation
    assert "method __magic__" not in file_documentation
    assert "function _hidden_function" not in file_documentation
