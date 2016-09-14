import inspect


def get_line_numbers(object):
    """
    Find on which lines is the object defined.

    Arguments:
        object (object):
            For which object (class, method, function) to get the line numbers.

    Returns:
        String with the object line numbers (range from-to).

    Example:
        #L10-L25
    """
    source_lines = inspect.getsourcelines(object)
    starting_line = source_lines[1]
    ending_line = starting_line + len(source_lines[0]) - 1

    # Note: Without minues one for 'ending_line' it would include blank line
    # after the object definition.

    return "#L{0}-L{1}".format(starting_line, ending_line)
