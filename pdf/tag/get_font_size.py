import re


def get_font_size(tag):
	try:
		style = tag.attrs.get('style')
		font_size = re.search(r'(?is)(font-size:)(.*?)(px)', str(style)).group(2)
		return float(font_size)
	except AttributeError:
		return None



