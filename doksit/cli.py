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

from doksit.api import DoksitStyle
from doksit.utils.highlighter import color_documentation


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
@click.option("-t", "--title", type=str, default="API Reference",
              help="Title for the generated documentation.")
@click.option("--colored", is_flag=True,
              help="Color the documentation output.")
@click.argument("package_directory", type=click.Path(exists=True))
def api(package_directory: str, colored: bool, title: str):
    """
    Generate the API Reference documentation.
    """
    #
    # If a stdout redirection isn't used, then the documentation will be
    # printed like man pages.
    #
    # Arguments:
    #     package_directory (str):
    #         Relative path to the Python package directory.
    #     title (str):
    #         Title name for the generated documentation.
    #     colored (bool):
    #         Whether to color the documentation output or not.
    #

    api_parser = DoksitStyle(package_directory, title)
    api_documentation = api_parser.get_api_documentation()

    if colored:
        colored_documentation = color_documentation(api_documentation)

        read, write = os.pipe()
        os.write(write, colored_documentation.encode("ascii"))
        os.close(write)

        subprocess.call(["less", "-r"], stdin=read)
    else:
        click.echo_via_pager(api_documentation)
