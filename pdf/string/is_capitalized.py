CAP_EXEMPT = [
	'', 'and', 'as', 'as if', 'as long as', 'at', 'but', 'by', 'even if', 'for', 'from', 'if', 'if only', 'in',
	'into', 'like', 'near', 'now that', 'nor', 'of', 'off', 'on', 'on top of', 'once', 'onto', 'or', 'out of',
	'over', 'past', 'so', 'so that', 'than', 'that', 'till', 'to', 'up', 'upon', 'with', 'when', 'yet'
]


def is_capitalized(string):
	words = string.split()
	for word in words:
		if word not in CAP_EXEMPT and word[0].islower():
			return False
	return True
