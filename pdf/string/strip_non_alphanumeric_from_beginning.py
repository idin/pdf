def strip_non_alphanumeric_from_beginning(s):
	while len(s) > 0 and not s[0].isalnum():
		s = s[1:]

	return s
