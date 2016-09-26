"""
Here are defined command line interfaces (CLI).
"""

import click

from doksit.api import find_files, get_documentation, read_file
from doksit.utils.inspectors import get_repository_url


@click.group()
def cli():
    """
    This function only initialize `doksit` CLI. Real commands (subcommands)
    are defined below.
    """
    pass


@cli.command()
@click.argument("package_directory", type=click.Path(exists=True))
def api(package_directory: str):
    """
    Command for generating the API Reference documentation for the given Python
    package.

    If a user doesn't use stdout redirection, then the documentation will be
    printed like man pages.

    Arguments:
        package_dir:
            Name of the Python package (relative path).
    """
    api_documentation = ["# API Reference\n"]
    file_paths = find_files(package_directory)
    repository_url = get_repository_url()

    for file in file_paths:
        file_metadata = read_file(file)
        file_documentation = get_documentation(file_metadata, repository_url)

        if file_documentation:
            api_documentation.append(file_documentation)

    # Remove 2 blank lines at the end of last item in the 'api_documentation'.

    api_documentation[-1] = api_documentation[-1][:-2]

    click.echo_via_pager("\n".join(api_documentation))
