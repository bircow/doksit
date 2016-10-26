# Contributing to the Doksit

If you want to actively contribute to the Doksit (by this I mean pull requests), then keep on reading.

I appreciate PL for bugs or improving codes (readability / speed), but if you 
want to write a new feature, please:

1. suggest it on the [Issue Tracker](https://github.com/nait-aul/doksit/issues)
2. mention that you would write it yourself
3. wait for my reaction

Thanks a lot.

## Code style

Follow:

1. [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/) standard

    - for checking code "grammar" use [flake8](https://pypi.python.org/pypi/flake8)
    - use for both Doksit package source code (`doksit/*`) and tests
    - install it via `requirements-dev.txt`

2. [Google Python Style Guide](http://google.github.io/styleguide/pyguide.html)

    - for checking code complexity, anti Python idioms and patterns use [pylint](https://www.pylint.org/)
    - use only for the Doksit source code (`doksit/*`)

3. [PEP 20](https://www.python.org/dev/peps/pep-0020/)

    - especially first two lines

And my own proposals:

- use [type hints](https://www.python.org/dev/peps/pep-0484/)
- use Doksit docstring style
- do **NOT** glue for example 50 lines of code together, please use blank line to separete logic

    - before a compound statemnt (`if`, `while` etc.) is 1 blank line
    - the same goes for the `return` statement

I highly recommend you to browse the `doksit/` directory and see, how I'm writing the codes (if you find an antipattern, too complex code, let me know).

## Python version

Doksit is only Python 3.x compatible and this isn't going to be changed (by this I mean not to be 2.7 backward compatible).

## Packages

### CLI

Commands are created via [click](http://click.pocoo.org/6/) package and each command (if it's body would be long) has own module, where are defined main (control) functions / classes.

Eg. `doksit api` subcommand has own module `doksit/api.py`.

### Testing

Doksit uses [pytest](http://docs.pytest.org/en/latest/) for testing and [pytest-cov](http://pytest-cov.readthedocs.io/en/latest/readme.html) plugin for writting better tests (eg. what part of code isn't tested).

#### Organizing tests

Directory structure is same as inside the `doksit/` directory.

Each class / function has own test module, which is named as the object names. For example if a class is named `SuperLongName`, then the name will be:

```
test_super_long_name.py
```

Tests themself are organized in the same way as they are defined in the modules. Name of test functions copy the name of method / function with optional suffix like `_with_config`.

If a class has more then two methods and there is a need to write multiple tests for a one method (testing different conditions etc.), please separate the methods like:

```python
def test_method_a():
    pass


##############################################################################


def test_method_b_with_config():
    pass


def test_method_b_without_config():
    pass


##############################################################################


def test_method_c():
    pass
```
