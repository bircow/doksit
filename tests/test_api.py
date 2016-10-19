from click.testing import CliRunner

from doksit.cli import api

RUNNER = CliRunner()


def test_api_subcommand():
    result = RUNNER.invoke(api, ["-p", "test_data"])

    assert result.exit_code == 0
    assert "# API Reference" in result.output


def test_api_subcommand_with_error():
    """
    Will raise PackageError, because here in directory Doksit cannot guess
    a package name (found 2 subpackages).
    """
    result = RUNNER.invoke(api)

    assert result.exit_code == -1


def test_title_option():
    result = RUNNER.invoke(api, ["-p", "test_data/", "-t", "Different title"])

    assert result.exit_code == 0
    assert "# Different title" in result.output


def test_api_subcommand_with_smooth_flag():
    result = RUNNER.invoke(api, ["-p", "test_data/", "--smooth"])

    assert result.exit_code == 0


def test_api_subcommand_with_colored_flag():
    """
    Don't assert a content in the result.output, because it executes
    subprocess call.
    """
    result = RUNNER.invoke(api, ["-p", "test_data/", "--colored"])

    assert result.exit_code == 0
