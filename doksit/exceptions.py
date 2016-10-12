"""
Here are defined exceptions.
"""

class PackageError(Exception):

    def __str__(self):
        return "Cannost guess a package, please use option:\n'-p <package>'"
