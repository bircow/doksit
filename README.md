# Doksit

`doksit` is a documentation generator (API Reference) with output to Markdown.

It was developed after frustration with [Sphinx](http://www.sphinx-doc.org/en/stable/) which has't have easy 'Getting started' section so I felt lost. [Pydoc](https://docs.python.org/3.5/library/pydoc.html) was also useless. Moreover, I needed something lightweight, respecting type hints and objects order in a module, one command only, output to Markdown and redirection to a single file wherever on a disk.

And that's why on 5th September 2016 came `doksit` to birth (first release).

## Installation

You need Python 3.5 and above, because I use type hints (new feature in Python 3.5).

```
$ pip install doksit
```

## Usage

Before we start you need to know that `doksit` is able to parse only docstrings written in specific format. If you have ever use Google style, then you are very close (I slightly modified it for my purposes).

Sample docstrings:

```python
from typing import List


class Foo:
	"""
    This is a brief description of 'Foo' class.
    
    This is another "long" paragraph.
    
    Note:
    	This is a note
        over two lines.
    
    Attributes:
    	foo (str):
        	Description of 'foo' attribute.
        bar (int):
        	This is a long description
            for 'bar' attribute over two lines.
    
    Todo:
    	- one short todo 
    	- two long todos 
    		over two lines
    """
    
    def __init__(self, x: str, y: float = 1.0, z: List[int] = []) -> None:
        """
        Initialize an instance of class 'Foo'.

        Arguments:
            x:
                Description of 'x'.
            y:
                Description of 'y'
                over two lines.
            z:  # After markdowning this line will be replaced to 'z (List[int], optional, default [])'
                Description of 'z'.
        """

    def method(self) -> bool:
        """
        This is a brief description.

        Warning:
            This is a warning
            over two lines.

        Returns:
            True if something
            happened.
        
        Raises:
        	ErrorName:
                Reason (description).
            ErrorName:
                Long reason
                over two lines.
            ErrorName:  # The same error raises in multiple ways.  
                1. reason
                2. Long reason
                    over two lines.
        """

def long_function_name(n: int) -> int:
	"""
    This is a brief description.

    Arguments:
        n:
            Description of 'n'.

    Yields:  # Instead of 'returns', because this function is generator.
        Integer.

    Example:
        This is an example code.

        This part is after line break.
    """
```

**Note:** Private / protected functions / methods will be ignored. The same goes for magic methods except the '\_\_init\_\_'.

Next, if your project directory looks like:

```
docs/
package_name/
tests/
requirements.txt
...
```

and has docstrings in the format above, then run a command below at root of your project:

```
$ doksit package_name/
```

It only prints your 'API Reference' documentation. If you want to save it:

```
$ doksit package_name/ > docs/api-reference.md
```

**Note:** Real example is API reference for `doksit` itself [HERE](https://github.com/nait-aul/doksit/blob/master/docs/api-reference.md).

Basically, a structure of the generated docs is following:

```
# API Reference

## package_name.module_name

### class package_name.module_name.class_name

Docstring for this class.

#### method method_name

Docstring for this method.

### function package_name.module_name.function_name

Docstring for this function.

## package_name.subpackage_name.module_name

...
```

## Contribution

If you've found a bug or want to suggest new features, please feel free to use [Issue Tracker](https://github.com/nait-aul/doksit/issues).

## License

MIT License.

For more details see the [LICENSE](https://github.com/nait-aul/doksit/blob/master/LICENSE).

