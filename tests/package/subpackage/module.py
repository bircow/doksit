from typing import List


class Foo:
    """This is a brief description.

    This is a long description.

    Note:
        This is a note.

    Attributes:
        foo (str):
            Foo is the attribute.
        bar (int):
            Bar is another attribute.

    Todo:
        - one thing
        - two things
    """

    def __init__(self, x: str, y: float = 1.0, z: List[int] = []) -> None:
        """This is a brief description.

        Arguments:
            x:
                Description of 'x'.
            y:
                Description of 'y'.
            z:
                Description of 'z'.

        Raises:
            AssertionError:
                Assertion failed.
            ValueError:
                1. Invalid argument for 'x'.
                2. Invalid argument for 'y'.
                3. Invalid argument for 'z'.
        """

    def method(self) -> bool:
        """This is a brief description.

        This is a long description.

        Warning:
            This is a warning.

        Returns:
            bool:
                Description.
        """

    def _protected(self) -> list:
        """This will be ignored."""

    def __private(self) -> tuple:
        """This will be also ignored."""

    def __magic__(self) -> dict:
        """This will be also ignored."""


def function(n) -> int:
    """This is a brief description.

    This is a long description.

    Arguments:
        n:
            Description of 'n'.

    Yields:
        int:
            Description.

    Example:
        This is an example code.
    """


def another_function() -> None:
    """This is a brief description."""
    pass


if __name__ == "__main__":
    pass
