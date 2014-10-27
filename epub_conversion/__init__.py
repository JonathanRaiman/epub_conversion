"""
Epub and wiki dump conversion module. Provides utilities
for taking large xml files and extracting pages or tokenized
sentences and words.

"""

from .converter import Converter
from .wiki_decoder import convert_wiki_to_lines, convert_wiki_to_corpus

__all__ = ["Converter", "convert_wiki_to_lines", "convert_wiki_to_corpus"]