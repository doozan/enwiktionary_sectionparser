from enwiktionary_sectionparser.utils import wiki_splitlines

def test_wiki_splitlines():

    text = """\
{{template}}
==Section==
{{header}}

# blah <ref>
reference
</ref>
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
        '',
        '# blah <ref>\nreference\n</ref>',
        '<!-- comment\ncomment -->',
        '{{template|\ntemplate}} {{t\n|template}}'
    ]

    res = list(wiki_splitlines(text))
    print(res)
    assert res == expected




