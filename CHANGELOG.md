# Doksit's changelog

## 0.2.0 (27-10-2016)

**Features:**

- support for module docstring (#2)
- added links to source code (#4)
- added `--colored` flag for the `doksit api` command (#19)
- support Markdown links (#22)
- config file (#25)
- choosing, which objects will be in the API (#27)
- added parser for Google Docstring Style with almost all Napoleon (#28)
- added `--smooth` flag for the `doksit api` command (#29)
- choice between A-Z order and user defined objects (#34)
- added API template (#35)

**Improvement:**

- shortened names of classes and functions (#3)
- created `CONTRIBUTING.md` (#7)
- converted unittests to pytests (#6)
- more documentation (#8)
- added backward compatibility with Python 3.x (#12)
- added Travis CI (#13)
- support for specifying language in the `Example:` section (#15)
- check for branch name (proper URL) (#17)
- support for return annotation (#18)
- support for static methods (#20)
- `--title` option for the API output (#26)
- highlight inline codes in the `--colored` output (#31)
- shortened URL in the `--smooth` and `--colored` output (#32)
- support for constructor and properties (#37)
- detect a package (#38)
- add package to sys path if `setup.py` isn't used (#42)
- support title setting in the config (#47)

**Bugfix:**

- don't overwrite used defined arguments (#14)
- invalid source code URL (#21) (Czech language)
- detect code blocks and color it in the `--colored` output (#41)
- only 1 inline code was colored (#48)

