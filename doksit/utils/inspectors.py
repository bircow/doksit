import inspect

from typing import Any


def get_repository_link():
    """
    Get absolute URL path.
    """
    pass


def get_line_numbers(object: Any):
    """
    Find on which lines is the given object defined.

    Arguments:
        object:
            For which object (class, method, function) to get the line numbers.

    Note:
        There is a problem for getting line numbers for defined CLI commands
        using `click` package (will raise `TypeError). Therefore it will be
        silenced and returned only `#`.

    Returns:
        String range, where the object definition starts and ends.

    Example:
        #L10-L25
    """
    try:
        source_lines = inspect.getsourcelines(object)
    except TypeError:
        return "#"

    starting_line = source_lines[1]
    ending_line = starting_line + len(source_lines[0]) - 1

    # Note: Without '- 1' for the 'ending_line' it would include blank line
    # after the object definition.

    return "#L{starting_line}-L{ending_line}".format(
        starting_line=starting_line, ending_line=ending_line)
