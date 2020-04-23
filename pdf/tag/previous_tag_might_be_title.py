from .get_children import get_children
from .is_break import is_break


# if a tag starts with a br this might belong to the previous tag which would make that one a title
def previous_tag_might_be_title(tag, children=None):
	if children is None:
		tag_children = get_children(tag)
	else:
		tag_children = children

	if tag_children and len(tag_children) > 1 and is_break(tag_children[0]):
		return True
	else:
		return False
