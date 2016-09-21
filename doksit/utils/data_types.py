"""
Here are defined own data types.
"""

import collections


class MyOrderedDict(collections.OrderedDict):
    """
    Upgraded `OrderedDict` from the standard library `collections`.
    """

    def last(self):
        """
        Get the name of the last inserted key.
        """
        return list(self.keys())[-1]
