from enwiktionary_sectionparser.utils import wiki_splitlines, wiki_finditer, wiki_replace

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
    expected = ['blah', '{{template\ntest']
    expected_state = 1

    res = list(wiki_splitlines(text, return_state=True))
    state = res.pop()
    print(res)
    assert res == expected

    text = "blah\n<ref>\ntest"
    expected = ['blah', '<ref>\ntest']
    expected_state = 0x100

    res = list(wiki_splitlines(text, return_state=True))
    state = res.pop()
    print(res)
    assert res == expected

    text = "blah\n<NoWiki>\ntest"
    expected = ['blah', '<NoWiki>\ntest']
    expected_state = 0x200

    res = list(wiki_splitlines(text, return_state=True))
    state = res.pop()
    print(res)
    assert res == expected


    text = "blah\n<!--\ntest"
    expected = ['blah', '<!--\ntest']
    expected_state = 0x400

    res = list(wiki_splitlines(text, return_state=True))
    state = res.pop()
    print(res)
    assert res == expected


def test_wiki_finditer():

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x+)", "foo x bar xxx baz")] == ["foo", "x", "bar", "xxx", "baz"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz)", "foo <!-- bar --> baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz)", "foo <!-- bar --> baz", match_comments=True)] == ["foo", "bar", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz)", "foo <!-- bar --> baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <math test='test'> bar </math> baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <math x='x'> bar </math> baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <math test='test'> bar </math> baz", match_math=True)] == ["foo", "bar", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <math test='test'> bar </math> baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <ref test='test'> bar </ref > baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <ref x='x'> bar < / ref > baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <ref test='test'> bar < /ref> baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <ref test='bar'/> baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <ref test='bar'/> baz", match_ref=True)] == ["foo", "bar", "baz"]
    #assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <ref test='bar'/> baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo < nowiki > bar </nowiki > baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <nowiki > bar < / nowiki> baz", match_nowiki=True)] == ["foo", "bar", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <nowiki > bar < / nowiki> baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo < NoWiki > bar </NOwiki > baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <NoWiki > bar < / NOwiki> baz", match_nowiki=True)] == ["foo", "bar", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <NoWiki > bar < / NOwiki> baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <pre> bar </pre> baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <pre> bar </pre> baz", match_pre=True)] == ["foo", "bar", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo <pre> bar </pre> baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo {|bar|} baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo {|bar|} baz", match_table=True)] == ["foo", "bar", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo {|bar|} baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo {{bar|test}} baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo {{bar|test}} baz", match_templates=True)] == ["foo", "bar", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo {{bar|test}} baz", invert_matches=True)] == ["bar"]

    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo [[File:test/bar.jpg|test]] baz")] == ["foo", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo [[File:test/bar.jpg|test]] baz", match_special=True)] == ["foo", "bar", "baz"]
    assert [m.group(0) for m in wiki_finditer("(foo|bar|baz|x)", "foo [[File:test/bar.jpg|test]] baz", invert_matches=True)] == ["bar"]

def test_wiki_replace():

    assert wiki_replace("foo", "FOO", "foo {{foo|foo}} bar foo <ref foo='foo'/> baz foo") == "FOO {{foo|foo}} bar FOO <ref foo='foo'/> baz FOO"
    assert wiki_replace("(foo|bar)", r"#\1#", "foo {{foo|foo}} bar foo <ref foo='foo'/> baz foo", regex=True) == "#foo# {{foo|foo}} #bar# #foo# <ref foo='foo'/> baz #foo#"
