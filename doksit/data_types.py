"""
Here are defined own data types.
"""

import collections


class MyOrderedDict(collections.OrderedDict):
    """
    Upgraded `OrderedDict` from the standard library `collections`.
    """

    def last(self) -> str:
        """
        Get the name of last inserted key.

        Returns:
            The name of last inserted key.

        Example:
            "foo"
        """
        return list(self.keys())[-1]
