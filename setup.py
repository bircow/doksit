import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 5, 0):
    sys.exit("ERROR: You need Python 3.5 or later to use doksit.")

try:
    import pypandoc

    long_description = pypandoc.convert("README.md", "rst")
except ImportError:
    long_description = ""

setup(
    name="doksit",
    version="0.1.0",
    description="Documentation generator with output to Markdown.",
    long_description=long_description,
    author="Nait Aul",
    author_email="nait-aul@protonmail.com",
    url="https://github.com/nait-aul/doksit",
    license="MIT License",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "doksit = doksit.main:main"
        ]
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries"
    ]
)
