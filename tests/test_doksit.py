import os
import unittest


class TestDoksitItself(unittest.TestCase):

    def test_doksit_command(self):
        os.system("python -m doksit package/ > tmp.md")

        with open("tmp.md") as f:
            first_line = f.readline()

        assert first_line == "# API Reference\n"

        os.system("rm tmp.md")


if __name__ == "__main__":
    unittest.main()
