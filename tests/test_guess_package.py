import os

import pytest

from setuptools import find_packages

from doksit.exceptions import PackageError
from doksit.validators import guess_package, _is_package


def test_is_package():
    assert _is_package("doksit")
    assert not _is_package("doksit.cli")


def test_guess_package():
    os.chdir("..")

    assert guess_package() == "doksit"


def test_fail_guess_package():
    packages = find_packages()
    filtered_packages = list(filter(_is_package, packages))

    if "tests" in filtered_packages:
        filtered_packages.remove("tests")

    with pytest.raises(PackageError):
        if len(filtered_packages) >= 1:
            raise PackageError
