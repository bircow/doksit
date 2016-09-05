import unittest

from doksit.main import find_files, file_paths


class TestFindFilesFunction(unittest.TestCase):

    def test_find_files_in_the_given_directory(self):
        """
        The 'find_files' requires external (global) variable 'file_paths'
        to run successfully.
        """
        expected_file_paths = [
            "package/module.py",
            "package/subpackage/module.py",
            "package/subpackage/subpackage/module.py",
        ]

        find_files("package")
        assert file_paths == expected_file_paths


if __name__ == "__main__":
    unittest.main()
