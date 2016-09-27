import inspect

from doksit.api import _functions_documentation, read_file

from tests.test_data import module


def test_functions_documentation():
    """
    Function 'another_function' has following docstring:

        This is a brief oneline description.
    """
    file_metadata = read_file("test_data/module.py")
    functions = file_metadata[2]

    functions_documentation = _functions_documentation(module, functions)
    function_another_function_url = \
        "https://github.com/nait-aul/doksit/blob/master/" \
        "tests/test_data/module.py#L129-L131"

    expected_output_draft = """
    ### function another_function

    [source]({function_another_function_url})

    This is a brief oneline description.
    """.format(function_another_function_url=function_another_function_url)

    expected_output = inspect.cleandoc(expected_output_draft)
    assert expected_output in functions_documentation
