import sys

from click.testing import CliRunner

from doksit.cli import api

# IMPORTANT:
#
# Add current directory to the Python sys path, othwerise this test fails.
# I don't know why it's buggy. With normal script / Python interpret / unittest
# it's working but with pytest no...

sys.path.append(".")


def test_api_subcommand():
    runner = CliRunner()
    result = runner.invoke(api, ["test_data/"])

    assert result.exit_code == 0
    assert "# API Reference" in result.output
