import click

from doksit.api import find_files, get_documentation, read_file


@click.group()
def cli():
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
    file_paths = find_files(package_directory)

    api_documentation = ["# API Reference\n"]

    for file in file_paths:
        file_documentation = get_documentation(read_file(file))

        if file_documentation is not None:
            api_documentation.append(file_documentation)

    # Remove 2 blank lines at the end of last item in the 'api_documentation'.

    api_documentation[-1] = api_documentation[-1][:-2]
    
    click.echo_via_pager("\n".join(api_documentation))
