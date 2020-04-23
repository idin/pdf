import re


def get_alphabetic(string):
	return re.sub("[^a-zA-Z]+", "", string)
