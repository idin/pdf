from nltk import word_tokenize


def get_words(string, language='english'):
	return word_tokenize(string, language=language)


def count_words(string, language='english'):
	return len(get_words(string=string, language=language))


def count_english_words(x, vocabulary, case_sensitive=False):
	if isinstance(x, (list, tuple)):
		words = x
	elif isinstance(x, str):
		words = get_words(string=x, language='english')

	if hasattr(vocabulary, 'words'):
		vocabulary = vocabulary.words()
	elif isinstance(vocabulary, (list, tuple, set)):
		pass
	else:
		raise TypeError(f'{vocabulary} is of type {type(vocabulary)}!')

	num_english_words = 0
	for word in words:
		if len(word) < 2:
			if word in ['a', 'A', 'I']:
				num_english_words += 1
			elif not case_sensitive and word == 'i':
				num_english_words += 1
		else:
			if word in vocabulary:
				num_english_words += 1
			elif not case_sensitive:
				if word.capitalize() in vocabulary or word.lower() in vocabulary or word.upper() in vocabulary:
					num_english_words += 1
	return num_english_words


def get_ratio_of_english_words(x, vocabulary=None, case_sensitive=False):
	if isinstance(x, (list, tuple)):
		words = x
	elif isinstance(x, str):
		words = get_words(string=x, language='english')

	if isinstance(x, (list, tuple)):
		words = x
	elif isinstance(x, str):
		words = get_words(string=x, language='english')

	num_english_words = count_english_words(x=words, vocabulary=vocabulary, case_sensitive=case_sensitive)

	return num_english_words / len(words)
