import os
import unittest

from doksit.main import read_file, class_regex, method_regex, function_regex


class TestReadFileFunction(unittest.TestCase):

    def test_regex_for_classes(self):
        classes = [
            "class Foo:",
            "class Foo(object):",
            "class Foo(Bar, object):"
        ]

        for class_name in classes:
            assert class_regex.search(class_name).group(1) == "Foo"

    def test_regex_for_methods(self):
        methods = [
            "    def sample_method(cls)",
            "    def sample_method(cls, arg1, arg2, ...)",
            "    def sample_method(self)",
            "    def sample_method(self, arg1, arg2, ...)"
        ]

        for method_name in methods:
            assert method_regex.search(method_name).group(1) == "sample_method"

    def test_regex_for_functions(self):
        functions = [
            "def function_name()",
            "def function_name(arg1, arg2, ...)"
        ]

        for function_name in functions:
            assert function_regex.search(function_name).group(1) \
                == "function_name"

    def test_read_sample_file_from_sample_package(self):
        """The file is located here in 'package/module.py'.

        Expected result is:

            (
                "package/module.py",
                OrderedDict([('Foo', ['__init__', 'method']), ('Bar', [])]),
                ['function', 'another_function']
            )

        """
        result = read_file("package/module.py")
        
        assert result[0] == "package/module.py"
        assert list(result[1].keys()) == ["Foo", "Bar"]
        assert result[1]["Foo"] == ["__init__", "method"]
        assert not result[1]["Bar"]
        assert result[2] == ["function", "another_function"]


if __name__ == "__main__":
    unittest.main()
