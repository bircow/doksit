import collections
import inspect

from doksit.utils.parsers import markdown_docstring

from tests.test_data.module import Foo, function, another_function


def test_markdown_class_docstring():
    """
    Sample class docstring from 'Foo' class:

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
    class_docstring = inspect.getdoc(Foo)
    markdowed_class_docstring = markdown_docstring(class_docstring)

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
    assert expected_output == markdowed_class_docstring


def test_markdown_method_docstring():
    """
    Sample method docstring from the 'Foo.__init__' method:

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

    Note:
        The 'Foo.__init__' method has parameters which are needed to get for
        the 'markdown_docstring' function.
    """
    method_parameters = inspect.signature(Foo.__init__).parameters
    method_parameters = collections.OrderedDict(method_parameters)

    method_docstring = inspect.getdoc(Foo.__init__)
    markdowned_method_docstring = \
        markdown_docstring(method_docstring, method_parameters)

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
    assert expected_output == markdowned_method_docstring


def test_markdown_another_method_docstring():
    """
    Sample method docstring from the 'Foo.method' method:

        This is a brief description.

        This is a long description.

        Warning:
            This is a warning.

        Returns:
            True.
    """
    method_docstring = inspect.getdoc(Foo.method)
    markdowned_method_docstring = markdown_docstring(method_docstring)

    expected_output_draft = """
    This is a brief description.

    This is a long description.

    **Warning:**
        This is a warning.

    **Returns:**
        True.
    """

    expected_output = inspect.cleandoc(expected_output_draft)
    assert expected_output == markdowned_method_docstring


def test_markdown_function_docstring():
    """
    Sample function docstring from the 'function' function:

        This is a brief description.

        This is a long description.

        Arguments:
            n:
                Description of 'n'.

        Yields:
            Integer.

        Example:
            This is an example code.

            This part is after line break.

    Note:
        The 'function' function has parameters which are needed to get for the
        'markdown_docstring' function.
    """
    function_parameters = inspect.signature(function).parameters
    function_parameters = collections.OrderedDict(function_parameters)

    function_docstring = inspect.getdoc(function)
    markdowned_function_docstring = \
        markdown_docstring(function_docstring, function_parameters)

    expected_output_draft = """
    This is a brief description.

    This is a long description.

    **Arguments:**

    - n:
        - Description of 'n'.

    **Yields:**
        Integer.

    Example:

    ```python
    This is an example code.

    This part is after line break.
    ```
    """

    expected_output = inspect.cleandoc(expected_output_draft)
    assert expected_output == markdowned_function_docstring


def test_markdown_another_function_docstring():
    """
    Sample function docstring from the 'another_function' function:

        This is a brief description.
    """
    function_docstring = inspect.getdoc(another_function)
    markdowned_function_docstring = markdown_docstring(function_docstring)

    expected_output_draft = """
    This is a brief description.
    """

    expected_output = inspect.cleandoc(expected_output_draft)
    assert expected_output == markdowned_function_docstring
