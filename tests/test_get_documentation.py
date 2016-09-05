import unittest

from doksit.main import get_documentation, read_file


class TestGetDocumentationFunction(unittest.TestCase):

    def test_get_documentation_for_sample_file(self):
        """
        Sample file (module) is 'package.module'.
        """
        file_metadata = read_file("package/module.py")
        file_documentation = get_documentation(file_metadata)

        assert "package.module" in file_documentation


if __name__ == "__main__":
    unittest.main()
