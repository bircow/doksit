"""
Here are defined helping functions.
"""

import os
import os.path

from setuptools import find_packages

from doksit.exceptions import PackageError, MissingTocFile


def get_toc_file_path(is_inside: bool) -> str:
    """
    Get an absolute file path to the `_toc.md` file.

    Note:
        The file path may be invalid (doesn't exists), but this is checked
        in another function (see below).

    Arguments:
        is_inside (bool):
            If a user is inside the `docs/` folder or outside.

    Returns:
        str:
            The file path to the `_toc.md`.

    Example:
        /home/<user>/<directory>/doksit_env/docs/_toc.md
    """
    current_directory = os.getcwd()
    file = "_toc.md"

    if is_inside:
        path = os.path.join(current_directory, file)
    else:
        path = os.path.join(current_directory, "docs", file)

    return path


def check_for_toc_file(is_inside: bool) -> None:
    """
    Check if a user has `_toc.md` file.

    Arguments:
        is_inside:
            If a user is inside the `docs/` folder or outside.

    Raises:
        MissingTocFile:
            Cannot find the `_toc.md` file.
    """
    path = get_toc_file_path(is_inside)

    try:
        open(path).close()
    except FileNotFoundError:
        raise MissingTocFile


def _is_package(package: str) -> bool:
    """
    Check, if the given package is really a package and not subpackage.

    Arguments:
        package (str):
            Name of package.

    Returns:
        bool:
            True if the given package is a package.
    """
    return "." not in package


def guess_package() -> str:
    """
    Guess a package directory name.

    Returns:
        The package name.

    Example:
        "doksit"

    Raises:
        PackageError:
            Cannot guess a package name.
    """
    packages = find_packages()
    filtered_packages = list(filter(_is_package, packages))

    if "tests" in filtered_packages:
        filtered_packages.remove("tests")

    if not len(filtered_packages) == 1:
        raise PackageError

    return filtered_packages[0]


def validate_file_path(file_path) -> bool:
    """
    Validate the given file path.

    Returns:
        True, if the file path really exists.
    """
    return os.path.isfile(file_path)
