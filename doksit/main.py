import re

from doksit.utils import OrderedDict

class_regex = re.compile("^class (\w+):?|\(")
method_regex = re.compile("^    def ([\w_]+)")
function_regex = re.compile("^def ([\w_]+)")


def read_file():
    """Read the given file to find names of classes with its methods and
    functions.
    """
    path = "/home/nait-aul/Apps/doksit_env/tests/package/module.py"

    classes = OrderedDict()
    functions = []

    with open(path) as f:
        file = f.readlines()

    for line in file:
        if line.startswith("class"):
            classes[class_regex.search(line).group(1)] = []

        if line.lstrip().startswith("def"):
            if method_regex.search(line):
                method_name = method_regex.search(line).group(1)

                if method_name == "__init__" or \
                        not method_name.startswith("_"):
                    classes[classes.last()].append(method_name)

            if function_regex.search(line):
                functions.append(function_regex.search(line).group(1))

    return classes, functions


if __name__ == "__main__":
    pass
