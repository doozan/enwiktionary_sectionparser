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
import mwparserfromhell as mwparser


class PosParser():

    TYPE_TO_TEMPLATES = {
        "alti": [   "alti", "inline alt forms", "altform-inline", "zh-alt-inline", ],
        "syn": [ "syn", "synonyms", "syn-lite", "seeSynonyms", "syndiff", "synsee", ],
        "ant": [ "ant", "antonyms", "antonym", "ant-lite", ],
        "hyper": [ "hyper", "hypernyms", ],
        "hypo": [ "hypo", "hyponyms", ],
        "holo": [ "holo", "holonyms", "hol", ],
        "mero": [ "mero", "meronyms", "mer" ],
        "tropo": [ "troponyms", ],
        "comero": [ "comeronyms", ],
        "cot": [ "cot", "coordinate terms", "coordinate_terms", ],
        "parasyn": [ "nearsyn", "parasynonyms", "parasyn", "par", "near-syn", "near-synonyms" ],
        "perfect": [ "perfectives", ],
        "imperfect": [ "imperfectives" ],
        "active": [ "active-voice", ],
        "midvoice": [ "middle-voice", ],
        "co": [ "co", "coi", "collocation", "coa", "zh-co", ],
        "cot": [ "cot", "coord", "coordinate terms", "coord-lite", ],
        "ux": [ "ux", "usex", "uxi", "ux-lite", "uxa", "prefex", "prefixusex", "afex", "sufex", "suffixusex", "afex", "affixusex" ] \
            + sum([[k + "-x", k + "-x-inline", k + "-usex", k + "-usex-inline"] for k in ["ja", "hi", "ko", "th", "ur", "zh", "km", "ne", "ryu"]], []),
        "quote": [ "Q", "quote", "quotei", "quote-book", "quote-web", "quote-text", "quote-journal", "quote-av",
            "quote-song", "quote-video game", "quote-newsgroup", "quote-news", "quote-book-ur", "quote-hansard",
            "quote-lite", "quote-mailing list", "quote-us-patent", "quote-wikipedia",
            "grc-cite",
            "zh-q",
            "seeCites", "seemoreCites", "seeMoreCites" ],

        # These aren't UX, but are better served when formatted as #: so they're not hidden by default
        "rfquote": [ "rfquote", "rfquote-sense", "rfquotek", "rfex" ],

        "sense": [ "lb", "lb-lite", "senseid", "defdate", "rfc-sense", "n-g", "q", "qual", "qualifier", "gloss", "ng",
            "non-gloss definition", "place", "taxon", "tcl" ],
    }

    ALL_NYMS = [ "syn", "ant", "hyper", "hypo", "holo", "merq", "tropo", "comero", "cot", "parasyn", "perfect", "imperfect", "active", "midvoice", "alti" ]

    all_templates = []
    template_to_type = {}
    for k, templates in TYPE_TO_TEMPLATES.items():
        all_templates += templates
        for template in templates:
            template_to_type[template] = k

    ALL_TYPE_TEMPLATES = "|".join(sorted(set(all_templates)))
    TEMPLATE_PATTERN = r"\{\{\s*(?P<t>" + ALL_TYPE_TEMPLATES + r")\s*\|"
    re_templates = re.compile(TEMPLATE_PATTERN)
    #print(all_templates)
    #print(TYPE_PATTERN)
    #exit()

    def __init__(self, section, log=None):
        """
        section = enwiktionary_sectionparser.Section
        log = list to append log messages
        """
        self._log = log
        self._changes = []
        self._section = section

        self.headlines, self.senses, self.footlines = self.parse(section)

        if self.headlines and self.senses:
            empty_count = sum(1 for l in self.headlines if l.strip() == "")

            trailing_empty = 0
            while (self.headlines and self.headlines[-1].strip() == ""):
                self.headlines.pop()
                trailing_empty += 1

            # Usually entries with [[File:]] or {{rfc}} or {{wikipedia}} - don't mess with existing newlines
            if trailing_empty != empty_count:
                pass
            elif trailing_empty == 1:
                pass
            elif trailing_empty == 0:
                self._changes.append("added empty line between header and senses per [[WT:NORM]]")
            elif trailing_empty > 1:
                self._changes.append("one empty line between header and senses per [[WT:NORM]]")

    def log(self, error, section, line):
        if self._log is None:
            return
        lineage = list(section.lineage) if section else [ self.title, "" ]
        page = lineage.pop()
        path = ":".join(reversed(lineage))
        self._log.append((error, path, line))

    @property
    def section(self):
        return self._section

    @property
    def changelog(self):
        summary = []
        for item in self._changes:
            if item not in summary:
                summary.append(item)
        return "; ".join(summary)


    def parse(self, section):

        wikilines = section.content_wikilines

        first_sense = 0
        while first_sense<len(wikilines) and (not wikilines[first_sense] or wikilines[first_sense][0] not in "*#:"):
            first_sense += 1

        last_sense = len(wikilines)-1
        while last_sense > first_sense and (not wikilines[last_sense].strip() or wikilines[last_sense][0] not in "*#:"):
            last_sense -= 1

        sense_list = self.parse_list(wikilines[first_sense:last_sense+1], section)
        if not sense_list:
            # TODO Better error handling here
            return wikilines, [], []

        self.set_item_types(sense_list)

        return wikilines[:first_sense], sense_list, wikilines[last_sense+1:]


    def parse_list(self, all_items, section):
        list_items = []

        prev_item = None
        prev_level = None

        for line in all_items:
            if not line.strip():
                self._changes.append("removed newline in list")
                continue

            m = re.match(r'([#:*]+)(\s*)(.*)(\s*)', line, flags=re.DOTALL)
            if not m:
#                print("FAILED processing list, found non_list_item", section.path, line)
                return

            prefix = m.group(1)
            space = m.group(2)
            data = m.group(3)
            trailing_space = m.group(4)

            if not data:
                self._changes.append("removed empty item")
                continue

            level = len(prefix)
            style = prefix[-1]

            if prev_item and level > prev_item.level:
                parent = prev_item

            elif prev_item:
                parent = prev_item.parent
                while parent and level <= parent.level:
                    parent = parent.parent
            else:
                parent = None

            if parent:
                idx = len(parent._children)
                name = parent.name + style + str(idx+1)
            else:
                idx = len(list_items)
                name = style + str(idx+1)

            if space != " ":
                self._changes.append("one space between format and line data per [[WT:NORM]]")

            if trailing_space:
                self._changes.append("remove trailing spaces per [[WT:NORM]]")

            item = ListItem(parent, prefix, data, name)
            if parent:
                parent._children.append(item)
            else:
                list_items.append(item)

            prev_item = item

        return list_items

    def set_item_types(self, items):

        for item in items:

            template_types = []
            is_single_template = False
            if "{{" in item.data:
                wiki = mwparser.parse(item.data)
                first_template = None
                for t in wiki.ifilter_templates(recursive=False):
                    template_type = self.template_to_type.get(t.name.strip())
                    if template_type:
                        template_types.append(template_type)

                        if not first_template:
                            first_template = t

                if first_template:
                    # Strip html comments before checking that text is a single template
                    text = strip_safe_templates(wiki)
                    text = strip_html_comments(item.data)
                    # TODO: Strip categories
                    text = strip_ref_tags(text)

                    template_text = str(first_template)
                    template_text = strip_html_comments(template_text)
                    template_text = strip_ref_tags(template_text)

                    is_single_template = template_text.strip() == text.strip()
#                    print([template_text, text])

            if template_types:
                if not all(t == template_types[0] for t in template_types):
                    item._type = "bad"
                else:
                    template_type = template_types[0]

                    if template_type != "sense" and not is_single_template:
                        item._type = "bad"

                    # "zh-x" may be a quote or a ux, depending on the existence of a "ref=" parameter
                    elif first_template.name == "zh-x" and first_template.has("ref"):
                        item._type = "quote"

                    else:
                        item._type = template_type

            else:
                # RQ: templates are quotes
                if re.match(r"\s*{{\s*(R|RQ):", item.data):
                    item._type = "quote"

                elif is_bare_quote(item):
                    item._type = "bare_quote"

                elif is_bare_uxi(item):
                    item._type = "bare_uxi"

                elif is_bare_ux(item):
                    item._type = "bare_ux"

                else:
                    item._type = "unknown"


        # Special handling for top level senses and
        # "sense" parents, "senses" whose children are all subsenses
        if items and (not items[0].parent or items[0].parent._type == "sense") \
                 and all(i._type in ["sense", "unknown"] for i in items) \
                 and all("[[" in i.data and "]]" in i.data for i in items if i._type == "unknown"):
            for i in items:
                i._type = "sense"

        # TODO: update callers to handle 'bad' as a line type
        for i in items:
            if i._type == "bad":
                i._type = "unknown"

        for item in items:
            if item._children:
                self.set_item_types(item._children)



    def __str__(self):
        return "\n".join(map(str, self.headlines + [""] + self.senses + self.footlines))


def strip_html_comments(text):
    return re.sub(r"\s*<!--.*?-->", "", text, flags=re.DOTALL)

def strip_ref_tags(text):
    return re.sub(r"(<\s*ref[^<>/]*>.*?<\s*/\s*ref\s*>|<\s*ref[^<>/]*/\s*>)", "", text, flags=re.DOTALL)


SAFE_TEMPLATES = ["att", "attn", "attention", "C", "c", "top", "topic", "anchor"]
def strip_safe_templates(wiki):
    text = str(wiki)
    to_remove = [str(t) for t in wiki.ifilter_templates() if t.name in SAFE_TEMPLATES]
    for old in to_remove:
        text = text.replace(old, "")
    return text

def has_link(text):
    return bool(re.search(r"(\[\[[^\[\]]+\]\]|{{\s*(l|m)\s*\|)", text))

def strip_wikilinks(text):
    # just good enough for use by is_sentence
    return re.sub(r"\[\[(?:[^\[\]]*[|])?(.*?)\]\]", r"\1", text)

def strip_template_links(text):
    # only good enough for use by is_sentence
    return re.sub(r"{{(?:l|m)[|].*?[|](.*?)}}", r"\1", text)

def is_sentence(text):
    text = strip_wikilinks(text)
    text = strip_template_links(text)
    return bool(re.match(r"""^\W*[A-Z].*[.?!]["'\W]*$""", text))

def is_italic(text):
    # Returns True if entire string is enclosed in '' italic wikimarkup
    ital = "(?<!')(?:'{2}|'{5})(?!')"
    return re.match(fr"{ital}.*{ital}$", text) and not re.search(ital, text[2:-2])

def is_bold(text):
    # Returns True if entire string is enclosed in ''' bold wikimarkup
    bold = "(?<!')(?:'{3}|'{5})(?!')"
    return re.match(fr"{bold}.*{bold}$", text) and not re.search(bold, text[3:-3])

def is_bare_uxi(item):
    return not item._children and re.match(r"{{lang[|][^{}]*}} — [A-Za-z\"',;.?! ]+$", item.data)

def is_bare_ux(item):

    passage = str(item.data)
    #print("is_bare_ux?", passage)

    # Must be an italic string
    if not is_italic(passage):
        #print("not italic")
        return False

    # Must contain at least 1 bold item
    if not passage.count("'''") > 1:
        #print("no bold")
        return False

    # Should not contain links
#    if has_link(passage):
#        #print("has link")
#        return False

    # TODO: English passages must be sentences

    if not item._children:
        #print("no children")
        return True

    # If it contains a child, should only have 1 child
    if len(item._children) > 1:
        #print("too many children")
        return False

    # TODO: English items should not have a translation

    #print("scanning child", item._children[0])
    return is_translation(item._children[0])


def is_translation(item):

    translation = str(item.data)

    # Must start with a capital and end with punctuation
    if not is_sentence(translation):
        #print("not a sentence")
        return False

    # Must contain at least 1 bold item
    if not translation.count("'''") > 1:
        #print("no bold")
        return False

    # Translation should not have a child (TODO: Not necessarily true, may contain transliteration)
    if item._children:
        #print("has children")
        return False

    return True



# This is used in a re.findall, so everything should be non-capturing
_quote_start = r"""
        (?:<!--.*?-->\s*)?                                             # html comment
        (?:
            (?:'''\s*)?                                                # optional bold
                {{\s*
                (?:c\.|ca\.|circa|circa2|a\.|ante|post|rfdate|rfdatek)  # date templates
                \s*\|
            |
            (?:(?:circa|early|late|mid|ca[.]?|c[.]?|a[.]?)?)?\s*       # optional date qualifier
            '''\s*                                                     # bold
                (?:(?:circa|early|late|mid|ca[.]?|c[.]?|a[.]?)?)?\s*   # optional date qualifier
                (?:
                    \d{1,2}(?:st|nd|rd|th)                             # 1st-99th
                    |
                    (?:\d|1\d|20)\d{2}                                 # year 100-2099
                    |
                    (?:(?:\d|[12]\d|30|31)\b\s*)?                        # 1-31
                    (?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:rch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b
                )
        )
    """
_quote_start_pattern = fr"(?x)\s*{_quote_start}"
_quote_line_pattern = fr"""(?x)
    ^
    (?P<prefix>
        [#:*]+
    )
    +\s*
    (?P<quote>
        {_quote_start}
        .*
    )
    $
"""

BARE_QUOTE_START_RX = re.compile(_quote_start_pattern)
BARE_QUOTE_LINE_RX = re.compile(_quote_line_pattern, re.MULTILINE)

def is_bare_quote(item):
    return bool(re.match(BARE_QUOTE_START_RX, item.data))

class ListItem():
    def __init__(self, parent, prefix, data, name):
        self.parent = parent
        self.level = len(prefix)
        self.prefix = prefix
        self.style = prefix[-1]
        self.data = data
        self.name = name

        self._children = []
        self._type = None

#    @property
#    def level(self):
#        level = 1
#        parent = self.parent
#        while parent:
#            level += 1
#            parent = parent.parent
#        return level

#    @property
#    def prefix(self):
#        prefix = [self.style]
#        parent = self.parent
#        while parent:
#            prefix.insert(0, parent.style)
#            parent = parent.parent
#
#        return "".join(prefix)

    def __str__(self):
        if self._children:
            return self.prefix + " " + self.data + "\n" + "\n".join(map(str, self._children))
        return self.prefix + " " + self.data


