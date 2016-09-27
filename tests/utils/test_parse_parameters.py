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
    output = parse_parameters(Foo.__init__)

    assert "self" not in output
    assert output["x"] == "x (str):"
    assert output["y"] == "y (float, optional, default 1.0):"
    assert output["z"] == "z (List[int], optional, default []):"


def test_parse_parameters_from_function():
    """
    Sample function 'function' has these paramaters:

    - n

    but with no annotations. Therefore the function 'parse_paramaters' should
    return False value.
    """
    output = parse_parameters(function)
    assert not output
