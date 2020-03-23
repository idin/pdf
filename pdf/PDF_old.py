from pdftotree import parse
from bs4 import BeautifulSoup
import warnings
from silverware import Spoon


from .clean_text import clean_text


class PDF:
	def __init__(self, path, extract_text=True, extract_tables=True, ignore_single_parents=False, keep_names=True, function=None, base_url=None, flatten=True):
		"""
		:type path: str
		"""
		self._path = path
		self._pdf_tree = None
		self._soup = None
		self._dictionary = None

		self._extract_text = extract_text
		self._extract_tables = extract_tables
		self._ignore_single_parents = ignore_single_parents
		self._keep_names = keep_names
		self._function = function or clean_text
		self._base_url = base_url
		self._flatten = flatten

	@property
	def path(self):
		"""
		:rtype: str
		"""
		return self._path

	@property
	def pdf_tree(self):
		"""
		:rtype: str
		"""
		if self._pdf_tree is None:
			with warnings.catch_warnings():
				warnings.simplefilter("ignore")
				self._pdf_tree = parse(
					pdf_file=self.path,
					html_path=None, model_type=None, model_path=None, favor_figures=True, visualize=False
				)
		return self._pdf_tree

	@property
	def soup(self):
		"""
		:rtype: BeautifulSoup
		"""
		if self._soup is None:
			self._soup = BeautifulSoup(markup=self.pdf_tree, features='lxml')
		return self._soup

	@property
	def dictionary(self):
		"""
		:rtype: dict
		"""
		if self._dictionary is None:
			self._dictionary = Spoon.convert_to_list(
				soup=self.soup,
				extract_text=self._extract_text,
				extract_tables=self._extract_tables,
				ignore_single_parents=self._ignore_single_parents,
				keep_names=self._keep_names,
				function=self._function,
				base_url=self._base_url,
				flatten=self._flatten
			)
		return self._dictionary




