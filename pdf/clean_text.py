REMOVABLE_STRINGS = ['•', '\uf0a7']


from pkg_resources import resource_filename
from symspellpy import SymSpell
from bs4 import NavigableString


SYM_SPELL = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)


SYM_SPELL.load_dictionary(
	resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt"),
	term_index=0,
	count_index=1
)


SYM_SPELL.load_bigram_dictionary(
	resource_filename("symspellpy", "frequency_bigramdictionary_en_243_342.txt"),
	term_index=0,
	count_index=2
)


def fix_spelling(s):
	suggestions = SYM_SPELL.lookup_compound(s, max_edit_distance=2)
	return suggestions[0].term

def clean_text(s):
	"""
	:type s: str
	:rtype: str
	"""
	if isinstance(s, NavigableString):
		s = str(s)
	elif not isinstance(s, str):
		return s

	for removable in REMOVABLE_STRINGS:
		s = s.replace(removable, ' ')
	s = s.strip()
	s = ' '.join(s.split())

	return fix_spelling(s=s)
