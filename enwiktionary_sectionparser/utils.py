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

def wiki_finditer(pattern, text, flags=0, invert_matches=False, match_comments=False, match_nowiki=False, match_ref=False, match_math=False, match_pre=False, match_table=False, match_templates=False, match_special=False, return_final_state=False):

    """
    matches pattern within wiki formatted text, with basic awareness
    of templates, html comments and <nowiki> tags

    if invert_matches is set, it will return only instances where pattern would be discarded for being inside the non-permitted wiki elements
    """

    in_comment = False
    in_nowiki  = False
    in_ref = False
    in_math = False
    in_pre = False
    in_table = False
    in_special = False
    template_depth = []

    separators = []
    tags = []
    if not match_comments:
        separators += ["<!--", "-->"]
    if not match_nowiki:
        tags.append("nowiki")
    if not match_ref:
        tags.append("ref")
    if not match_math:
        tags.append("math")
    if not match_pre:
        tags.append("pre")
    if not match_table:
        separators += [r"(?<![{]){\|", r"\|}(?!})"]
    if not match_templates:
        separators += [r"{{", "}}"]

    if pattern in separators:
        raise ValueError(f"Invalid search value: {start}")

    match_items = []
    if separators:
        match_items.append("(?P<_sep>" + "|".join(separators) + ")")
        #match_items.append("(?P<_sep>" + "|".join(separators + [tag_pattern]) + ")")

    if isinstance(match_templates, list):
        # When given a list of templates that should allow their contents to be matched,
        # capture the template name when matching {{
        template_start = r"(?P<_tmpl_start>{{(\s|<--.*-->)*(?P<_tmpl_name>[^\n|}{]*)(\s*|<!--.*-->)*(?=[}|]))"
        template_end = "(?P<_tmpl_end>}})"
        named_templates = template_start + "|" + template_end
        match_items.append(named_templates)

    if tags:
        open_tags = r"<\s*(?P<_tag_start>" + "|".join(tags) + r")(?:\s[^/>]*)?>"
        close_tags = r"<\s*\/\s*(?P<_tag_end>" + "|".join(tags) + r")\s*>"
        single_tags = r"<\s*(?P<_single_tag>" + "|".join(tags) + r")\b[^/>]*[/]\s*>"
        tag_pattern = "(?i:" + open_tags + "|" + close_tags + "|" + single_tags + ")"
        match_items.append(tag_pattern)


    if not match_special:
        match_items.append(r"(?P<_special_start>\[\[\s*[:]?\s*(?i:file|media|special)\s*:)|(?P<_special_end>\]\])")

    match_items.append("(?P<_pat>" + pattern + ")")

    pattern = "|".join(match_items)

    start_pos = None
    for m in re.finditer(pattern, text, flags):
        if m.group("_pat"):
            if not (in_comment or in_nowiki or in_ref or in_math or in_pre or in_table or in_special or template_depth):
                if not invert_matches:
                    yield m
            elif invert_matches:
                yield m
            continue

        cmd = None
        if m.group('_tag_start'):
            cmd = m.group('_tag_start').lower()
        elif m.group('_tag_end'):
            cmd = "/" + m.group('_tag_end').lower()

        elif m.group('_special_start'):
            cmd = "[[special"
        elif m.group('_special_end'):
            cmd = "]]"

        elif m.group('_single_tag'):
            continue
        elif m.group('_sep'):
            cmd = m.group('_sep')

        elif m.group("_tmpl_start"):
            if template_depth:
                cmd = "{{"
            elif m.group("_tmpl_name") and m.group("_tmpl_name") not in match_templates:
                cmd = "{{"
            else:
                continue
        elif m.group("_tmpl_end"):
            cmd = "}}"

        else:
            raise ValueError("unexpected")

        # html comments, <pre> and <math> consume everything until they are closed
        if in_comment:
            if cmd == "-->":
                in_comment = None
            continue

        if in_math:
            if cmd == "/math":
                in_math = None
            continue

        if in_pre:
            if cmd == "/pre":
                in_pre = None
            continue

        # opening html comments can appear anywhere and take precedence (except inside <pre>?)
        if cmd == "<!--":
            in_comment = m
            continue

        # already handled above, anything matching here is errant and can be ignored
        elif cmd in ["-->", "/math", "/pre"]:
            continue

        elif cmd == "/nowiki":
            in_nowiki = None

        elif cmd == "{|":
            in_table = m

        elif cmd == "|}":
            in_table = None

        elif cmd == "{{":
            template_depth.append(m)

        elif cmd == "}}":
            if template_depth:
                template_depth.pop()
            # warn?

        elif cmd == "nowiki":
            in_nowiki = m

        elif cmd == "ref":
            in_ref = m

        elif cmd == "/ref":
            in_ref = None

        elif cmd == "math":
            in_math = m

        elif cmd == "pre":
            in_pre = m

        elif cmd == "[[special":
            in_special = m

        elif cmd == "]]":
            in_special = None

        else:
            print("Unexpected match", cmd, m)
            raise ValueError("Unexpected match", cmd)

    if return_final_state:
        yield {k:v for k, v in [
            ("open_ref", in_ref),
            ("open_nowiki", in_nowiki),
            ("open_comment", in_comment),
            ("open_math", in_math),
            ("open_pre", in_pre),
            ("open_table", in_table),
            ("open_templates", template_depth),
        ] if v}

def wiki_splitlines(text, return_state=False):
    prev_pos = 0

    state = None
    res = []
    for m in wiki_finditer("\n", text, return_final_state=return_state):
        if return_state and isinstance(m, dict):
            state = m
            break

        yield text[prev_pos:m.start()]
        prev_pos = m.end()

    if prev_pos != len(text):
        if text.endswith("\n") and prev_pos != len(text)-len("\n"):
            yield text[prev_pos:-1*len("\n")]
        else:
            yield text[prev_pos:]

    if return_state:
        yield state

def wiki_search(pattern, text, **kwargs):
    return wiki_finditer(pattern, text, **kwargs)

def wiki_replace(pattern, replacement, text, regex=False, **kwargs):

    prev_pos = 0

    if not regex:
        pattern = re.escape(pattern)
        new = replacement
    else:
        if "(?" in pattern or"(!" in pattern or "(<" in pattern:
            raise ValueError("lookahead/behind not supported")

    parts = []
    state = None
    for m in wiki_finditer(pattern, text, return_final_state=True, **kwargs):
        if isinstance(m, dict):
            state = m
            break

        parts.append(text[prev_pos:m.start()])
        if regex:
            new = re.sub(pattern, replacement, m.group(0))

        parts.append(new)
        prev_pos = m.end()

    if prev_pos != len(text):
        parts.append(text[prev_pos:])

    return "".join(parts)
