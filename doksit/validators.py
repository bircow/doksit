"""
Here are defined validation functions (callbacks) and other helpers for CLI
commands.
"""

from setuptools import find_packages

from doksit.exceptions import PackageError


def _is_package(package: str) -> bool:
    """
    Check, if the given package is really a package or not (subpackage).

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
