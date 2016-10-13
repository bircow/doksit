"""
Here are defined helping functions.
"""

import os.path

from setuptools import find_packages

from doksit.exceptions import PackageError


def _is_package(package: str) -> bool:
    """
    Check, if the given package is really a package and not (subpackage).

    Arguments:
        package (str):
            Name of package.

    Returns:
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


def validate_file_path(file_path) -> str:
    """
    Validate the given file path.

    Returns:
        True, if the file path really exists.
    """
    return os.path.isfile(file_path)
