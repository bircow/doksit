from doksit.helpers import validate_file_path


def test_validate_file_path():
    assert validate_file_path("test_data/module.py")
    assert validate_file_path("test_data/subpackage/module.py")
    assert not validate_file_path("doksit/blablabla.py")
