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

class PosParser():

    TYPE_TO_TEMPLATES = {
        "syn": [ "syn", "synonyms", "syn-lite", "seeSynonyms", "syndiff", "synsee", ],
        "ant": [ "ant", "antonyms", "antonym", "ant-lite", ],
        "hyper": [ "hyper", "hypernyms", ],
        "hypo": [ "hypo", "hyponyms", ],
        "holo": [ "holo", "holonyms", "hol", ],
        "merq": [ "mero", "meronyms", ],
        "tropo": [ "troponyms", ],
        "comero": [ "comeronyms", ],
        "cot": [ "cot", "coordinate terms", "coordinate_terms", ],
        "parasyn": [ "nearsyn", "parasynonyms", "parasyn", "par", ],
        "perfect": [ "perfectives", ],
        "imperfect": [ "imperfectives" ],
        "active": [ "active-voice", ],
        "midvoice": [ "middle-voice", ],
        "alti": [   "alti", "inline alt forms", ],
        "co": [ "co", "coi", "collocation", "zh-co", ],
        "cot": [ "cot", "coord", "coordinate terms", "coord-lite", ],
        "ux": [ "ux", "usex", "uxi", "ux-lite", "prefex", "prefixusex", "afex", "sufex", "suffixusex", "afex", "affixusex", "rfex", "rfquotek"] + \
              sum([[k + "-x", k + "-x-inline", k + "-usex", k + "-usex-inline"] for k in ["ja", "hi", "ko", "th", "ur", "zh", "km", "ne"]], []),
        "quote": [ "Q", "quote", "quotei", "quote-book", "quote-web", "quote-text", "quote-journal", "quote-av",
            "quote-song", "quote-video game", "quote-newsgroup", "quote-news", "quote-book-ur", "quote-hansard",
            "quote-lite", "quote-mailing list", "quote-us-patent", "quote-wikipedia",
            "grc-cite",
            "seeCites", "seemoreCites", "seeMoreCites", "rfquote", "rfquote-sense", ],
        "sense": [ "lb", "lb-lite", "senseid", "defdate", "rfc-sense", "n-g", "q", "qualifier", "gloss", "ng" ]
    }

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

    quote_pattern = r"""(?x)
        \s*
        (
            ('''\s*)?                           # optional bold
                {{\s*
                (c\.|circa|circa2|a\.|ante|post|rfdate|rfdatek)    # date templates
                \s*\|
            |
            ((circa|early|late|mid|ca[.]?|c[.]?|a[.]?)?)?\s*          # optional date qualifier
            '''\s*                              # bold
                ((circa|early|late|mid|ca[.]?|c[.]?|a[.]?)?)?\s*          # optional date qualifier
                (
                    \d{1,2}(st|nd|rd|th)            # 1st-99th
                    |
                    (1\d|20)\d{2}                   # year 1000-2099
                )
        )
    """
    QUOTE_RX = re.compile(quote_pattern)


    def __init__(self, section, log=None):
        """
        section = enwiktionary_sectionparser.Section
        log = list to append log messages
        """
        self._log = log

        self.headlines, self.senses, self.footlines, self._changes = self.parse(section)


    def log(self, error, section, line):
        if self._log is None:
            return
#        lineage = list(section.lineage) if section else [ self.title, "" ]
#        page = lineage.pop
#        path = ":".join(reversed(lineage))
        self._log.append((error, path, line))
        return

    @property
    def changelog(self):
        summary = []
        for item in self._changes:
            if item not in summary:
                summary.append(item)
        return "; ".join(summary)


    def parse(self, section):

        changes = []
        header = []
        footer = []
        senses = []

        wikilines = section.content_wikilines

        first_sense = 0
        while first_sense<len(wikilines) and (not wikilines[first_sense] or wikilines[first_sense][0] not in "*#:"):
            first_sense += 1

        if first_sense == len(wikilines):
            return wikilines, [], [], changes

        last_sense = len(wikilines)-1
        while last_sense > first_sense and (not wikilines[last_sense] or wikilines[last_sense][0] not in "*#:"):
            last_sense -= 1

        sense_list = self.parse_list(wikilines[first_sense:last_sense+1], section)
        if not sense_list:
            # TODO Better error handling here
            return wikilines, [], [], changes

        self.set_item_types(sense_list)

        return wikilines[:first_sense], sense_list, wikilines[last_sense+1:], changes


    def parse_list(self, all_items, section):

        list_items = []

        prev_item = None
        prev_level = None

        for data in all_items:
            if data == "":
                self.log("removed_newline", "", "")

            m = re.match(f'[#:*]+', data)
            if not m:
                #self.warn("non_list_item", section, data)
#                print("FAILED processing list, found non_list_item", section.path, data)
                return


            prefix = m.group(0)
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

            old_len = len(data)
            data = re.sub(r'^[#*:]+\s*', '', data)
            if len(data) + len(prefix) + 1 != old_len:
                self.log("whitespace", name, data)

            old_len = len(data)
            data = data.rstrip()
            if len(data) != old_len:
                self.log("whitespace", name, data)

            item = ListItem(parent, prefix, data, name)
            if parent:
                parent._children.append(item)
            else:
                list_items.append(item)

            prev_item = item

        return list_items

    def set_item_types(self, items):

        for item in items:
            m = re.search(self.re_templates, item.data)
            if m:
                item._type = self.template_to_type[m.group('t')]

            else:
                # RQ: templates are quotes
                if re.match(r"\s*{{\s*(R|RQ):", item.data):
                    item._type = "quote"

                # if starts with a bold year, probably a quote
                elif re.match(self.QUOTE_RX, item.data):
                    item._type = "bare_quote"

                # check this after bare quotes, which may also start ''' and end ''
                # lines starting and ending with italics are probably bare ux lines
                elif item.data.startswith("''") and item.data.endswith("''") and not \
                        (item.data.startswith("'''") and not item.data.startswith("'''")):
                    item._type = "bare_ux"

                else:
                    item._type = "unknown"

            if item._children:
                self.set_item_types(item._children)

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


