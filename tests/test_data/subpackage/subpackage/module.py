"""
This is a module docstring, right?

Example:
    >>> print("Hello World!)
    Hello World!
"""

from typing import List, Union


class Foo:
    """
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

    def __init__(self, x: str, y: float = 1.0, z: List[int] = []) -> None:
        """
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
        pass

    def method(self) -> List[str]:
        """
        This is a brief description.

        This is a long description.

        Warning:
            This is a warning.

        Returns:
            True.

        Example: (markdown)
            # Heading
        """
        pass

    @staticmethod
    def static_method() -> str:
        """
        This is a static method.

        Returns:
            str:
                Return description
                over two lines.
        """
        pass

    def _protected(self) -> list:
        """
        This will be ignored.
        """
        pass

    def __private(self) -> tuple:
        """
        This will be also ignored.
        """
        pass

    def __magic__(self) -> dict:
        """
        This will be also ignored.
        """
        pass


class Bar:
    pass


def function(n) -> int:
    """
    This is a brief description.

    This is a long description.

    Arguments:
        n:
            Description of 'n'.

    Yields:
        Integer.

    Example:
        # This is an example code.

        # This part is after line break.
    """
    pass


def another_function() -> Union[str, int]:
    """This is a brief oneline description."""
    pass


def _hidden_function() -> None:
    """
    This will be ignored.
    """
    pass
