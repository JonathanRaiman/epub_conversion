epub conversion
---------------

Create text corpuses using epubs and wiki dumps.
This is a python package with a Converter for epub and xml (wiki dumps) to text, lines, or Python generators.

Usage:
------

### Epub usage

#### Book by book

To convert epubs to text files, usage is straightforward. First create a converter object:

	converter = Converter("my_ebooks_folder/")

Then using this converter let's concatenate all the text within the ebooks into a single mega text file:

	converter.convert("my_succinct_text_file.gz")

#### Line by line

You can also proceed line by line:

	from epub_conversion.utils import open_book

	book = open_book("twilight.epub")

	lines = convert_epub_to_lines(book)

### Wikidump usage

#### Redirections

Suppose you are interested in all redirections in a given Wikipedia dump file
that is still compressed, then you can access the dump as follows:


	wiki = epub_conversion.wiki_decoder.almost_smart_open("enwiki.bz2")


Taking this dump as our **input** let us now use a generator to output all pairs of `title` and `redirection title` in this dump:

	redirections = {redirect_from:redirect_to
		for redirect_from, redirect_to in epub_conversion.wiki_decoder.get_redirection_list(wiki)
	}

#### Page text

Suppose you are interested in the lines within each page's text section only, then:


	for line in epub_conversion.wiki_decoder.convert_wiki_to_lines(wiki):
		process_line( line )


See Also:
---------

* [Wikipedia NER](https://github.com/JonathanRaiman/wikipedia_ner) a Python module that uses `epub_conversion` to process Wikipedia dumps and output only the lines that contain page to page links, with the link anchor texts extracted, and all markup removed.