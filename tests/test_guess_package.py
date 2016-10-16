import os

import pytest

from doksit.exceptions import PackageError
from doksit.helpers import guess_package


def test_guess_package():
    os.chdir("..")

    assert guess_package() == "doksit"

    os.chdir("tests")


def test_fail_guess_package():
    with pytest.raises(PackageError) as error:
        guess_package()

    message = "Cannost guess a package, please use option:\n'-p <package>'"

    assert str(error.value) == message
