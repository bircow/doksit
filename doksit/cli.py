"""
Here are defined command line interfaces (CLI) as functions.

Note:
    The functions docstrings have very short documentation, because they're
    taken as CLI description. Therefore the rest is written in comments.

Warning:
    The source code links below lead to a module file only and not direct
    to specific line number. The reason is that is not possible to locate
    CLI functions using `click` package (bug).
"""
import os
import subprocess

import click

from doksit.api import (
    find_files, get_documentation, read_file, color_documentation)


@click.group()
def cli():
    """
    Use one of the subcommands below.
    """
    #
    # This function only initialize `doksit` CLI. Real commands (subcommands)
    # are defined below.
    #
    pass


@cli.command()
@click.option("--colored", is_flag=True,
              help="Color the documentation output.")
@click.argument("package_directory", type=click.Path(exists=True))
def api(package_directory: str, colored: bool):
    """
    Generate the API Reference documentation.
    """
    #
    # If a stdout redirection isn't used, then the documentation will be
    # printed like man pages.
    #
    # Arguments:
    #     package_directory:
    #         Relative path to the Python package directory.
    #     colored:
    #         Whether to color the documentation output or not.
    #

    api_documentation = ["# API Reference"]
    file_paths = find_files(package_directory)

    for file in file_paths:
        file_metadata = read_file(file)
        file_documentation = get_documentation(file_metadata)

        if file_documentation is not None:
            api_documentation.append(file_documentation)

    if colored:
        colored_documentation = color_documentation(api_documentation)

        read, write = os.pipe()
        os.write(write, colored_documentation.encode("ascii"))
        os.close(write)

        subprocess.call(["less", "-r"], stdin=read)
    else:
        click.echo_via_pager("\n".join(api_documentation))
