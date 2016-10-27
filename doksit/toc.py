"""
Here are defined main objects for running the following command:

    $ doksit toc
"""

import os.path
import urllib

from typing import List, Tuple

from doksit.helpers import get_toc_file_path
from doksit.models import Base, VARIABLE_REGEX


BULLET_POINT = {
    1: "- ",
    2: 4 * " " + "- ",
    3: 8 * " " + "- ",
    4: 12 * " " + "- ",
    5: 16 * " " + "- ",
    6: 20 * " " + "- "
}


class TableOfContents:
    """
    In this class are defined methods for generating the table of contents.

    The main method is `self.generate_toc`.
    """

    @staticmethod
    def create_bullet_point(heading: Tuple[int, str, str],
                            url_path: str) -> str:
        """
        Create a Markdown bullet point with a link to the heading.

        Arguments:
            heading:
                Information about the heading. First is a heading level, second
                original heading and third is an encoded variant.
            url_path:
                Absolute URL path (on GitHub) to a file containing that
                heading.

        Returns:
            The Markdown bullet point with the link.

        Example: (markdown)
            - [Hello](https://github.com/.../master/docs/foo.md#hello)
        """
        heading_level, original_heading, encoded_heading = heading

        bullet_point = BULLET_POINT[heading_level]
        link_description = "[" + original_heading + "]"
        link_source = "(" + url_path + encoded_heading + ")"

        return bullet_point + link_description + link_source

    @staticmethod
    def encode_heading(heading: str) -> str:
        """
        Encode the given heading for a CSS ID attribute.

        Arguments:
            heading:
                Markdown heading without `#` characters.

        Returns:
            The encoded heading.

        Example:
            "#about-docstrings"
        """
        encoded_heading = urllib.parse.quote_plus(heading, encoding="utf-8") \
            .replace("+", "-") \
            .lower()

        return "#" + encoded_heading

    def find_headings(self, file_path: str) -> List[Tuple[int, str, str]]:
        """
        Find in the given file Markdown headings.

        Arguments:
            file_path (str):
                Absolute path to a Markdown file.

        Returns:
            Metadata about headings. First item is a heading level, second
            origional heading and third an encoded variant.
        """
        with open(file_path) as file:
            file_content = file.read()

        split_content = file_content.split("\n")
        is_code_block = False
        headings = []

        for line in split_content:
            if line.startswith("```"):
                if is_code_block:
                    is_code_block = False
                else:
                    is_code_block = True

            elif not is_code_block:
                if line.startswith("# "):
                    heading = line[2:]
                    headings.append((1, heading, self.encode_heading(heading)))

                elif line.startswith("## "):
                    heading = line[3:]
                    headings.append((2, heading, self.encode_heading(heading)))

                elif line.startswith("### "):
                    heading = line[4:]
                    headings.append((3, heading, self.encode_heading(heading)))

                elif line.startswith("#### "):
                    heading = line[5:]
                    headings.append((4, heading, self.encode_heading(heading)))

                elif line.startswith("##### "):
                    heading = line[6:]
                    headings.append((5, heading, self.encode_heading(heading)))

                elif line.startswith("###### "):
                    heading = line[7:]
                    headings.append((6, heading, self.encode_heading(heading)))

        return headings

    def generate_file_toc(self, directory: str, file_path: str) -> str:
        """
        Generate the table of contents for the given file path.

        Arguments:
            directory:
                Absolute path to the `docs/` directory.
            file_path:
                Relative path to a Markdown file.

        Returns:
            The generated file TOC.

        Example: (markdown)
            - [<file_title>](<absolute_URL_path_to_this_title)
                - [<heading_level_1](<abs_URL_path_to_this_title)
        """
        validated_file_path = self.validate_file_path(directory, file_path)
        headings = self.find_headings(validated_file_path)

        file_toc = ""
        url_path = Base().repository_prefix + "docs/" + file_path

        for heading in headings:
            file_toc += self.create_bullet_point(heading, url_path) + "\n"

        return file_toc

    def generate_toc(self, is_inside: bool) -> None:
        """
        Generate the table of contets and put it into `docs/README.md`.

        Arguments:
            is_inside:
                If a user is inside the `docs/` folder or outside.
        """
        toc_file_path = get_toc_file_path(is_inside)

        with open(toc_file_path) as file:
            file_content = file.read()

        files = VARIABLE_REGEX.findall(file_content)
        docs_directory = toc_file_path.rstrip("_toc.md")

        for file in files:
            file_toc = self.generate_file_toc(docs_directory, file)
            file_variable = "{{ " + file + " }}"

            file_content = file_content.replace(file_variable, file_toc)

        with open(os.path.join(docs_directory, "README.md"), "w") as file:
            file.write(file_content)

    @staticmethod
    def validate_file_path(directory: str, file_path: str) -> str:
        """
        Validate the given file path to a Markdown file.

        Arguments:
            directory:
                Absolute path to the `docs/` directory
            file_path:
                Relative path to the Markdown file.

        Returns:
            The absolute file path to the Markdown file.

        Raises:
            ValueError:
                Invalid file path (template variable) in the `docs/_toc.md`.
        """
        absolute_path = os.path.join(directory, file_path)

        if os.path.exists(absolute_path):
            pass
        else:
            message = (
                "Invalid file path '{{{{ {file_path} }}}}' in the "
                "`docs/_toc.md`"
            ).format(file_path=file_path)

            raise ValueError(message)

        return absolute_path
