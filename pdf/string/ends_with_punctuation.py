def ends_with_punctuation(string):
	if string is None:
		return False
	for punctuation in ['.', '!', '?']:
		if string.rstrip().endswith(punctuation):
			return True
	return False
