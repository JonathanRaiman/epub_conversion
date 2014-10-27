from .utils import get_files_from_path, convert_epub_to_lines, convert_lines_to_text, open_book
import gzip

class Converter(object):
	"""
	Convert a folder of epubs to raw text for corpus
	learning.
	
	"""

	def __init__(self, path):
		self.path = path

	def convert(self, target_path):
		epub_paths = get_files_from_path(".epub", self.path)

		with gzip.open(target_path, "wb") as file:
			for (epub_path, epub_name) in epub_paths:
				book = open_book(epub_path)
				if book is not None:
					for sentence in convert_lines_to_text(convert_epub_to_lines(book)):
						file.write(sentence.encode("utf-8"))
					print("Wrote \"%s\" to disk" % (epub_name))
				else:
					print("Couldn't open \"%s\"." % (epub_name))