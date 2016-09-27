import inspect

from doksit.api import _method_documentation

from tests.test_data import module


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
    method_url = \
        "https://github.com/nait-aul/doksit/blob/master/" \
        "tests/test_data/module.py#L34-L59"

    expected_output_draft = """
    #### method \_\_init\_\_

    [source]({method_url})

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
    """.format(method_url=method_url)

    expected_output = inspect.cleandoc(expected_output_draft)
    assert expected_output in method_documentation
