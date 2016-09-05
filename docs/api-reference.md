# API Reference

## doksit.main

### function doksit.main.find_files

Get ordered relative paths for all python files in the given directory and
subdirectories.

These relative paths will be inserted into global variable 'file_paths'.

Example:

```python
["package/module.py", "package/subpackage/module.py"]
```

Files in '\_\_pycache\_\_' directories are excluded. The same goes for
'\_\_init__.py' and '\_\_main\_\_.py' files.

**Arguments:**

- directory_path (str):
    - Relative directory path.

### function doksit.main.read_file

Get names for classes and methods inside and functions if there are any.

Unlike Pydoc the Doksit cares about order of objects specified above in the
given file + omits magic methods except the '\_\_init\_\_'.

**Arguments:**

- file_path (str):
    - Relative file path.

**Returns:**
    3-tuple, where first item is relative file path, second is ordered
    dict with class names and methods and third is list of function names.

Example:

```python
("package.module", MyOrderedDict({"Foo": ["__init__", "method_name"]),
["function_name"])
```

### function doksit.main.get_documentation

Create documentation for objects from the given file (module), if there
are any.

In other words, if the file is empty then documentation won't be created
for it.

The documentation will be inserted into global variable 'output' which
contains entire documentation for the given package.

**Arguments:**

- file_metadata (tuple):
    - Returned data from the 'read_file' function from the 'doksit.main'.

**Returns:**
    Updated global variable 'output'. It's needed for successful
    unittest of this function.

### function doksit.main.main

Create documentation for the given Python package and print it.

## doksit.utils.data_types

### class doksit.utils.data_types.MyOrderedDict

Upgraded 'OrderedDict' from module 'collections'.

#### method last

Get the name of the last inserted key.

## doksit.utils.parser

### function doksit.utils.parser.parse_parameters

Parse the given parameters (come from a method / function) to readable
format.

This function is used internally by 'markdown_docstring' method from
'doksit.utils.parser' for markdowning a 'Arguments' section in a docstring.

**Arguments:**

- parameters (collections.OrderedDict):
    - Parameters of method / function with annotations and default
values if any.

**Returns:**
    Dictionary of parameters names with parsed string for documentation.

Example:

```python
{"foo": "foo (str):", "bar": "bar (int, optional, default 0):"}
```

### function doksit.utils.parser.markdown_docstring

Read the given docstring and convert it to Markdown.

This function is used internally by 'get_documentation' from the
'doksit.main'.

**Arguments:**

- docstring (str):
    - Docstring of class / method / function.
- parameters (collections.OrderedDict, optional, default OrderedDict()):
    - Parameters of method / function which will be passed to the
'parse_parameters' function from the 'doksit.utils.parser'.

**Returns:**
    Docstring in Markdown format.

Example:

```python
This is a brif description of object.

This is a long paragraph.

**Arguments**:

- foo (str):
    - Foo description.
- bar (int, optional, 1):
    - Bar description.

**Returns:**
    True if something.
```
