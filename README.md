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
* Categories and category templates are placed at the end of each language section.
* Topline templates (LDL, normalized, hot word, rfd) are placed at the top of an entry immediately after the L2 header.

``entry.changelog`` contains a summary of any fixes applied. If you are using this as part of a bot to write changes
back to wiktionary, you should include this string in the edit summary.

## Usage

### Basic usage

```python
import enwiktionary_sectionparser as parser
entry = parser.parse(page_text, page_title)
```

If the page can be clealy parsed, ``entry`` will be a ``SectionParser`` object, which acts like an
ordinary ``str`` object with some extra methods for navigating and manipulating the page sections.

In rare circumstances (unclosed HTML comments, unclosed templates, etc) the page cannot be cleanly parsed and should not
be maniuplated programatically until the errors have been manually identified and corrected. In this case, ``entry`` will
be ``None``.

### Using filter_sections()

``entry`` provides ``filter_sections()`` which takes two optional keyword arguments, ``recursive`` (True by default) and ``matches``.

``Recursive``: when True (default), will search all descendent sections, when False will only search direct children.

``matches`` can be a string or a callable. If it's a string, it will match the section title. Callables can be used for more advanced matching.

filter_sections() returns a list of ``SectionParser`` objects which can act like strings but also provide methods for
for navigating and manipulating the section and any descendent sections.

### Recipes

#### Get the "Japanese" L2 section

```python
entry = parser.parse(page_text, page_title)
all_japanese_l2s = entry.filter_sections(matches="Japanese", recursive=False)
if len(all_japanese_l2s) > 1:
    raise ValueError("Multiple Japanese L2 sections")
if not all_japanese_l2s:
    raise ValueError("No Japanese L2 section not found")
japanese = all_japanese_l2s[0]
```

#### Get "English::Noun::Usage notes"
```python
usage_notes = entry.filter_sections(matches=lambda x: x.name == "Usage notes" and x.path == ("English", "Noun"))
```

#### Add a new Spanish L2 entry
```python
entry = parser.parse(page_text, page_title)
if entry.filter_sections(matches="Spanish", recursive=False):
    raise ValueError("Spanish entry already exists")

spanish_data = """===Noun===
{{es-noun|m}}

# [[foo]]
# [[bar]]
"""
spanish = entry.add_child("Spanish", spanish_data)
```

#### Add a "DRAE" link to the "Spanish::Further reading" if it is not already included, create "Further reading" if it doesn't exist

```python
entry = parser.parse(page_text, page_title)

spanish = next(entry.ifilter_sections(matches="Spanish", recursive=False), None)
if not spanish:
    return

further_reading = next(spanish.ifilter_sections(matches="Further reading"), None)
if not further_reading:
    further_reading = spanish.add_child("Further reading")

if "DRAE" not in str(further_reading):
    further_reading.add_line("* {{R:es:DRAE}}")
```
