from disk import Path
import os
from silverware import HtmlFile, Spoon

from .convert_pdf_to_html import convert_pdf_to_html


class PdfFile(Path):
	def __init__(self, string, show_size=False):
		super().__init__(string=string, show_size=show_size)
		self._html_file = None
		self._spoon = None
		self._paragraphs = None

	@property
	def html_file(self):
		"""
		:rtype: HtmlFile
		"""
		if self._html_file is None:
			self._html_file = self.convert_to_html()
		return self._html_file

	def get_html_path(self, path=None):
		"""
		:type path: NoneType or str or Path or HtmlPath
		:rtype: HtmlFile
		"""
		if path is None:
			path = HtmlFile(string=(self.parent_directory + (self.name + '.html')).path)
		elif isinstance(path, HtmlFile):
			pass
		elif isinstance(path, Path):
			path = HtmlFile(path)
		elif isinstance(path, str):
			if '.' in path:
				path = HtmlFile(path)
			else:
				path = HtmlFile(path + '.html')
		else:
			raise TypeError(f'html_path is of type {type(path)}!')
		return path

	def convert_to_html(self, path=None, ignore_if_exists=True):
		"""
		:rtype: HtmlFile
		"""
		path = self.get_html_path(path=path)
		if path.exists() and ignore_if_exists:
			pass
		else:
			convert_pdf_to_html(pdf_path=self, html_path=path)
		self._html_file = path
		return path

	@property
	def spoon(self):
		"""
		:rtype: Spoon
		"""
		if self._spoon is None:
			self._spoon = self.html_file.spoon.clean_text()
		return self._spoon

	@property
	def paragraphs(self):
		"""
		:rtype: list[str]
		"""
		if self._paragraphs is None:
			self._paragraphs = self.spoon.get_text(sep=' ', flatten=True)
		return self._paragraphs
