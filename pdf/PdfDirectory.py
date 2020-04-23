from disk import Path
from joblib import Parallel
from joblib import delayed
from pandas import concat
from pandas import DataFrame
from chronometry.progress import iterate

from .PdfFile import PdfFile


class PdfDirectory(Path):
	def __init__(self, string, html_directory):
		super().__init__(string=string, show_size=False)
		self._html_directory = Path(html_directory)
		self._html_directory.make_dir(ignore_if_exists=True)
		self._pdfs = [
			PdfFile(x, html_directory=self._html_directory)
			for x in self.list(show_size=False) if x.extension.lower() == 'pdf'
		]
		self._errors = []

		self._data = None

	def reset_errors(self):
		self._errors = []

	@property
	def pdfs(self):
		"""
		:rtype: PdfFile
		"""
		return self._pdfs

	def get_data(self, num_jobs=1, **kwargs):
		def _get_data(pdf):
			"""
			:type pdf: PdfFile
			:rtype: DataFrame
			"""
			try:
				return pdf.get_data(**kwargs)
			except Exception as e:
				self._errors.append({'exception': e, 'pdf': pdf})
				return None

		if num_jobs == 1:
			dataframes = [
				_get_data(pdf=pdf)
				for pdf in iterate(self.pdfs, text='getting the data')
			]
		else:
			processor = Parallel(n_jobs=num_jobs, backend='threading', require='sharedmem')
			dataframes = processor(
				delayed(_get_data)(pdf=pdf)
				for pdf in iterate(self.pdfs, text='getting the data in parallel')
			)
		self._data = concat([x for x in dataframes if x is not None])
		if len(self._errors) > 0:
			raise self._errors[0]['exception']

	def get_time_data(self, num_jobs=1):
		"""
		:rtype: DataFrame
		"""
		def _get_time_data(x):
			return dict(pdf=x.name, **x._elapsed)

		if num_jobs == 1:
			records = [
				_get_time_data(pdf)
				for pdf in iterate(self.pdfs, text='getting processing time')
			]
		else:
			processor = Parallel(n_jobs=num_jobs, backend='threading', require='sharedmem')
			records = processor(
				delayed(_get_time_data)(pdf)
				for pdf in iterate(self.pdfs, text='getting processing time in parallel')
			)

		return DataFrame.from_records(records)
