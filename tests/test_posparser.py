import pytest
import enwiktionary_sectionparser as parser
from enwiktionary_sectionparser.posparser import is_sentence, is_bare_ux, is_template, strip_ref_tags

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

    assert pos.headlines == ['{{en-noun}}', '']
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



def test_basic():
    text = """\
===Adjective===
{{en-adj}}

# sense 1

# sense 2
"""

    wikt = parser.parse(text, "test")
    section = wikt.filter_sections(matches="Adjective")[0]
    pos = parser.parse_pos(section)

    assert len(pos.senses) == 2



