import re


def has_border(tag):
	try:
		style = tag.attrs.get('style')
		re.search(r'(?is)(border:)', str(style)).group(1)
	except AttributeError:
		return None


def get_invisible_border_size(tag):
	try:
		style = tag.attrs.get('style')
		border_size = re.search(r'(?is)(border:\s*textbox)(.*?)(px)', str(style)).group(2)
		return float(border_size)
	except AttributeError:
		return None


def get_border_size(tag):
	try:
		style = tag.attrs.get('style')
		border_size = re.search(r'(?is)(border:)(\s*\w+\s*)(.*?)(px)', str(style)).group(3)
		return float(border_size)
	except AttributeError:
		return None
	except ValueError as e:
		print(style)
		raise e


def get_visible_border_size(tag):
	if has_border(tag):
		if get_invisible_border_size(tag):
			return None
		else:
			return get_border_size(tag)
	else:
		return None