import pytest
import enwiktionary_sectionparser as parser
import enwiktionary_sectionparser.posparser as posparser
from enwiktionary_sectionparser.posparser import is_sentence, is_bare_ux, is_template, strip_ref_tags, is_bare_quote

def test_basic():
    text = """\
===Noun===
{{en-noun}}

# sense1<ref>
blah blah
</ref>
#: {{ux|en|there's a '''sense1''' in here}}
# sense2
#: {{syn|es|foo|bar}}

{{footer}}
"""

    wikt = parser.parse(text, "test")
    section = wikt.filter_sections(matches="Noun")[0]
    pos = parser.parse_pos(section)

    assert pos.headlines == ['{{en-noun}}']
    assert len(pos.senses) == 2
    assert pos.footlines == ['', '{{footer}}']


def test_item_types():

    text = """\
===Noun===
{{en-noun}}

# {{lb|en|foo}} sense1
## [[subsense]]
##: {{ux|en|there's a '''subsense''' in here}}
# [[sense2]]
#* {{quote-book|lang=en|year=1822|title=foo}}
#: {{syn|es|foo|bar}}<ref>test</ref>
#: ''Jeg skal nok få '''tatt knekken på''' ham til slutt.''
# {{lb|eu|du}} to [[do]]
## to [[do]], [[make]], [[create]], [[produce]]
## to [[cook]]a

{{footer}}
"""

    wikt = parser.parse(text, "test")
    section = wikt.filter_sections(matches="Noun")[0]
    pos = parser.parse_pos(section)

    assert len(pos.senses) == 3
    assert [s._type for s in pos.senses] == ["sense", "sense", "sense"]

    assert [c._type for c in pos.senses[0]._children] == ["sense"]
    subsense = pos.senses[0]._children[0]

    assert [c._type for c in subsense._children] == ["ux"]
    subsense = pos.senses[0]._children[0]

    assert [c._type for c in pos.senses[1]._children] == ["quote", "syn", "bare_ux"]

    assert [c._type for c in pos.senses[2]._children] == ["sense", "sense"]



def test_is_sentence():
    assert is_sentence("This is a sentence.") == True
    assert is_sentence("This is a sentence?") == True
    assert is_sentence("This is a sentence!") == True
    assert is_sentence("''This is a sentence.''") == True
    assert is_sentence("[[this#test|This]] is a sentence!") == True
    assert is_sentence("This is a sentence!") == True
    assert is_sentence("This is not a sentence;") == False
    assert is_sentence("This is not a sentence") == False
    assert is_sentence("this Is not a sentence.") == False


def test_is_template():
    assert is_template('w', "{{w}}") == True
    assert is_template('w', "{{w|{{foo}}\n|bar}}") == True

    assert is_template('w', "{{W}}") == False
    assert is_template('w', "{{w}} foo") == False
    assert is_template('w', "foo {{w}}") == False
    assert is_template('w', "{{w}}<!-- html comment -->") == False

#def test_is_bare_ux():
#    from collections import namedtuple
#    Item = namedtuple('Item', ['data', '_children'])
#    assert is_bare_ux(Item("''Jeg skal nok få '''tatt knekken på''' ham til slutt.''", None)) == True
#

def test_strip_ref_tags():

    assert strip_ref_tags('{{template}}<ref>test</ref>') == "{{template}}"
    assert strip_ref_tags('{{template}}< ref name="blah" >test< / ref >') == "{{template}}"
    assert strip_ref_tags('{{template}}< ref name="blah" />') == "{{template}}"

    assert strip_ref_tags('{{syn|tl|nakawin}} <ref>{{cite-web|tl|url=https://www.sunstar.com.ph/article/360265/genoguin-p-noy-mag-minarcos|title=Genoguin: P-Noy mag-Minarcos?|date=2014-08-10|accessdate=2023-01-15|work=SUNSTAR}}</ref><ref>{{cite-song|tl|url=https://www.soundcloud.com/itsunehonoka/minarcos|title=Minarcos Mo ang Aking Puso (song)|date=2022-05-07}}</ref><ref>{{cite-web|tl|url=https://issuu.com/dochokage/docs/_lcfilia_lasalitaan_e-poster_1_|title=MINARCOS POSTER by Paul Anfrei De Sagun - Issuu|accessdate=2023-01-15|work=issuu.com}}</ref>') == "{{syn|tl|nakawin}} "



def test_newline():
    text = """\
===Adjective===
{{en-adj}}

Test

# sense 1

# sense 2

Test

Test
"""

    wikt = parser.parse(text, "test")
    section = wikt.filter_sections(matches="Adjective")[0]
    pos = parser.parse_pos(section)

    assert len(pos.senses) == 2

    assert str(pos) == """\
{{en-adj}}

Test

# sense 1
# sense 2

Test

Test\
"""

def test_empty():
    text = """\
===Adjective===
{{en-adj}}

# sense 1
#
# sense 2
"""

    wikt = parser.parse(text, "test")
    section = wikt.filter_sections(matches="Adjective")[0]
    pos = parser.parse_pos(section)

    assert len(pos.senses) == 2

    assert str(pos) == """\
{{en-adj}}

# sense 1
# sense 2\
"""



def test_is_bare_quote():

    tests = [
"'''1659''', {{w|Robert South}}, ''Interest Deposed, and Truth Restored''",
"'''24 July, 1659''', {{w|Robert South}}, ''Interest Deposed, and Truth Restored''",
"'''January 26 1751''', {{w|Samuel Johnson}}, ''The Rambler'' No. 90",
"<!-- comment --> '''1659''', {{w|Robert South}}, ''Interest Deposed, and Truth Restored''",
"'''November 2011''', test",
 ]

    from collections import namedtuple
    Item = namedtuple('Item', ['data', 'children'])

    for test in tests:
        assert is_bare_quote(Item(test, None)) == True


def test_strip_wikilinks():
    assert posparser.strip_wikilinks("[[b]]") == "b"
    assert posparser.strip_wikilinks("a [[b]] c") == "a b c"
    assert posparser.strip_wikilinks("[[b]] c") == "b c"
    assert posparser.strip_wikilinks("a [[b]]") == "a b"

    assert posparser.strip_wikilinks("[[test|Test]]") == "Test"
    assert posparser.strip_wikilinks("[[test#Lang|Test]]") == "Test"

def test_strip_template_links():
    assert posparser.strip_template_links("a {{l|en|b}} c") == "a b c"
    assert posparser.strip_template_links("a {{m|en|b}} c") == "a b c"
    assert posparser.strip_template_links("a {{x|en|b}} c") == "a {{x|en|b}} c"

def test_strip_safe_templates():
    assert posparser.strip_safe_templates("a {{b|test}} c") == "a {{b|test}} c"
    assert posparser.strip_safe_templates("a {{attn|en|test}} c") == "a  c"
    assert posparser.strip_safe_templates("a {{C|en|test}} c") == "a  c"
    assert posparser.strip_safe_templates("a {{test|foo{{attn|test}}bar}} c") == "a {{test|foobar}} c"
    assert posparser.strip_safe_templates("a {{attn|en|foo{{test|test}}bar}} c") == "a  c"
