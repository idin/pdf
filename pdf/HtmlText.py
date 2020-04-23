from bs4 import Tag
from .Text import Text, Title
from .tag import get_text
from .tag import get_children
from .tag import get_font_size
from .tag import get_visible_border_size
from .tag import is_tag_title
from .tag import previous_tag_might_be_title
from .string import is_short_text
from .string import is_capitalized
from .string import ends_with_punctuation
from .string import get_alphabetic_ratio
from .string import get_ratio_of_english_words
from .string import get_words


class HtmlText:
	def __init__(
			self, tag, depth=0, strong_sep='\n', sep=' ', parent=None, is_title=False,
			font_size=None, border_size=None,
			vocabulary=None, language='english',
			index=None, log=False
	):
		"""
		:type tag: Tag
		:type depth: int
		"""
		if tag is None:
			raise

		self._do_log = log
		self._id = None

		if self._do_log:
			if parent:
				if index is None:
					raise ValueError('need an index!')
				elif parent.id is not None:
					self._id = f'{parent.id}.{index}'
				else:
					self._id = f'{index}'


				self._logs = parent._logs
				self.log('added')
				parent._children_dictionary[index] = self
			else:
				self._logs = {'first one': ['created']}

			self._children_dictionary = {}

		self._depth = max(0, depth)
		self._strong_sep = strong_sep
		self._sep = sep
		self._vocabulary = vocabulary
		self._language = language

		tag_children = get_children(tag)
		self._clean = False
		self._parent = parent
		self._tag = tag

		self._font_size = font_size or get_font_size(tag)
		self._border_size = border_size or get_visible_border_size(tag)
		self._is_table = border_size is None and self._border_size is not None
		self._is_short = False
		self._previous_might_be_title = False

		if tag_children is None:
			self._children = None
			self._string = get_text(tag, remove_non_alphabetic=is_title)
			self._is_title = is_title

			if not self._string:
				self._string = None
			else:
				self._is_short = is_short_text(self._string)

		else:
			self._string = None
			if is_tag_title(tag=tag, children=tag_children):
				self._is_title = True
			else:
				self._is_title = is_title

			self._previous_might_be_title = previous_tag_might_be_title(tag=tag, children=tag_children)

			self._children = []
			index = 0
			for child_tag in tag_children:
				self._children.append(
					HtmlText(
						tag=child_tag, depth=self._depth + 1, strong_sep=self._strong_sep, sep=self._sep,
						parent=self, is_title=self._is_title,
						font_size=self._font_size, border_size=self._border_size,
						index=index, log=log
					)
				)
				index += 1

			if not self._children:
				self._children = None
		self.clean_up(remove_tables=False)

		# if most children are short text it's a table
		if self.children:
			num_string_children = 0
			num_short_strings = 0
			for child in self.children:
				if child._string:
					num_string_children += 1
					if child._is_short:
						num_short_strings += 1

			if num_string_children > 3:
				if num_short_strings + 1 == num_string_children:
					self._is_table = True
					self.log(f'is table because num_short_strings={num_short_strings} and num_string_children={num_string_children}')
				elif num_string_children > 0 and num_short_strings / num_string_children >= 0.9:
					self._is_table = True
					self.log(f'is table because num_short_strings={num_short_strings} and num_string_children={num_string_children}')

	@property
	def id(self):
		return self._id

	def is_empty(self):
		if not self._children:
			self._children = None
		if not self._string and not self._children:
			return True
		else:
			return False

	@property
	def parent(self):
		"""
		:rtype: NoneType or HtmlText
		"""
		return self._parent

	# CLEAN UP

	def log(self, message):
		"""
		:type message: str
		"""
		if self._do_log:
			if self.id in self._logs:
				self._logs[self.id].append(message)
			else:
				self._logs[self.id] = [message]

	@property
	def logs(self):
		"""
		:rtype: dict[str, list[str]]
		"""
		return self._logs

	def log_for_all_children(self, message):
		if self._do_log:
			self.log(message=message)
			if self.children:
				for child in self.children:
					child.log_for_all_children(message=message)

	def clean_up(self, remove_tables=True):
		# removes empty children and grand children
		if self._children:
			children = self.children.copy()
			self._children = []
			for child in children:
				if remove_tables and child._is_table:
					child.log_for_all_children(message=f'table removed by {self.id}')
					continue
				if not child._clean:
					child.clean_up(remove_tables=remove_tables)
				if not child.is_empty():
					self._children.append(child)
				else:
					child.log(f'empty removed by {self.id}')

		if not self._children:
			self._children = None
			if not self._string and self.parent:
				self.parent._clean = False

		# some titles can be determined by looking at the second tag among children (which makes the first tag, a title)
		if self._children and len(self._children) > 1:
			first = self._children[0]
			second = self._children[1]
			if second._previous_might_be_title and first._string and is_capitalized(first._string):
				first._is_title = True
				first._string = get_text(first._tag, remove_non_alphabetic=True)
				second._previous_might_be_title = False

		self._clean = True

	def flatten(self, ignore_tables=True):
		self.log('flatten')
		if self._is_table and ignore_tables:
			return self
		else:
			if self.children:
				new_children = []
				for child in self.children:
					child.flatten(ignore_tables=ignore_tables)
					if child.children:
						for grand_child in child.children:
							if not grand_child._is_short:
								new_children.append(grand_child)
								grand_child._parent = self
							else:
								grand_child.log(f'short grand child "{grand_child._string}" removed by {self.id}')

						child._children = None
					else:
						if not child._is_short:
							new_children.append(child)
						else:
							child.log(f'short child "{child._string}" removed by {self.id}')
				self._children = new_children
			return self

	def simplify(
			self, ignore_depth=False,
			remove_short_strings=False,
			min_alphabetic_ratio=0.5,
			min_english_ratio=0.5,
			remove_tables=True
	):
		# merges children that are similar
		self.log('simplify')
		self.clean_up(remove_tables=remove_tables)
		if self.children is not None:
			if len(self.children) == 1:
				self.become_first_child(ignore_depth=ignore_depth)

		if self.children is not None:
			new_children = []
			for child in self.children:
				child.simplify(
					ignore_depth=ignore_depth,
					remove_short_strings=remove_short_strings,
					min_alphabetic_ratio=min_alphabetic_ratio,
					min_english_ratio=min_english_ratio
				)

			for child in self.children:
				if child.is_empty():
					child.log(f'empty removed in simplify by {self.id}')
					continue
				else:
					if len(new_children) == 0:
						new_children.append(child)
					else:
						last_child = new_children[-1]
						if last_child._is_title or child._is_title:
							new_children.append(child)
						elif last_child._string and ends_with_punctuation(last_child._string):
							new_children.append(child)
						elif last_child.is_similar_to(child, ignore_depth=ignore_depth):
							last_child.absorb(child)
						else:
							new_children.append(child)

			if remove_short_strings:
				new_children_2 = []
				for child in new_children:
					if child._is_short:
						child.log(f'short child removed in simplify by {self.id}')
					else:
						new_children_2.append(child)
			else:
				new_children_2 = new_children

			if min_alphabetic_ratio > 0:
				new_children_3 = []

				for child in new_children_2:
					if child._string is None:
						new_children_3.append(child)
					else:
						alphabetic_ratio = get_alphabetic_ratio(child._string)
						if not child._string or alphabetic_ratio > min_alphabetic_ratio:
							new_children_3.append(child)
						else:
							child.log(
								message=f'removed by {self.id} because alphabetic ratio {alphabetic_ratio} < {min_alphabetic_ratio}'
							)
			else:
				new_children_3 = new_children_2

			if min_english_ratio > 0 and self._vocabulary:
				new_children_4 = []
				for child in new_children_3:
					if child._string is None:
						new_children_4.append(child)
					else:
						ratio_of_english_words = get_ratio_of_english_words(
							child._string, vocabulary=self._vocabulary, case_sensitive=False
						)
						if not child._string or ratio_of_english_words > min_english_ratio or get_words(child._string) < 5:
							new_children_4.append(child)
						else:
							child.log(
								message=f'removed by {self.id} because ratio of english {ratio_of_english_words} < {min_english_ratio}'
							)
			else:
				new_children_4 = new_children_3

			self._children = new_children_4
		self.clean_up(remove_tables=remove_tables)
		return self

	# MERGING

	def is_similar_to(self, other, ignore_depth=False):
		"""
		:type other: HtmlText
		:type ignore_depth: bool
		:rtype: bool
		"""
		if self._depth != other._depth and not ignore_depth:
			return False
		if self._font_size is not None and other._font_size is not None and self._font_size < other._font_size:
			return False
		else:
			return (self._children is None and other._children is None) or (self._children is not None and other._children is not None)

	def absorb(self, other):
		"""
		:type other: HtmlText
		"""
		self.log(f'absorbs {other.id}')
		if self._is_title or other._is_title:
			raise RuntimeError(f'cannot absorb a title {other} into another {self}')

		if self._is_table and not other._is_table:
			raise RuntimeError(f'table cannot absorb non table')

		if not self._is_table and other._is_table:
			raise RuntimeError(f'table cannot be absorbed by non table')

		if self._children is None:
			self._string = self._string.strip()
			other._string = other._string.strip()
			if self._string:
				self._string += self._sep + other._string
			else:
				self._string += other._string
			other._string = None
			other.log(f'absorbed by {self.id}')
		else:
			self._children += other._children
			other._children = None
			other.log(f'children absorbed by {self.id}')

		if self._font_size and other._font_size:
			self._font_size = max(self._font_size, other._font_size)
		elif other._font_size:
			self._font_size = other._font_size

		self._clean = self._clean and other._clean
		self.parent._clean = False
		other.parent._clean = False

	def become_first_child(self, ignore_depth):
		single_child = self.children[0]
		self.log(f'becomes first child {single_child.id}')
		single_child.simplify(ignore_depth=ignore_depth)
		if single_child.children is None:
			self._string = single_child._string
			self._children = None
			single_child.log(f'taken over by parent {self.id}')
		else:
			self._children = single_child.children
			single_child.log(f'children taken over by parent {self.id}')

		self._is_title = self._is_title or single_child._is_title
		self._is_table = self._is_table or single_child._is_table
		self._border_size = self._border_size or single_child._border_size
		self._font_size = self._font_size or single_child._font_size
		self._clean = self._clean and single_child._clean

	#  CHILDREN

	def has_children(self):
		return self._children is not None

	@property
	def children(self):
		"""
		:rtype: list[HtmlText]
		"""
		return self._children

	def __getitem__(self, item):
		return self._children_dictionary[item]

	# STRING

	def get_string(self):
		if self._string is None and self._children is None:
			raise RuntimeError(f'cannot display an empty text {self.id}')
		elif self._children is None:
			if self._is_title:
				string = f'* {self._string} *'
			else:
				string = f'"{self._string}"'

			if self._font_size:
				string = f'({self._font_size}):{string}'

			if self._is_table:
				string = f'|| {string} ||'
			elif self._border_size:
				string = f'| {string} |'

			return f'{self.id} <{self._depth}> {string}'
		else:
			if any([child.has_children() for child in self.children]):
				return self._strong_sep.join([child.get_string() for child in self.children])
			else:

				return self._sep.join([child.get_string() for child in self.children])

	def get_paragraphs(self, paragraph_max=50, text_as_string=True):
		"""
		:rtype: str or list[str or list[str] or list[list]]
		"""

		if self.children:
			result = []
			for child in self.children:
				text = child.get_paragraphs(paragraph_max=paragraph_max, text_as_string=text_as_string)
				total_paragraph_font_size = 0
				num_strings = 0

				if isinstance(text, Text):
					if text_as_string:
						result += text.paragraphs
					else:
						result.append(text)
					if text.font_size:
						total_paragraph_font_size += text.font_size
						num_strings += len(text.paragraphs)
				else:
					# append the title
					result.append(text)

				# remove titles with font size smaller than average paragraph font size
				'''
				if total_paragraph_font_size > 0 and num_strings > 0:
					mean_paragraph_font_size = total_paragraph_font_size / num_strings
					result = [x for x in result if not isinstance(x, Title) or x.font_size > mean_paragraph_font_size]
				'''
			return result
		else:
			if self._string is None:
				print(f'error being raised for child of {self.parent._tag}')
				raise ValueError(f' has no string!')
			string = ' '.join(self._string.split())
			if self._is_title:
				return Title(string, font_size=self._font_size)
			else:
				return Text(
					string, font_size=self._font_size, paragraph_max=paragraph_max, language=self._language
				)

	def __str__(self):
		return self.get_string()

	def __repr__(self):
		return str(self)


