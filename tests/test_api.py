import sys

from click.testing import CliRunner

from doksit.cli import api

# IMPORTANT:
#
# Add current directory to the Python sys path, othwerise this test fails.

sys.path.append(".")

RUNNER = CliRunner()


def test_api_subcommand():
    result = RUNNER.invoke(api, ["test_data/"])

    assert result.exit_code == 0
    assert "# API Reference" in result.output


def test_title_option():
    result = RUNNER.invoke(api, ["test_data", "--title", "Different title"])

    assert result.exit_code == 0
    assert "# Different title" in result.output


def test_api_subcommand_with_colored_option():
    """
    Don't assert a content in the result.output, because it executes
    subprocess call.
    """
    result = RUNNER.invoke(api, ["test_data/", "--colored"])

    assert result.exit_code == 0
