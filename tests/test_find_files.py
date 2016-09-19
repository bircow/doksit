from doksit.api import find_files, file_paths


def test_find_files_in_the_given_directory():
    """
    The 'find_files' function requires external (global) variable 'file_paths'
    to run successfully.
    """
    expected_file_paths = [
        "test_data/module.py",
        "test_data/subpackage/module.py",
        "test_data/subpackage/subpackage/module.py",
    ]

    find_files("test_data")
    assert file_paths == expected_file_paths
