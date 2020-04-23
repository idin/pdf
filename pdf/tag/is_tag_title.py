from .get_children import get_children
from .get_text import get_text
from .is_break import is_break
from ..string import ends_with_punctuation
from ..string import is_capitalized
from ..string import count_words


def is_tag_title(tag, children=None):
	if children is None:
		tag_children = get_children(tag)
	else:
		tag_children = children

	# if this tag has only two children and the second one is a br then it's a title
	if len(tag_children) == 2 and is_break(tag_children[-1]):
		tag_children.pop()
		only_child = tag_children[0]
		child_text = get_text(only_child)
		if child_text:
			if not ends_with_punctuation(child_text) and count_words(child_text) < 13:
				return True
			else:
				return is_capitalized(child_text)
		else:
			return False

	else:
		return False
