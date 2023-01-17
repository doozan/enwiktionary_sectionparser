"""
enwiktionary_sectionparser

A simple parser for English Wiktionary pages
"""

__version__ = "0.1.0"
__author__ = 'Jeff Doozan'

from . import sectionparser

SectionParser = sectionparser.SectionParser
Section = sectionparser.Section

def parse(text, title, log=None):
    entry = sectionparser.SectionParser(text, title, log)

    # Pages with an unclosed template or html comment are not safe to edit automatically
    # return None *unless* logging has been enabled in which case it is assumed
    # that the caller knows enough to handle any errors
    if not log and entry.state:
        return

    return entry
