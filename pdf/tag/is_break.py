from .get_raw_text import get_raw_text


def is_break(tag):
	if tag.name == 'br':
		return True
	else:
		text = get_raw_text(tag)
		if text:
			if '\n' in text and text.strip() == '':
				return True
			else:
				return False
		else:
			return False