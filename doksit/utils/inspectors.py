"""
Here are defined helping functions for getting particular information.
"""

import inspect
import subprocess
import re

from typing import Any, Union

REPOSITORY_URL_REGEX = re.compile(r"origin\t([\S]+) ")
BRANCH_NAME_REGEX = re.compile(r"\* ([\S]+)\n")


def get_repository_url() -> Union[str, None]:
    """
    Get absolute URL path to a Github repository including current branch
    name if a user is using Git & GitHub.

    Note:
        The URL is not correct yet, because it will be used as prefix.

    Returns:
        The absolute URL path or nothing if the Git is not used.

    Example:
        https://github.com/nait-aul/doksit/blob/master/
    """
    try:
        remote_repository = subprocess.check_output(
            ["git", "remote", "-v"], universal_newlines=True)
        current_branch = subprocess.check_output(
            ["git", "branch"], universal_newlines=True)
    except subprocess.CalledProcessError:
        return

    repository_url = REPOSITORY_URL_REGEX.search(remote_repository).group(1)
    branch_name = BRANCH_NAME_REGEX.search(current_branch).group(1)

    return repository_url + "/blob/" + branch_name + "/"


def get_line_numbers(object_name: Any) -> str:
    """
    Find on which lines is the given object defined.

    Arguments:
        object_name:
            For which object (class, method, function) to get the line numbers.

    Note:
        There is a problem for getting line numbers for defined CLI commands
        using a `click` package (will raise `TypeError). Therefore it will be
        silenced and returned only `#`.

    Returns:
        Range, where the object definition starts and ends or only `#`
        if `TypeError` was raised.

    Example:
        #L10-L25  # or only '#'
    """
    try:
        source_lines, starting_line = inspect.getsourcelines(object_name)
    except TypeError:
        return "#"

    ending_line = starting_line + len(source_lines) - 1

    # Note:
    #
    # Without '- 1' for the 'ending_line' it would include blank line after
    # the object definition.

    return "#L{starting_line}-L{ending_line}".format(
        starting_line=starting_line, ending_line=ending_line)
