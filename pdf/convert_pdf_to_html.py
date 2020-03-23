import os
from disk import Path


def convert_pdf_to_html(pdf_path, html_path):
	if isinstance(pdf_path, Path):
		pdf_path = pdf_path.path
	if isinstance(html_path, Path):
		html_path = html_path.path
	os.system(f'pdf2txt.py -o "{html_path}" "{pdf_path}"')
