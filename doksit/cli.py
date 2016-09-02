import argparse

description = "Generate API Reference documentation"

parser = argparse.ArgumentParser(description=description)
parser.add_argument(
    "-v", "--version",
    action="version",
    version="Doksit 0.1.0"
)
parser.add_argument(
    "directory",
    help="relative path to your Python package directory"
)
