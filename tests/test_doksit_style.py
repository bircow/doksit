import copy
import os

import pytest

from doksit.api import DoksitStyle
from doksit.models import Base

from tests.test_data import module

doksit = DoksitStyle("test_data", "API")


def test_get_api_documentation():
    api_doc = doksit.get_api_documentation()

    assert "# API" in api_doc
    assert "test_data.module" in api_doc
    assert "test_data.subpackage.module" in api_doc
    assert "test_data.subpackage.subpackage.module" in api_doc
    assert "test_data.blank" not in api_doc


def test_get_api_documentation_respecting_template():
    template_text = (
        "# API\n\n"
        "This is a paragraph.\n\n"
        "{{ module.py }}"
    )

    with open("docs/_api.md", "w") as file:
        file.write(template_text)

    api_doc = doksit.get_api_documentation()

    assert "{{ module.py }}" not in api_doc
    assert "## test_data.module" in api_doc

    os.remove("docs/_api.md")


###############################################################################


def test_get_documentation(file_metadata):
    doc = doksit._get_documentation(file_metadata)

    assert doc
    assert "## test_data.module" in doc


@pytest.mark.usefixtures("enable_alphabetical_order")
def test_get_documentation_in_alphabetical_order():
    file_metadata = Base.read_file("test_data/module.py")
    doc = doksit._get_documentation(file_metadata)

    assert doc.index("class Bar") < doc.index("class Foo")
    assert doc.index("property variable") < doc.index("method method")
    assert doc.index("function another_function") \
        < doc.index("function function")


def test_get_documentation_for_blank_file():
    file_metadata = Base.read_file("test_data/blank.py")
    doc = doksit._get_documentation(file_metadata)

    assert doc is None


###############################################################################


def test_alphabetically():
    assert not doksit.alphabetically


@pytest.mark.usefixtures("enable_alphabetical_order")
def test_alphabetically_with_config_file():
    assert doksit.alphabetically


###############################################################################


def test_order_classes(file_metadata):
    _, classes, _ = file_metadata
    classes_copy = copy.deepcopy(classes)  # Important, otherwise tests fail.
    ordered_classes = doksit._order_classes(module, classes_copy)
    list_classes = list(ordered_classes.items())

    assert list_classes[0][0] == "Bar"
    assert list_classes[1][0] == "Foo"
    assert list_classes[1][1][0] == "__init__"
    assert list_classes[1][1][1] == "variable"
    assert list_classes[1][1][2] == "method"
    assert list_classes[1][1][3] == "static_method"


###############################################################################


def test_get_module_documentation():
    module_doc = doksit.get_module_documentation(module)

    assert module_doc
    assert "This is a module docstring, right?" in module_doc


###############################################################################


def test_get_class_documentation(file_metadata):
    _, classes, _ = file_metadata
    doc = doksit.get_class_documentation(module, classes)

    assert "### class Foo" in doc
    assert "### class Bar" in doc


###############################################################################


def test_get_method_documentation_for_constructor(file_metadata):
    _, classes, _ = file_metadata
    method = classes["Foo"][0]

    assert method == "__init__"

    class_object = getattr(module, "Foo")
    method_object = getattr(class_object, "__init__")

    doc = doksit.get_method_documentation(module, method_object, "__init__")

    assert doc
    assert "#### constructor" in doc


def test_get_method_documentation_for_property(file_metadata):
    _, classes, _ = file_metadata

    class_object = getattr(module, "Foo")
    method_object = getattr(class_object, "variable")

    doc = doksit.get_method_documentation(module, method_object, "variable")

    assert doc
    assert "#### property variable" in doc


def test_get_method_documentation_for_method(file_metadata):
    _, classes, _ = file_metadata

    class_object = getattr(module, "Foo")
    method_object = getattr(class_object, "method")

    doc = doksit.get_method_documentation(module, method_object, "method")

    assert doc
    assert "#### method method" in doc


###############################################################################


def test_get_function_documentation(file_metadata):
    _, _, functions = file_metadata
    doc = doksit.get_function_documentation(module, functions)

    assert doc
    assert "### function function" in doc


###############################################################################


def test_get_markdowned_docstring_for_module():
    docstring = doksit.get_markdowned_docstring(module)

    example = (
        "Example:\n\n"
        "```python\n"
        ">>> print('Hello World!')\n"
        "Hello World!\n"
        "```"
    )

    assert example in docstring


def test_get_markdowned_docstring_for_class_foo():
    docstring = doksit.get_markdowned_docstring(module.Foo)

    note = (
        "**Note:**\n"
        "    This is a note."
    )
    attributes = (
        "**Attributes:**\n\n"
        "- foo (str):\n"
        "    - Foo is the attribute.\n"
        "- bar (int):\n"
        "    - Bar is another\n"
        "      attribute."
    )
    todo = (
        "**Todo:**\n\n"
        "- [ ] one thing\n"
        "- [ ] two\n"
        "      things"
    )

    assert docstring
    assert note in docstring
    assert attributes in docstring
    assert todo in docstring


def test_get_markdowned_docstring_for_foo_constructor():
    docstring = doksit.get_markdowned_docstring(module.Foo.__init__)

    arguments = (
        "**Arguments:**\n\n"
        "- x (str):\n"
        "    - Description of\n"
        "      'x'.\n"
        "- y (float, optional, default 1.0):\n"
        "    - Description of 'y'.\n"
        "- z (List[int], optional):\n"
        "    - Description of 'z'."
    )
    raises = (
        "**Raises:**\n\n"
        "- AssertionError:\n"
        "    - Assertion failed.\n"
        "- TypeError:\n"
        "    - TypeError\n"
        "      description.\n"
        "- ValueError:\n"
        "    1. Invalid argument for\n"
        "       'x'.\n"
        "    2. Invalid argument for 'y'.\n"
        "    3. Invalid argument for 'z'."
    )

    assert arguments in docstring
    assert raises in docstring


def test_get_markdowned_docstring_for_method_foo_method():
    docstring = doksit.get_markdowned_docstring(module.Foo.method)

    warning = (
        "**Warning:**\n"
        "    This is a warning."
    )
    returns = (
        "**Returns:**\n\n"
        "- List[str]:\n"
        "    - True."
    )
    example = (
        "Example:\n\n"
        "```markdown\n"
        "# Heading\n"
        "```"
    )

    assert warning in docstring
    assert returns in docstring
    assert example in docstring


def test_get_markdowned_docstring_for_function_function():
    docstring = doksit.get_markdowned_docstring(module.function)

    arguments = (
        "**Arguments:**\n\n"
        "- n (None):\n"
        "    - Description of 'n'."
    )
    yields = (
        "**Yields:**\n\n"
        "- int:\n"
        "    - Integer."
    )
    example = (
        "Example:\n\n"
        "```python\n"
        "# This is an example code.\n"
        "\n"
        "# This part is after line break.\n"
        "```"
    )

    assert arguments in docstring
    assert yields in docstring
    assert example in docstring
