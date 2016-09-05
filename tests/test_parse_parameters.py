import collections
import inspect
import unittest

from doksit.utils.parser import parse_parameters

from package.module import Foo


class TestParseParametersFunction(unittest.TestCase):

    def test_parse_parameters_from_method(self):
        """
        Sample 'Foo.__init__' has these parameters:

        - self
        - x: str
        - y: float = 1.0
        - z: List[int] = []

        and expected (unorered) output is:

        {"x": "x (str)", "y": "y (float, optional, default 1.0),
         "z": "z (List[int], optional, [])}
        """
        method_parameters = inspect.signature(Foo.__init__).parameters
        method_parameters = collections.OrderedDict(method_parameters)
        output = parse_parameters(method_parameters)

        assert "self" not in output
        assert output["x"] == "x (str):"
        assert output["y"] == "y (float, optional, default 1.0):"
        assert output["z"] == "z (List[int], optional, default []):"


if __name__ == "__main__":
    unittest.main()
