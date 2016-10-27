"""
Here are defined command line interfaces (CLI) as functions.

Note:
    The CLI docstrings have very short documentation, because they're
    taken as CLI description. Therefore the rest may be written in comments or
    help arguments for each parameters.

Warning:
    The source code links below lead to a module file only and not direct
    to specific line number. The reason is that is not possible to locate
    CLI functions using `click` package (bug).
"""

import os
import subprocess

import click

from doksit.api import DoksitStyle
from doksit.exceptions import InvalidPlace
from doksit.helpers import guess_package, check_for_toc_file
from doksit.toc import TableOfContents
from doksit.utils.highlighters import ColoredHighlighter, SmoothHighlighter


@click.group()
def cli() -> None:
    """
    Use one of the subcommands below.
    """
    #
    # This function only initialize `doksit` CLI. Real commands (subcommands)
    # are defined below.
    #
    pass


@cli.command()
@click.option("-p", "--package", type=click.Path(exists=True),
              help="Path to the package directory.")
@click.option("-t", "--title", type=str, default="API Reference",
              help="Title for the generated documentation.")
@click.option("--smooth", is_flag=True,
              help="Smooth the documentation output.")
@click.option("--colored", is_flag=True,
              help="Color the documentation output.")
def api(package: str, title: str, smooth: bool, colored: bool) \
        -> None:
    """
    Generate the API Reference documentation.
    """
    #
    # If a stdout redirection isn't used, then the documentation will be
    # printed like man pages via `less`.
    #

    if package is None:
        package = guess_package()

    api_parser = DoksitStyle(package, title)
    api_documentation = api_parser.get_api_documentation()

    if colored:
        colored_parser = ColoredHighlighter(api_documentation)
        colored_documentation = colored_parser.get_api_documentation()

        read, write = os.pipe()
        os.write(write, colored_documentation.encode("ascii"))
        os.close(write)

        subprocess.call(["less", "-r"], stdin=read)
    elif smooth:
        smooth_parser = SmoothHighlighter(api_documentation)

        click.echo_via_pager(smooth_parser.get_api_documentation())
    else:
        click.echo_via_pager(api_documentation)


@cli.command()
def toc():
    """
    Create table of contents with links to the documentation on gitHub.
    """
    if "docs" in os.listdir():
        is_inside = False
        check_for_toc_file(is_inside)
    elif os.path.basename(os.getcwd()) == "docs":
        is_inside = True
        check_for_toc_file(is_inside)
    else:
        raise InvalidPlace

    TableOfContents().generate_toc(is_inside)

    click.echo("OK")
