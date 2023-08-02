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


def test_with_state():
    text = "blah\n{{template\ntest"
    expected = ['blah', '{{template\ntest', 1]

    res = list(wiki_splitlines(text, return_state=True))
    print(res)
    assert res == expected

    text = "blah\n<ref>\ntest"
    expected = ['blah', '<ref>\ntest', 0x100]

    res = list(wiki_splitlines(text, return_state=True))
    print(res)
    assert res == expected

    text = "blah\n<NoWiki>\ntest"
    expected = ['blah', '<NoWiki>\ntest', 0x200]

    res = list(wiki_splitlines(text, return_state=True))
    print(res)
    assert res == expected


    text = "blah\n<!--\ntest"
    expected = ['blah', '<!--\ntest', 0x400]

    res = list(wiki_splitlines(text, return_state=True))
    print(res)
    assert res == expected



