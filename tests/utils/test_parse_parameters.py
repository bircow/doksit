import collections
import inspect

from doksit.utils.parsers import parse_parameters

from tests.test_data.module import Foo, function


def test_parse_parameters_from_method():
    """
    Sample method 'Foo.__init__' has these parameters:

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


def test_parse_parameters_from_function():
    """
    Sample function 'function' has these paramaters:

    - n

    and expected output is:

    {"n": "n:"}
    """
    function_parameters = inspect.signature(function).parameters
    function_parameters = collections.OrderedDict(function_parameters)

    output = parse_parameters(function_parameters)

    assert output["n"] == "n:"
