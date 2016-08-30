import collections


class OrderedDict(collections.OrderedDict):
    """Upgraded 'OrderedDict' from module 'collections'."""

    def last(self):
        """Get a name of the last key"""
        return next(reversed(self))
