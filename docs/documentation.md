# Generating API documentation

Once again (if you haven't read Doksit's [README](https://github.com/nait-aul/doksit#doksit)), a command for generating the API documentation is:

```
$ doksit api  # or also
$ doksit api -p <package_name>
```

First command expects that `Doksit` is able to detect a Python package, where you have the codes. But if it raises a `PackageError`, then you should use the second command.

For both commands, you should run them in the root of your repository (next to `setup.py`, `.gitignore` etc.), otherwise links in the API documentation to the source codes will be broken (missing some paths).

## The process of generating the API

1. Doksit will be browse the given Python package (directory) and find all the Python modules

    - files like `__init__.py`, `__main__.py`, `<name>.pyx` are ignored
    - direction is TOP -> DOWN + alphabetical order

        - in the other words, first is scanned top level content of that directory and then its subdirectories etc.

    - example of intern file paths:

        ```
        <package>/api.py
        <package>/exceptions.py
        <package>/models.py
        <package>/<subpackage_a>/<name>.py
        <package>/<subpackage_b>/<name>.py
        ...
        ```

2. Each file path is scanned for getting class / method / function names exactly in the order as they are defined

    - private / protected / magic methods (functions) are excluded, except the constructor `__init__`
    - this feature may be switched in a config file to A-Z order (first classes with methods, then functions)

3. Doksit is looking for object docstrings via standard library `inspect` and if they exists, content is parsed to Markdown format

4. the API documentation output is showed to a user if he / she didn't use standard Unix redirection to a file.

## Modifying the documentation output

### Title

Default title is `API Reference`. 

If you want different title, you may choose between:

1. using `-t` / `--title` option

    ```
    $ doksit api -title "API"
    ```

2. add title to a config file `.doksit.yml`

    ```
    title: My Own API Title
    ```

### Order of classes / functions

Default is the order as they are defined in a module:

```markdown
### class C
### class A
### class B
### function Foo
### function Bar
```

If you want to sort them A-Z, then write to the config file:

```
order: a-z  # or
order: alphabetically
```

### Choose, which objects will be in the API documentation

In the module docstrings you use template variables with references to objects, which will be in the documentation:

```python
"""
This is a module docstring.

{{ class_name }}
{{ function_name }}
"""
```

There is not support for methods, if you don't want some to be visible, change them to private / protected variant.

**Notes:**

1. if you write bad class / function name, don't worry, you will be warned
2. don't forget to use spaces between `{{` and `}}`

### Choose, which modules will be in the API documentation

If you don't want the documentation for all the Python modules, create a `_api.md` file in the `docs/` folder like:

```
docs/
    _api.md
package_name/
    subpackage/
        highlighters.py
    api.py
    exceptions.py
    models.py
tests/
.gitignore
...
```

and write inside:

```markdown
# Own API Title

Your abstract.

{{ api.py }}
{{ subpackage/highlighters.py }}
```

**Warning**: Do NOT write the package name (parent directory). It will be automatically inserted internally and finally replaced with the module documentation.

Again, if you write invalid file path, you will be warned.

## Changing API documentation view

In default, pure Markdown API documentation will be showed to you via `less` program (if no redirection is used).

But if you want to read it in a bit nice way, you have 2 options:

1. use `--smooth` flag

    - some text will be bold (mainly headings and docstrings headers)
    - shortened file path to a module / object (no absolute HTTP URL)

2. use `--colored` flag

    - smooth variant + colored headings, docstring headers, inline and block codes, foreground and background color for the rest of text

**Warning:** Colors may look differently in different operating systems (eg. Ubuntu vs Mac OS X)


