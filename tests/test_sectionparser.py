import pytest
import enwiktionary_sectionparser as enwiktparser
from enwiktionary_sectionparser.sectionparser import SectionParser, Section

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
blah}}\
"""

    parsed = SectionParser(text, "test")
    res = str(parsed)
    print(res)
    assert res.splitlines() == text.splitlines()

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
