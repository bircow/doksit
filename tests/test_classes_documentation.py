import inspect

from doksit.api import _classes_documentation, read_file

from tests.test_data import module


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
    class_foo_url = \
        "https://github.com/nait-aul/doksit/blob/master/" \
        "tests/test_data/module.py#L12-L101"

    expected_output_draft = """
    ### class Foo

    [source]({class_foo_url})

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
    """.format(class_foo_url=class_foo_url)

    expected_output = inspect.cleandoc(expected_output_draft)
    assert expected_output in classes_documentation
