from disk import Path
from silverware import HtmlFile, Spoon
from silverware.htmltext import HtmlText
from chronometry import get_elapsed
from chronometry import get_now

import re

from .convert_pdf_to_html import convert_pdf_to_html
from .exceptions import ConversionError


class Pdf(Path):
	def __init__(self, string, show_size=False, html_directory=None, num_jobs=1):
		super().__init__(string=string, show_size=show_size)
		self._html_file = None
		self._spoon = None
		self._paragraphs = None

		if html_directory is not None:
			html_directory = Path(html_directory)
		self._html_directory = html_directory

		self._elapsed = {}
		self._html_text = None
		self._num_jobs = num_jobs

	def move_and_rename(self, new_name=None, new_directory=None, new_path=None):
		old_html_directory = Path(self.html_directory)
		old_html_path = Path(self.html_path)
		old_text_path = Path(self.text_path)
		super().move_and_rename(new_name=new_name, new_directory=new_directory, new_path=new_path)
		if old_text_path.exists() and not self.text_path.exists():
			old_text_path.move_and_rename(new_path=self.text_path)
		if old_html_path.exists() and not self.html_path.exists():
			old_html_path.move_and_rename(new_path=self.html_path)
		if self._html_file is not None and self.html_path.exists():
			self._html_file = HtmlFile(self.html_path)

		if old_html_directory.exists() and old_html_directory.is_empty():
			old_html_directory.delete()
		return self

	@property
	def html_directory(self):
		return self.parent_directory + (self.name + '_helpers')

	@property
	def html_path(self):
		return self.html_directory + (self.name + '.html')

	def convert_to_html(self, ignore_if_exists=True, num_tries=3):
		"""
		:rtype: HtmlFile
		"""
		path = self.html_path

		start_time = get_now()
		for try_num in range(num_tries + 1):
			if path.exists() and ignore_if_exists and path.get_size_kb() > 6:
				break
			else:
				if not path.parent_directory.exists():
					path.parent_directory.make_dir()
				convert_pdf_to_html(pdf_path=self, html_path=path)
				if path.exists() and path.get_size_kb() > 6:
					self._elapsed['html_conversion'] = get_elapsed(start=start_time, unit='s')
					break
		else:
			raise ConversionError(f'could not convert {self.name_and_extension} to html after {num_tries} tries')

		html_file = HtmlFile(path)
		return html_file

	@property
	def html_file(self):
		"""
		:rtype: HtmlFile
		"""
		if self._html_file is None:
			self._html_file = self.convert_to_html()
		return self._html_file

	@property
	def text_path(self):
		"""
		:rtype: Path
		"""
		return self.html_directory + (self.name + '_html_text.pickle')

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

	@property
	def text(self):
		"""
		:rtype: HtmlText
		"""
		if self._html_text is None:
			self._html_text = self.generate_text(ignore_if_exists=True, extract_tags=False)
		return self._html_text

	def generate_text(self, extract_tags=False, ignore_if_exists=True):
		"""
		:rtype: HtmlText
		"""
		if self.text_path.exists() and ignore_if_exists:
			text = self.text_path.load()

		else:
			text = HtmlText(
				obj=self,
				ignore_function=lambda x: not re.match(r'^page \d+$', 'Page 02', flags=re.IGNORECASE),
				log=False,
				num_jobs=self._num_jobs,
				extract_tags=extract_tags
			)
			self.text_path.save(text)

		return text

	def delete_extra_files(self):
		if self.html_directory.exists():
			self.html_directory.delete()
