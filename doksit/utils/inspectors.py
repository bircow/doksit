"""
Here are defined helping functions for getting particular information.
"""

import inspect
import subprocess
import re

from typing import Any, Union

REPOSITORY_URL_REGEX = re.compile(r"origin\t([\S]+) ")
BRANCH_NAME_REGEX = re.compile(r"\* ([\S]+)\n")


def _get_repository_url() -> Union[str, None]:
    """
    Get an absolute URL path to a Github repository including current branch
    name if a user is using Git & GitHub.

    Note:
        The URL is not correct yet, because it will be used as prefix.

    Returns:
        The absolute URL path or nothing if the Git is not used.

    Example:
        "https://github.com/nait-aul/doksit/blob/master/"
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


def _get_line_numbers(object_name: Any) -> str:
    """
    Find on which lines is the given object defined.

    Arguments:
        object_name:
            For which object (class, method, function) to get the line numbers.

    Note:
        There is a problem for defined CLI commands (functions) using a
        `click` package, because it will raise `TypeError. Therefore it will be
        silenced and returned only `#`.

    Returns:
        Range, where the object definition starts and ends or only `#` if
        the `TypeError` was raised.

    Example:
        "#L10-L25"
    """
    try:
        source_lines, starting_line = inspect.getsourcelines(object_name)
    except TypeError:
        return "#"

    ending_line = starting_line + len(source_lines) - 1

    return "#L{starting_line}-L{ending_line}" \
        .format(starting_line=starting_line, ending_line=ending_line)


def get_source_code_url(module: Any, object_name: Any=None) -> str:
    """
    Get an absolute path to the source file on GiHub.

    If there is an argument for the `object_name` parameter, then a suffix
    for line highlights will be added.

    Arguments:
        module:
            Module object.
        object_name:
            Class / method / function object.

    Returns:
        The full URL path or empty string if a user isn't using Git & GitHub.

    Example:
        ""
    """
    module_path = module.__name__.replace(".", "/") + ".py"
    repository_url = _get_repository_url()

    if repository_url is not None:
        url = "[source](" + repository_url + module_path

        if object_name is not None:
            url += _get_line_numbers(object_name)

        url += ")\n\n"
    else:
        url = ""

    return url
