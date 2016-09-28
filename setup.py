import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

if sys.version_info < (3, 5, 0):
    sys.exit("ERROR: You need Python 3.5 or later to use doksit.")


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


try:
    import pypandoc

    long_description = pypandoc.convert("README.md", "rst")
except ImportError:
    long_description = ""

setup(
    name="doksit",
    version="0.2.0",
    description="Future all-in-one documentation tool for Python packages.",
    long_description=long_description,
    author="Nait Aul",
    author_email="nait-aul@protonmail.com",
    url="https://github.com/nait-aul/doksit",
    license="MIT License",

    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    entry_points={
        "console_scripts": [
            "doksit = doksit.cli:cli"
        ]
    },

    tests_require=["pytest"],
    cmdclass={"test": PyTest},

    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries"
    ]
)
