# All Parts of Speech defined by WT:ELE
WT_POS = {
    "Adjective": "adj",
    "Adverb": "adv",
    "Ambiposition": "ambip",
    "Article": "art",
    "Circumposition": "circump",
    "Classifier": "classifier",
    "Clitic": "clitic",
    "Conjunction": "conj",
    "Contraction": "contraction",
    "Counter": "counter",
    "Determiner": "determiner",
    "Ideophone": "ideophone",
    "Interjection": "interj",
    "Noun": "n",
    "Numeral": "num",
    "Participle": "v",
    "Particle": "particle",
    "Postposition": "postp",
    "Preposition": "prep",
    "Pronoun": "pron",
    "Proper noun": "prop",
    "Verb": "v",

    # Morphemes
    "Circumfix": "circumfix",
    "Combining form": "affix",
    "Infix": "infix",
    "Interfix": "interfix",
    "Prefix": "prefix",
    "Root": "root",
    "Suffix": "suffix",

    # Symbols and characters
    "Diacritical mark": "diacrit",
    "Letter": "letter",
    "Ligature": "ligature",
    "Number": "num",
    "Punctuation mark": "punct",
    "Syllable": "syllable",
    "Symbol": "symbol",

    # Phrases
    "Phrase": "phrase",
    "Proverb": "proverb",
    "Prepositional phrase": "prep",

    "Romanization": "rom",
    "Logogram": "logo",
    "Determinative": "dtv",
}

# Not in WT:POS, but allowed
EXTRA_POS = {
    "Adjectival noun": "adj",
    "Adnominal": "adnominal",
    "Affix": "affix",
    "Enclitic": "enclitic",
    "Medial": "medial",
    "Idiom": "idiom",
    "Ordinal number": "onum",
    "Preverb": "preverb",
    "Prenoun": "prenoun",
    "Transliteration": "translit",
    "Verbal noun": "verbalnoun",

    "Final": "final",
    "Stem": "stem",
    "Initial": "initial",
}

ALL_POS = WT_POS | EXTRA_POS
