def get_numeric_ratio(s):
	"""
	gets the ratio of numeric characters to the total alphanumerics
	:type s: str
	:rtype: float or NoneType
	"""
	num_numeric = 0
	num_alphabetic = 0
	if len(s) == 0:
		return None
	else:
		for character in s:
			if character.isnumeric():
				num_numeric += 1
			elif character.isalpha():
				num_alphabetic += 1
		return num_numeric / (num_numeric + num_alphabetic)
