class PdfError(TypeError):
	pass


class HtmlTextError(RuntimeError):
	pass


class EmptyTagError(HtmlTextError):
	pass


class MissingTagError(HtmlTextError):
	pass


class MissingIndexError(HtmlTextError):
	pass


class AbsorptionError(HtmlTextError):
	pass


class HtmlTextDisplayError(HtmlTextError):
	pass


class ConversionError(PdfError):
	pass
