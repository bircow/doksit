import unittest

from doksit.utils import MyOrderedDict


class TestModifiedOrderedDict(unittest.TestCase):

    def test_last_added_key(self):
        sample_dict = MyOrderedDict()
        sample_dict.update({"foo": 0})
        sample_dict.update({"bar": 1})

        assert sample_dict.last() == "bar"


if __name__ == "__main__":
    unittest.main()
