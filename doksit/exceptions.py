"""
Here are defined own exceptions.
"""


class InvalidObject(Exception):
    """
    When a user placed into a module docstring a template variable with
    invalid object reference to a class / funciton.
    """
    __slots__ = ("module", "object_name")

    def __init__(self, module_name: str, object_name: str) -> None:
        """
        Initialize an object of class `InvalidObject`.

        Arguments:
            module_name:
                Name of a module.
            object_name:
                Name of an object.
        """
        super().__init__()
        self.module_name = module_name
        self.object_name = object_name

    def __str__(self) -> str:
        return (
            "In a {module}'s docstring is an invalid template variable "
            "'{{{{ {variable} }}}}'."
        ).format(module=self.module_name, variable=self.object_name)


class PackageError(Exception):
    """
    When Doksit cannot guess / detect a package directory.
    """

    def __str__(self) -> str:
        return "Cannost guess a package, please use option:\n'-p <package>'"
