from doksit.utils import MyOrderedDict


def test_get_last_inserted_dict_key():
    sample_dict = MyOrderedDict()
    sample_dict.update({"foo": 0})
    sample_dict.update({"bar": 1})

    assert sample_dict.last() == "bar"
