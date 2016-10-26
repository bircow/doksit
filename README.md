# Doksit

[![Build Status](https://travis-ci.org/nait-aul/doksit.svg?branch=master)](https://travis-ci.org/nait-aul/doksit)
[![codecov](https://codecov.io/gh/nait-aul/doksit/branch/master/graph/badge.svg)](https://codecov.io/gh/nait-aul/doksit)
![Pylint](https://img.shields.io/badge/pylint%20doksit-10%2F10-brightgreen.svg)

`Doksit` is an API documentation generator (draft) for the [MkDocs][mkdocs] project (lightweight and simple alternative to [Sphinx][sphinx]) at the moment.

In the future it will be also:

- docstring linter
- TODO notifier
- integrated with the `MkDocs` (easy interlinks to API, one command for everything etc.)
- open to 3rd party packages (eg. different docstring parser)

\+ has own `MkDocs` theme

## Installation

Doksit is available only for Python 3.x version.

```
# DO NOT INSTALL IT YET, new version 0.2.0 will be shipped soon (26 - 27th).

$ pip install doksit
```

## Usage

Before I mention a CLI command for generating the API documentation, you should know that Doksit parses only docstrings based on a combination of 

1. [Google Docstring Style][google]
2. [Napoleon][napoleon] layer (docstring parser for [Sphinx][sphinx])
3. and a Doksit layer on top of it.

**Note:** If you are using the `Napoleon`, then only around 95 % of its features is compatible with Doksit docstring parser.

---

The CLI command is following:

```
$ doksit api
```

This is the shortest variant, which assumes that your project directory looks like:

```markdown
docs/
<package_name>/
tests/
.gitignore
...
```

and you've run the command in that directory.

Doksit will automatically detect the `<package_name>/` directory, browse its directory, scan all the Python files and get the API documentation for them (will be showed via `less` program if no output redirection is used).

For the redirection use the standard Unix redirection:

```
$ doksit api <package_name> > docs/api.md
```

But if it fails (cannot detect a package directory), then you will be warned and prompted to use a `-p` / `--package` option:

```
$ doksit api -p <package_name>  # or
$ doksit api --package <package_name>
```

The structure of the API documentation without using templates is following:

```markdown
# <api_title>

## <package_name>.<module_name>

[source](https://github.com/<username>/<repository>/blob/<branch>/<package_directory>/<file>.py)

Content of the module docstring.

### class <class_name>

[source](.../<file>.py#L1-L10)

Content of the class docstring.

#### constructor
#### property <property_name>
#### method <method_name>

[source](...)

Content of the constructor / property / method docstring.

### function <function_name>

[source](...)

Content of the function docstring.
```

Live example you may find [HERE](https://github.com/nait-aul/doksit/blob/master/tests/docs/api.md). It's for test data used by Doksit's tests.

## Documentation

Further documentation is located in the [docs/](https://github.com/nait-aul/doksit/tree/master/docs) folder of this repository.

**Note:** This is a temporary solution until [Doksit theme](https://github.com/nait-aul/mkdocs-doksit) for the `MkDocs` will be ready to use the `MkDocs` and GitHub Pages.

## FAQ

> What should convice me to use Doksit (with MkDocs) instead of Sphinx?

Doksit's goal is **NOT** to fully replace the power of `Sphinx`. You should always use the right tools for the job. If you need features provided by `Sphinx` with `reStructuredText`, then surely go with them.

But if you like the [MkDocs][mkdocs], don't need superior features (versioning, internalization, `reST` directives, ...) and want an API generator for it, then Doksit may help you with it.

## Contribution

If you've found a bug or want to suggest new features / improvements, please feel free to use [GitHub Issue Tracker](https://github.com/nait-aul/doksit/issues).

## License

MIT License.

For more details see the [LICENSE](https://github.com/nait-aul/doksit/blob/master/LICENSE).

[google]: http://google.github.io/styleguide/pyguide.html#Comments
[mkdocs]: http://www.mkdocs.org/
[napoleon]: https://pypi.python.org/pypi/sphinxcontrib-napoleon
[sphinx]: http://www.sphinx-doc.org/en/stable/
