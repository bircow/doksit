import os
import os.path

from doksit.cli import toc

from tests.test_api import RUNNER


def test_toc_subcommand_outside_docs():
    with open("docs/_toc.md", "w") as file:
        file.write("# Title\n{{ example.md }}")

    result = RUNNER.invoke(toc)

    assert result.exit_code == 0
    assert os.path.exists("docs/README.md")

    os.remove("docs/README.md")
    os.remove("docs/_toc.md")


def test_toc_subcommand_inside_docs_folder():
    os.chdir("docs")

    with open("_toc.md", "w") as file:
        file.write("# Title\n{{ example.md }}")

    result = RUNNER.invoke(toc)

    assert result.exit_code == 0
    assert os.path.exists("README.md")

    os.remove("README.md")
    os.remove("_toc.md")
    os.chdir("..")


def test_toc_subcommand_in_invalid_place():
    os.chdir("test_data")

    result = RUNNER.invoke(toc)
    error_message = "Cannot create the TOC, you're in the wrong directory."

    assert result.exit_code == -1
    assert str(result.exception) == error_message

    os.chdir("..")
