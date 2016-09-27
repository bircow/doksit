import inspect

from doksit.api import _module_documentation

from tests.test_data import module


def test_module_documentation():
    """
    Module 'module' has following docstring:

        This is a module docstring, right?

        Example:
            >>> print("Hello World!)
            Hello World!
    """
    module_documentation = _module_documentation(module)
    module_url = \
        "https://github.com/nait-aul/doksit/blob/master/" \
        "tests/test_data/module.py"

    expected_output_draft = """
    ## tests.test_data.module

    [source]({module_url})

    This is a module docstring, right?

    Example:

    ```python
    >>> print("Hello World!)
    Hello World!
    ```
    """.format(module_url=module_url)

    expected_output = inspect.cleandoc(expected_output_draft)
    assert expected_output == module_documentation
