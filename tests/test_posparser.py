import pytest
import enwiktionary_sectionparser as parser

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
