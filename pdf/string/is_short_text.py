def is_short_text(string):
	string = string.strip()
	if len(string) < 4:
		return True
	return len(string.split()) < 10 and string[-1] not in ['.', '!']
