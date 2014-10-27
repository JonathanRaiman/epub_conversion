import os
from xml_cleaner import to_raw_text
from epub import open_epub, BadEpubFile
from zipfile import BadZipFile

def get_files_from_path(filetype, path):
	"""
	Recursively returns files matching a filetype from
	a path (e.g. return a list of paths from a folder
	of epub files).
	"""
	
	paths = []
	for subdir in os.listdir(path):
		joined_path = os.path.join(path, subdir)
		if subdir.endswith(filetype):
			paths.append((joined_path, subdir))
		elif os.path.isdir(joined_path):
			paths.extend(get_files_from_path(filetype, joined_path))
	return paths

def try_utf8(data):
	"Returns a Unicode object on success, or None on failure"
	try:
	   return data.decode('utf-8')
	except UnicodeDecodeError:
	   return None

def try_decode(ebook, item):
	try:
		return try_utf8(ebook.read_item(item))
	except KeyError:
		return None

def open_book(path):
	try:
		return open_epub(path)
	except (BadEpubFile, BadZipFile, KeyError, IndexError):
		return None

def convert_xml_element_to_lines(data, boundary):
	start_boundary = "<%s" % (boundary)
	end_boundary = "</%s>" % (boundary)
	data = data.replace("\xa0", " ")
	multi_line = data.split("\n")
	lines = []
	in_book = False
	for line in multi_line:
		if line.find(start_boundary) != -1:
			in_book = True
			line_end = line.find(">")
			sliced_line = line[line_end+1:]
			if len(sliced_line) > 0: lines.append(sliced_line)
			continue
		if line.endswith(end_boundary):
			in_book = False
			line_end = line.find("<")
			sliced_line = line[:line_end]
			if len(sliced_line) > 0: lines.append(sliced_line)
			continue
		if in_book:
			lines.append(line)
	return lines


def convert_epub_to_lines(ebook):
	lines = []
	for item in ebook.opf.manifest.values():
		# read the content
		data = try_decode(ebook, item)
		if data != None:
			lines.extend(convert_xml_element_to_lines(data, "body"))
	return lines

def convert_lines_to_text(lines, article_title):
	for sentence in to_raw_text(lines):
		yield " ".join(sentence)+"\n"