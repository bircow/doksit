from doksit.api import find_files


def test_find_files_in_the_given_directory():
    expected_file_paths = [
        "test_data/module.py",
        "test_data/subpackage/module.py",
        "test_data/subpackage/subpackage/module.py",
    ]

    assert find_files("test_data") == expected_file_paths
