from .get_raw_text import get_raw_text
from ..string import get_alphabetic
import re


def get_text(tag, remove_non_alphabetic=True):
	"""
	:type tag: Tag
	:rtype: NoneType or str
	"""
	text = get_raw_text(tag)
	text = text.strip()

	if re.search('^Page \d+$', text):
		return None

	if remove_non_alphabetic:
		alphabetic = get_alphabetic(text)
		if len(alphabetic) < 2:
			return None
		else:
			return text
	else:
		return text
