def get_alphabetic_ratio(string):
	"""
	gives the ratio of alphabetic characters to the rest
	:type string: str
	:rtype: float or NoneType
	"""
	length = len(string)
	if length == 0:
		return None
	else:
		return sum([1 for character in string if character.isalpha()]) / length
