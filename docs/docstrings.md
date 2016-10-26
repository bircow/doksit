# About docstrings

For those who have used [Napoleon](https://pypi.python.org/pypi/sphinxcontrib-napoleon/) before, then you may skip the next section about writing docstrings and go directly to [Coming from Napoleon](#coming-from-napoleon) section.

## Never used Google Docstring Style with Napoleon

If you are completely new to Python docstrings styling / formatting or even have never ever written a docstring, then pay attention.

### Why you should care about docstring style / format?

1. enough information about a given object without reading its code
   - brief info about object's behaviour
   - if you may pass any arguments and how they should look like
   - if an error may be raised
   - what may the object return / yield as a value
   - an example of using the object etc. 
2. your teammates will thank you a lot
3. optional, writing first docstrings before codes may calm your mind and you will know how to exactly write the algorithms

### Where to write docstrings

Docstrings may be written for:

1. module (at the start of a file)

    ```python
    """
    This is a module docstring.
    """

    from x import y
    ```

2. class

    ```python
    class Foo:
        """
        This is a class docstring.
        """
        pass
    ```

3. method / function

    ```python
    def bar():
        """
        This is a function docstring.
        """
        pass
    ```

### Formatting docstrings

Below is a simple example with used type hints and `typing` module (built-in since Python 3.5, otherwise must be downloaded via `pip`):

```python
"""
This module contains ... / Here are defined ... / any other module description of your choice.

Note:
    To a non-maintainer must be clear, what is this file about, what he / she
    may find here. 
"""

from typing import List


class Foo:
    """
    Brief description of `Foo` class.

    Long multiline description aka paragraph, if
    it's necessary.

    Attributes:
        a (str):
            Description of `self.a` attribute.
        b (List[str]):
            Long description of `self.b` attribute
            over two lines.

    Properties should be described separately in their `def ...` docstrings.

    Todo:
        - add method `baz`
        - refactor method `bar`
          according to `pylint` advice
    """

    def __init__(self, a: str, b: List[str]=None, c: int=1) -> None:
        """
        Initialize an instance of `Foo` class.

        Arguments:
            a:
                Description of `a` parameter.
            b:
                Long description of `b` parameter
                over two lines. 
            c:
                Description of `c` parameter.

        Note:
            If you're using type hints, then you don't have to write
            explicitly data types and default values (if any) for each
            argument. If you don't you use it, then you should write them
            yourself.

        Example:
            a (str):
                Description ...
            b (List[str], optional):
                Description ...
            c (float, optional, default 1):
                Description ...

        Warning:
            Do **NOT** use blank lines (even only 1) in the descriptions for
            whatever header (`Arguments:`, `Note:` etc.) unless it's inside
            the `Example:` section (1 blank line is allowed).
        """
        pass

    def x(self) -> int:
        """
        Description of `self.x` property.

        Note:
            Better support for property description will be added in the
            future version (0.3.0), watch #49 issue. 
        """
        pass

    def bar(self) -> dict:
        """
        Description of `self.bar` method.

        If there was defined parameters, then again you should write
        `Arguments:` section like for the constructor.

        Returns:
            Description for a returned value.

        Again, if you are using type hints, then you don't have to write
        a data type of the returned value. But if you're not using it, please
        write explicitly the data type.

        Returns:
            dict:
                Description ...

        If a method / function may raise an error, also mention it.

        Raises:
            ErrorName:
                Error description.
            NextErrorName:
                Long error description
                over two lines.
        """
        pass


def generator() -> int:
    """
    Descriptin of this `generator` function.

    Instead of `Returns:` you should write `Yields:` for generators like:

    Yields:
        Description for a yield value.

    or explicitly (not using type hints):

    Yields:
        int:
            Description ...
    """
    pass
```

## Coming from Napoleon

List of supported headers:

- Args
- Arguments
- Attributes
- Example
- Note
- Returns
- Raises
- Todo
- Warning
- Yields

Content for these headers write as you are writing with Napoleon. There is only two differences:

1. Do **NOT** use blank lines (1) outside of `Example:` section unless it's normal paragraph breaker.

2. You don't have to write information about data types and default values for the `Arguments:`, `Returns:` and `Yields` section. They will be added automatically into the docstrings if you are using type hints (new feature since Python 3.0). So simply write:

    ```python
    """
    Arguments:
        x: blabla
    """
    ```

## Doksit layer

Doksit has own "layer" (minor features) on top of `Google Docstring Style` + `Napoleon`:

1. automatically insertion of data types (arguments + returned value) and default values into a generated API documentation, if type hints are used.

    ```python
    """
    Instead of:

        x: (str, optional, default "Foo"):
            Description ...

    you may write:

        x:
            Description ...
    """
    ```


2. support for description indentation after colon `:` (for those who used Napoleon before)

    ```python
    """
    Instead of:

        x: Long description
            of `x` argument.

    you may write: (For me it's better for my eyes and brain.)

        x:
            Long description
            of `x` argument.

    """
    ```

2. numbering errors in the `Raises:` section

    - eg. in a constructor is also a validator of data types and there is twice `raise ValueError("...")` for two different arguments:

        ```python
        """
        Raises:
            ValueError:
                1. for a argument `a`
                2. for a
                   argument `b`
        """
        ```

3. you may specify language in the `Example:` section (default is Python)

    ```python
    """
    Example: (markdown)
        # Title
    """
    ```

4. writing pure Markdown (according to [Commonmark specification](http://commonmark.org/help/)) and [GitHub flavored MD](https://guides.github.com/features/mastering-markdown/#GitHub-flavored-markdown) into the docstrings

    ```python
    """
    This is a **bold** text and this is a [link](github) to the GitHub
    homepage.

    | Column A | Column B |
    | --- | :---: |
    | a | b |

    - list
    - list :smile:

    [github]: https://github.com
    """
    ```
