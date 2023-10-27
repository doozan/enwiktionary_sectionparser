# Copyright (c) 2023 Jeff Doozan
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

_separators = (
    "<!--", "-->",
    r"<\s*nowiki\s*>", r"<\s*/\s*nowiki\s*>",
    r"<\s*ref[^/]*?>", r"<\s*/\s*ref\s*>",
    r"<\s*math\s*>", r"<\s*/\s*math\s*>",
    r"(?<!\\){{", "}}",
    r"(?<!{){\|", r"\|}",
    r"\n"
)
_pattern = "(" + "|".join(_separators) + ")"
_regex = re.compile(_pattern, re.IGNORECASE)

def wiki_splitlines(text, return_state=False):
    """
    Like str.splitlines(), but doesn't split on newlines inside
    html comments, <nowiki> tags and {{ templates }}

    if return_state is True,
        the last value returned contains information about unclosed items
    """

    template_depth = 0
    in_comment = False
    in_nowiki  = False
    in_ref = False
    in_math = False
    in_table = False

    prev_pos = 0
    for m in re.finditer(_regex, text):
        item = m.group(0)

        # normalize tags for easier matching below
        if item.startswith("<") and item.endswith(">"):
            item = item.replace(" ", "").lower()

        if in_comment:
            if item == "-->":
                in_comment = False
            continue

        # opening html comments can appear anywhere and take precedence (except inside <pre>?)
        if item == "<!--":
            in_comment = True
            continue

        if in_nowiki:
            if item == "</nowiki>":
                in_nowiki = False
            continue

        if item == "{|":
            in_table = True

        if item == "|}":
            in_table = False

        if item == "{{":
            template_depth += 1

        elif item == "}}" and template_depth:
            template_depth -= 1

        elif item == "<nowiki>":
            in_nowiki = True

        elif item.startswith("<ref"):
            in_ref = True

        elif item == "</ref>":
            in_ref = False

        elif item.startswith("<math"):
            in_math = True

        elif item == "</math>":
            in_math = False

        if in_comment or in_nowiki or in_ref or in_math or in_table or template_depth:
            continue

        if item == "\n":
            yield text[prev_pos:m.end()-len("\n")]
            prev_pos = m.end()

    if prev_pos != len(text):
        if text.endswith("\n") and prev_pos != len(text)-len("\n"):
            yield text[prev_pos:-1*len("\n")]
        else:
            yield text[prev_pos:]

    if return_state:
        state = min(0xFF, template_depth) & 0xFF
        if in_ref:
            state |= 0x0100
        if in_nowiki:
            state |= 0x0200
        if in_comment:
            state |= 0x0400
        if in_math:
            state |= 0x0800
        if in_table:
            state |= 0x1000
        yield state

