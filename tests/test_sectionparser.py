import pytest
import enwiktionary_sectionparser as enwiktparser
from enwiktionary_sectionparser.sectionparser import SectionParser, Section, text_to_wikilines

def test_text_to_wikilines():

    text = """\
{{template}}
==Section==
{{header}}
<!-- comment
comment -->
{{template|
template}} {{t
|template}}
"""
    expected = [
        '{{template}}',
        '==Section==',
        '{{header}}',
        '<!-- comment\ncomment -->',
        '{{template|\ntemplate}} {{t\n|template}}'
    ]

    res = text_to_wikilines(text)
    print(res)
    assert res == expected



def test_is_section():
    assert Section.is_category("[[Category:en:Trees]]") == True
    assert Section.is_category("{{c|en|Trees}}") == True
    assert Section.is_category("# {{c|en|Trees}}") == False
    assert Section.is_category("[[Category:en:Trees]] text") == False
    assert Section.is_category("[[Category:en:Trees]] <!--text-->") == True
    assert Section.is_category("<!-- [[Category:en:Trees]] -->") == False
    assert Section.is_category("   [[Category:en:Trees]]    {{c|en|Trees}}   ") == True

def test_has_category():
    assert Section.has_category("[[Category:en:Trees]] text") == True
    assert Section.has_category("test text") == False

def test_basic1():
    text = """\
{{also|Dictionary}}
==  English==
blah

=== Noun  ======= <!-- This is a comment -->
blah

<!--
=== Adjective ===
blah
!-->


----
==Thai==   

blah

====Noun====
# text


----


==Spanish==
[[Category:blah]]

=== Noun ====

[[Category:blah2]]
# blah

====Usage notes====
* info

===Anagrams===
# anagrams

===Further reading===
* {{R:DRAE}}
"""

    result = """\
{{also|Dictionary}}
==English==
blah

===Noun=======
<!-- This is a comment -->
blah

<!--
=== Adjective ===
blah
!-->

==Thai==
blah

====Noun====
# text

==Spanish==

===Noun====
# blah

====Usage notes====
* info

===Anagrams===
# anagrams

===Further reading===
* {{R:DRAE}}

[[Category:blah]]
[[Category:blah2]]
"""

    parsed = SectionParser(text, "test")

#    print(parsed._header)

    assert len(parsed._children) == 3
    assert len(list(parsed.ifilter_sections())) == 9

    notes = list(parsed.ifilter_sections(matches=lambda x: x.title == "Usage notes"))
    assert len(notes) == 1
    assert notes[0].path == "Spanish:Noun=:Usage notes"

    res = str(parsed)
    assert res.splitlines() == result.splitlines()

def test_l2_joiner():
    text = """\
==Translingual==
----
==English==

----
==Thai==

----

==Spanish==


----

"""

    result = """\
==Translingual==

==English==

==Thai==

==Spanish==
"""

    parsed = SectionParser(text, "test")
    res = str(parsed)
    print(res)
    assert res.splitlines() == result.splitlines()


def test_categories_inside_open_templates():
    text = """\
==English==

===Noun===
# blah {{blah|
[[Category:en:blah]]
blah}}
# bar\
"""

    parsed = SectionParser(text, "test")
    res = str(parsed)
    print(res)
    assert res.splitlines() == text.splitlines()


def test_content_wikilines():
    text = """\
===Noun===

# multiline_template {{template|foo
|bar}}
# simple item
# multiline_comment and multiline_template <!--
# commented line
--> {{open_template|test=
template line
}}
# ignore open template inside html comment <!--
# {{commented|open|template
-->
# ignore closing template inside comment {{template|
blah <!-- }} -->
ending }}
#: multiple multiline_templates {{ux|en|1
}}{{ux|en|2
}}{{ux|en|3
}}
# {{trailing unclosed
"""
    expected = [
        '# multiline_template {{template|foo\n|bar}}',
        '# simple item',
        '# multiline_comment and multiline_template <!--\n# commented line\n--> {{open_template|test=\ntemplate line\n}}',
        '# ignore open template inside html comment <!--\n# {{commented|open|template\n-->',
        '# ignore closing template inside comment {{template|\nblah <!-- }} -->\nending }}',
        '#: multiple multiline_templates {{ux|en|1\n}}{{ux|en|2\n}}{{ux|en|3\n}}',
        '# {{trailing unclosed'
    ]

    parsed = SectionParser(text, "test")
    section = parsed.filter_sections(matches="Noun")[0]
    assert section.content_wikilines == expected


def test_general():

    page_text = """\
==English==

===Etymology 1===

====Noun====

====Verb====

=====Usage notes=====

====Adjective=====

===Etymology 2===

====Noun====

===References===

==Japanese==

===Noun===
"""
    page_title = "test"

    entry = enwiktparser.parse(page_text, page_title)
    assert len(entry.filter_sections()) == 11
    assert len(entry.filter_sections(recursive=False)) == 2
    assert len(entry.filter_sections(matches="Etymology")) == 2
    assert len(entry.filter_sections(matches="Noun")) == 3
    assert len(entry.filter_sections(matches=lambda section: section.title in ["Verb", "Noun"])) == 4


    japanese = next(entry.ifilter_sections(matches="Japanese", recursive=False), None)
    assert len(japanese.filter_sections()) == 1
    japanese_nouns = japanese.filter_sections(matches="Noun")
    assert len(japanese_nouns) == 1
    jnoun = japanese_nouns[0]
    assert jnoun.path == "Japanese:Noun"

    japanese_verbs = japanese.filter_sections(matches="Verb")
    assert len(japanese_verbs) == 0

    ety1 = entry.filter_sections(matches="Etymology")[0]
    ety2 = entry.filter_sections(matches="Etymology")[1]

    verb = ety1.filter_sections(matches="Verb")[0]
    verb.reparent(ety2)

    print("---")
    print(entry)
    print("---")

    assert str(entry) == """\
==English==

===Etymology 1===

====Noun====

====Adjective=====

===Etymology 2===

====Noun====

====Verb====

=====Usage notes=====

===References===

==Japanese==

===Noun===\
"""


    adj = ety1.filter_sections(matches="Adjective=")[0]
    # Re-parenting the section will cleanup the stray =
    adj.reparent(ety2, 0)

    assert str(entry) == """\
==English==

===Etymology 1===

====Noun====

===Etymology 2===

====Adjective====

====Noun====

====Verb====

=====Usage notes=====

===References===

==Japanese==

===Noun===\
"""
