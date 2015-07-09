from .utils import convert_lines_to_text
from xml.etree.cElementTree import fromstring
import gzip, time, re
from contextlib import closing
try:
	from IPython.display import clear_output as clear_output_ipython
except ImportError:
	def clear_output_ipython(*args, **kwargs):
		pass
from bz2file import BZ2File
from os import path

Namespaces = [
	"WP", "Aide", "Help", "Talk", "User", "Template", "Wikipedia",
	"File", "Book", "Portal", "Portail", "TimedText", "Module",
	"MediaWiki", "Special", "Spécial", "Media", "Category",
	"Catégorie", "[^:]+"
]

Disambiguation = [
	"disambiguation","homonymie", "значения", "disambigua", "peker",
	"ujednoznacznienie", "olika betydelser", "Begriffsklärung", "desambiguación"
]

namespace_matcher = re.compile(
	"(?P<namespace>(?:"+"|".join(Namespaces) + "|[^|+])):.+",
	re.IGNORECASE)
disambiguation_matcher = re.compile(
	".+ \((?:"+"|".join(Disambiguation) + ")\)",
	re.IGNORECASE)

ends_with_templator = re.compile("([\|}]})$")


def line_is_agreeable(line):
	return not (line.startswith("|") or line.startswith("!") or line.startswith("{{") or line.startswith("{|") or ends_with_templator.search(line) != None)

class XMLNode(object):

	@staticmethod
	def parse_node(text):
		node = fromstring(text)
		return (node.tag, node.text)

	def __init__(self, text):
		self.tag, self.text = self.parse_node(text)

class TitleXMLNode(XMLNode):

	def is_disambiguation_page(self):
		return disambiguation_matcher.match(self.text) != None

	def matches_special_namespaces(self):
		return namespace_matcher.match(self.text) != None

	def is_special_page(self):
		return self.matches_special_namespaces() or self.is_disambiguation_page()

def smart_open(fname, mode='r'):
	_, ext = path.splitext(fname)
	if ext == '.bz2':
		return closing(BZ2File(fname, mode))
	if ext == '.gz':
		return closing(gzip.open(fname, mode))
	return open(fname, mode)

def almost_smart_open(fname, mode='r'):
	_, ext = path.splitext(fname)
	if ext == '.bz2':
		return BZ2File(fname, mode)
	if ext == '.gz':
		return gzip.open(fname, mode)
	return open(fname, mode)

def convert_wiki_to_corpus(path, target_path, target_mode = "wb", *args, **kwargs):
	try:
		with gzip.open(target_path, target_mode) as file:
			origin_file = almost_smart_open(path, "rb")
			for sentence in convert_wiki_to_lines(origin_file, *args, **kwargs):
				file.write(sentence.encode("utf-8"))
			origin_file.close()
	except KeyboardInterrupt:
		return origin_file

class WikiReaderState:
	"""
	Stores the state of the reader
	as it sequentially discovers the
	contents of an xml dump line by line
	"""

	def __init__(self, file, report_every = 100, clear_output = True):

		# parameters & input
		self.file = file
		self.report_every = report_every
		self.clear_output = clear_output

		# state
		self.reset_state()

		# counters:
		self.articles_seen = 0
		self.filtered_articles_seen = 0
		self.lines_seen = 0

		# clock:
		self.start_time = time.time()

	def is_special(self):
		"""
		Check whether the page is special:
		is it a redirection, a namespace, or a
		disambiguation_page.
		"""
		return self.disambiguation_page or self.namespace_page or self.redirection_page

	def mark_redirection(self):
		"""
		Tell state that a redirection was observed
		"""
		self.redirection_page = True

	def enter_page(self):
		"""
		Mark that reader is inside a page
		"""
		self.in_page = True
		self.articles_seen += 1

	def enter_text(self):
		"""
		Mark that reader is inside the text portion of a page
		"""
		self.inside_text = True

	def enter_line(self):
		self.lines_seen += 1

	def mark_seen_filtered_article(self):
		self.filtered_articles_seen += 1
		if self.filtered_articles_seen % self.report_every == 0:
			freq = self.filtered_articles_seen /(time.time() - self.start_time)
			if self.clear_output:
				clear_output_ipython(wait=True)
			print("%d articles seen so far. Processing %.3f articles / s : position %r" % (self.filtered_articles_seen, freq, self.file.tell()))

	def reset_state(self):
		"""
		Resets all boolean observations in the state
		"""
		self.in_page = False
		self.inside_text = False
		self.disambiguation_page = False
		self.redirection_page = False
		self.namespace_page = False
		self.current_title = None

	def exit_page(self):
		"""
		Mark that reader exits a page.
		Also modifies state to reflect new knowledge.
		"""
		self.reset_state()

	def exit_text(self):
		self.inside_text = False

	def observe_title_line(self, line):
		"""
		Observe and mark updates to state given
		a line with <title> in it
		"""
		title_node               = TitleXMLNode(line)
		self.current_title       = title_node.text
		self.disambiguation_page = title_node.is_disambiguation_page()
		self.namespace_page      = title_node.matches_special_namespaces()

	def print_state(self):
		print("title          '%s'" % (self.current_title))
		print("redirect       %r"   % (self.redirection_page))
		print("disambiguation %r"   % (self.disambiguation_page))
		print("special_page   %r"   % (self.namespace_page))

def get_redirection_list(wiki,
	encoding="utf-8",
	element = "page",
	max_articles = 9999999999999999,
	maxlines = 9999999999999999,
	offset = 0):

	state = WikiReaderState(wiki, report_every = 100000000, clear_output = False)

	start_element_node       = "<%s" % (element)
	end_element_node         = "</%s>" % (element)

	redirect_to = None

	for line in wiki:
		line = line.decode(encoding)
		state.enter_line()

		if state.lines_seen > maxlines:
			break

		if line.find("<redirect") != -1:
			state.mark_redirection()
			redirect_to = line.split('"')[1]
			continue

		if line.find(start_element_node) != -1:
			state.enter_page()
			if state.filtered_articles_seen >= max_articles:
				break
			continue

		if state.in_page and line.find("<title>") != -1:
			state.observe_title_line(line)
			continue

		if line.find(end_element_node) != -1:
			if state.redirection_page:
				state.mark_seen_filtered_article()
				yield (state.current_title, redirect_to)
			redirect_to = None
			state.exit_page()
			continue

def convert_wiki_to_lines(wiki,
	skip_cdata = False,
	line_converter = convert_lines_to_text,
	encoding="utf-8",
	inner_element="text",
	element = "page",
	report_every = 100,
	clear_output = True,
	parse_special_pages = False,
	skip_templated_lines = True,
	max_articles = 9999999999999999,
	maxlines = 9999999999999999,
	offset = 0):

	state = WikiReaderState(wiki, report_every = report_every, clear_output = clear_output)

	current_article          = ''
	start_element_node       = "<%s" % (element)
	start_inner_element_node = "<%s" % (inner_element)
	end_inner_element_node   = "</%s>" % (inner_element)
	end_element_node         = "</%s>" % (element)

	for line in wiki:
		line = line.decode(encoding)
		state.enter_line()

		if state.lines_seen > maxlines:
			break

		if skip_cdata:
			if line.find("<![CDATA") != -1:
				continue

		if line.find("<redirect") != -1:
			state.mark_redirection()
			continue

		if line.find(start_element_node) != -1:
			state.enter_page()
			if state.filtered_articles_seen >= max_articles:
				break
			continue

		if state.in_page and line.find("<title>") != -1:
			state.observe_title_line(line)
			continue

		if (parse_special_pages or not state.is_special()) and line.find(start_inner_element_node) != -1:
			state.enter_text()

		if line.find(end_element_node) != -1:
			if state.articles_seen > offset and (parse_special_pages or not state.is_special()):
				state.mark_seen_filtered_article()
				for subline in line_converter(current_article, state.current_title):
					yield subline
			current_article = ''
			state.exit_page()
			continue

		if state.inside_text and (not skip_templated_lines or line_is_agreeable(line)):
			current_article += line.replace("\xa0", " ").replace("&quot;", '"').replace("&gt;", ">").replace("&lt;", "<").replace("&amp;nbsp;", " ").replace("&amp;", "&")
			if line.find(end_inner_element_node) != -1:
				state.exit_text()
			continue

		if state.inside_text and line.find(end_inner_element_node) != -1:
			state.exit_text()
