def get_raw_text(tag):
	"""
		:type tag: Tag
		:rtype: NoneType or str
		"""
	if hasattr(tag, 'text'):
		text = tag.text
		if text is None:
			return None
	else:
		text = str(tag)

	return text
