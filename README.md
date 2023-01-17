# enwiktionary_sectionparser
`enwiktionary_sectionparser` is a Python module that allows you to parse and edit pages from en.wiktionary.org

## Installation

To install it, run the following command:

    $ pip3 install git+https://github.com/doozan/enwiktionary_sectionparser

## Parser notes

``enwiktionary_sectionparser`` is an opinionated parser and will apply
[recommended formatting](https://en.wiktionary.org/wiki/Wiktionary:Normalization_of_entries) to the text it parses.
Specifically, it will make the following changes as needed

* One blank line before all headings, including between two headings, except for before the first language heading.
* No blank line after any heading except when another heading immediately follows.
* No whitespace between = and heading title, i.e. ==English== and ===Noun===, not == English == or === Noun ===.
* No blank lines between the first language heading and any preceding content.
* One horizontal rule ---- between language sections.
* The horizontal rule (----) on its own line.
* One blank line before the ---- between language sections.
* One blank line after the ---- between language sections.
* Categories and category templates are placed at the end of each language section.
* Topline templates (LDL, normalized, hot word, rfd) are placed at the top of an entry immediately after the L2 header.

``entry.changelog`` contains a summary of any fixes applied. If you are using this as part of a bot to write changes
back to wiktionary, you should include this string in the edit summary.

## Usage

### Basic usage

```python
import enwiktionary_sectionparser as enwiktparser
entry = enwiktparser.parse(page_text, page_title)
```

If the page can be clealy parsed, ``entry`` will be a ``enwiktionary_sectionparser.SectionParser`` object, which acts like an
ordinary ``str`` object with some extra methods for navigating and manipulating the page sections.

In rare circumstances (unclosed HTML comments, unclosed templates, etc) the page cannot be cleanly parsed and should not
be maniuplated programatically until the errors have been manually identified and corrected. In this case, ``entry`` will
be ``None``.

### Using filter_sections()

``entry`` provides ``filter_sections()`` which takes two optional keyword arguments, ``recursive`` (True by default) and ``matches``.

``Recursive``: when True (default), will search all descendent sections, when False will only search direct children.

``matches`` can be a string or a callable. If it's a string, it will match the section title. Callables can be used for more advanced matching.

filter_sections() returns a list of ``enwiktionary_sectionparser.SectionParser`` objects which can act like strings but also provide methods for
for navigating and manipulating the section and any descendent sections.

#### Finding a specific L2 section
```python
entry = enwiktparser.parse(page_text, page_title)
all_japanese_l2s = entry.filter_sections(matches="Japanese", recursive=False)
if len(all_japanese_l2s) > 1:
    raise ValueError("Multiple Japanese L2 sections")
if not all_japanese_l2s:
    raise ValueError("No Japanese L2 section not found")
japanese = all_japanese_l2s[0]
```
