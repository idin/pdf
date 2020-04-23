from nltk import tokenize
from .string import strip_non_alphanumeric_from_beginning
from .string import ends_with_punctuation


class String:
	def __init__(self, string, font_size):
		self._string = strip_non_alphanumeric_from_beginning(string)
		self._string = ' '.join(self._string.split())
		self._font_size = font_size

	@property
	def font_size(self):
		return self._font_size

	@property
	def string(self):
		"""
		:rtype: str
		"""
		return self._string

	def __str__(self):
		return self._string

	def __repr__(self):
		return str(self)


class Title(String):
	def __str__(self):
		return f'* {self._string} *'


class Paragraph:
	def __init__(self, language='english'):
		self._language = language
		self._sentences = []
		self._num_words = 0

	@property
	def num_words(self):
		"""
		:rtype: int
		"""
		return self._num_words

	def append(self, sentence, num_words=None):
		num_words = num_words or len(tokenize.word_tokenize(sentence, language=self._language))
		self._sentences.append(sentence)
		self._num_words += num_words

	@property
	def string(self):
		"""
		:rtype: str
		"""
		return ' '.join(self._sentences)

	def __str__(self):
		return self.string

	def __repr__(self):
		return str(self)


class Text(String):
	def __init__(self, string, font_size, paragraph_max=50, language='english'):
		super().__init__(string=string, font_size=font_size)
		self._paragraph_max = paragraph_max
		self._language = language
		self._paragraphs = None

	@property
	def sentences(self):
		"""
		:rtype: list[str]
		"""
		return [
			strip_non_alphanumeric_from_beginning(sentence)
			for sentence in tokenize.sent_tokenize(self._string, language=self._language)
		]

	@property
	def paragraphs(self):
		"""
		:rtype: list[str]
		"""
		sentences = self.sentences
		num_sentences = len(sentences)

		if self._paragraphs is None:
			paragraphs = []
			for sentence in sentences:
				num_words = len(tokenize.word_tokenize(sentence, language=self._language))
				if not ends_with_punctuation(sentence) and num_sentences < 2 and (num_words < 8 or len(sentence) < 12):
					break
				if len(paragraphs) == 0:
					new_paragraph = Paragraph()
					new_paragraph.append(sentence=sentence, num_words=num_words)
					paragraphs.append(new_paragraph)
				else:
					last_paragraph = paragraphs[-1]
					if num_words + last_paragraph.num_words > self._paragraph_max - 2:
						new_paragraph = Paragraph()
						new_paragraph.append(sentence=sentence, num_words=num_words)
						paragraphs.append(new_paragraph)
					else:
						last_paragraph.append(sentence=sentence, num_words=num_words)
			self._paragraphs = [paragraph.string for paragraph in paragraphs]
		return self._paragraphs
