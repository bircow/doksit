"""
Here are defined command line interfaces (CLI) as functions.
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
    Generate the API Reference documentation for the given package.

    If stdout redirection isn't used, then the documentation will be printed
    like man pages.

    Arguments:
        package_directory:
            Relative path to the Python package directory.
    """
    api_documentation = ["# API Reference\n"]

    file_paths = find_files(package_directory)
    repository_url = get_repository_url()

    for file in file_paths:
        file_metadata = read_file(file)
        file_documentation = get_documentation(file_metadata, repository_url)

        if file_documentation is not None:
            api_documentation.append(file_documentation)

    # Remove a blank line at the end of last item of 'api_documentation'.

    api_documentation[-1] = api_documentation[-1][:-1]
    click.echo_via_pager("\n".join(api_documentation))
