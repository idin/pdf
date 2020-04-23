from disk import Path
from silverware import HtmlFile, Spoon
from pandas import DataFrame
from chronometry import get_elapsed
from chronometry import get_now

from .convert_pdf_to_html import convert_pdf_to_html
from .HtmlText import HtmlText
from .Text import Title
from .Text import Text


class PdfFile(Path):
	def __init__(self, string, vocabulary=None, show_size=False, html_directory=None):
		super().__init__(string=string, show_size=show_size)
		self._html_file = None
		self._spoon = None
		self._paragraphs = None
		self._vocabulary = vocabulary

		if html_directory is not None:
			html_directory = Path(html_directory)
		self._html_directory = html_directory

		self._elapsed = {}

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
			if self._html_directory is None:
				html_directory = self.parent_directory + 'html'
			else:
				html_directory = self._html_directory
			html_directory.make_dir(ignore_if_exists=True)
			path = HtmlFile(string=(html_directory + (self.name + '.html')).path)
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

	def convert_to_html(self, path=None, ignore_if_exists=True, num_tries=3):
		"""
		:rtype: HtmlFile
		"""
		path = self.get_html_path(path=path)

		start_time = get_now()
		for try_num in range(num_tries + 1):
			if path.exists() and ignore_if_exists and path.get_size_kb() > 6:
				break
			else:
				convert_pdf_to_html(pdf_path=self, html_path=path)
				if path.exists() and path.get_size_kb() > 6:
					self._elapsed['html_conversion'] = get_elapsed(start=start_time, unit='s')
					break
		else:
			raise RuntimeError(f'could not convert {self.name_and_extension} to html after {num_tries} tries')

		self._html_file = path
		return path

	@property
	def spoon(self):
		"""
		:rtype: Spoon
		"""
		if self._spoon is None:
			start_time = get_now()
			self._spoon = self.html_file.spoon
			self._elapsed['html_parsing'] = get_elapsed(start=start_time, unit='s')
		return self._spoon

	def get_text(
			self, simplify=True, ignore_depth=True, flatten=True, remove_short_strings=False, remove_tables=True,
			min_english_ratio=0
	):
		"""
		:rtype: HtmlText
		"""
		soup = self.spoon.soup

		start_time = get_now()
		html_text = HtmlText(tag=soup, vocabulary=self._vocabulary)
		self._elapsed['text_generation'] = get_elapsed(start=start_time, unit='s')
		start_time = get_now()
		if simplify:
			html_text = html_text.simplify(
				ignore_depth=ignore_depth,
				remove_short_strings=False,
				remove_tables=remove_tables,
				min_english_ratio=min_english_ratio
			)
		if flatten:
			html_text = html_text.flatten()
		if simplify:
			html_text = html_text.simplify(
				ignore_depth=ignore_depth,
				remove_short_strings=remove_short_strings,
				remove_tables=remove_tables,
				min_english_ratio=min_english_ratio
			)
		self._elapsed['simplification'] = get_elapsed(start=start_time, unit='s')
		return html_text

	def get_text_records(
			self, simplify=True, ignore_depth=True, remove_short_strings=False,
			paragraph_max=50, min_english_ratio=0
	):
		"""
		:rtype: list[dict[str, ]]
		"""

		try:
			text = self.get_text(
				simplify=simplify, ignore_depth=ignore_depth,
				flatten=True, remove_short_strings=remove_short_strings,
				min_english_ratio=min_english_ratio
			)
		except Exception as e:
			print(f'exception raised when tried to get_text for {self.name_and_extension}')
			raise e

		paragraph_start = get_now()
		try:
			paragraphs = text.get_paragraphs(paragraph_max=paragraph_max, text_as_string=False)
		except Exception as e:
			print(f'exception raised when tried to get_paragraphs from text of {self.name_and_extension}')
			raise e

		records = []
		section_title = None
		title_font_size = None
		section_num = 0
		paragraph_num = 0
		for paragraph in paragraphs:
			if isinstance(paragraph, Title):
				section_num += 1
				section_title = paragraph.string
				title_font_size = paragraph.font_size
			elif isinstance(paragraph, Text):
				paragraph_num += 1
				for i, paragraph_text in enumerate(paragraph.paragraphs):
					record = {
						'pdf': self.name,
						'section': section_num,
						'paragraph': paragraph_num,
						'part': i + 1,
						'title': section_title,
						'title_font_size': title_font_size,
						'paragraph_font_size': paragraph.font_size,
						'text': paragraph_text,
					}
					records.append(record)

		self._elapsed['paragraph_generation'] = get_elapsed(start=paragraph_start, unit='s')
		return records

	def get_data(
			self, simplify=True, ignore_depth=True, remove_short_strings=False,
			paragraph_max=50, min_english_ratio=0, measure_time=False
	):
		"""
		:type simplify: bool
		:type ignore_depth: bool
		:type remove_short_strings: bool
		:type paragraph_max: int
		:rtype: DataFrame
		"""
		start_time = get_now()
		records = self.get_text_records(
			simplify=simplify,
			ignore_depth=ignore_depth,
			remove_short_strings=remove_short_strings,
			paragraph_max=paragraph_max,
			min_english_ratio=min_english_ratio
		)

		data = DataFrame.from_records(records)
		self._elapsed['total'] = get_elapsed(start=start_time, unit='s')

		if measure_time:
			for key, value in self._elapsed.items():
				data[f'{key}_time'] = value
		return data
