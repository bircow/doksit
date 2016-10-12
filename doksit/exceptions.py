"""
Here are defined exceptions.
"""


class PackageError(Exception):
    """
    When Doksit cannot find a package directory.
    """

    def __str__(self):
        return "Cannost guess a package, please use option:\n'-p <package>'"
