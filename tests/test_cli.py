from click.testing import CliRunner

from doksit.cli import cli


def test_cli():
    result = CliRunner().invoke(cli)

    assert result.exit_code == 0
