from . import sectionparser

def parse(text, title):
    return sectionparser.SectionParser(text, title)
