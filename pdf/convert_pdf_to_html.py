import os
from disk import Path
import pdfminer
import pdfminer.layout
import pdfminer.high_level
import sys
from time import sleep
from .exceptions import PdfError

OUTPUT_TYPES = (
    (".htm", "html"),
    (".html", "html"),
    (".xml", "xml"),
    (".tag", "tag")
)


def convert_pdf_to_html_using_command(pdf_path, html_path):
    if isinstance(pdf_path, Path):
        pdf_path = pdf_path.path
    if isinstance(html_path, Path):
        html_path = html_path.path
    os.system(f'pdf2txt.py -o "{html_path}" "{pdf_path}"')


def extract_text(
        files=None, outfile='-',
        no_laparams=False, all_texts=None, detect_vertical=None,
        word_margin=None, char_margin=None, line_margin=None,
        boxes_flow=None, output_type='text', codec='utf-8',
        strip_control=False, maxpages=0, page_numbers=None,
        password="", scale=1.0, rotation=0, layoutmode='normal',
        output_dir=None, debug=False, disable_caching=False,
        **kwargs
):
    files = files or []
    if not files:
        raise ValueError("Must provide files to work upon!")

    # If any LAParams group arguments were passed,
    # create an LAParams object and
    # populate with given args. Otherwise, set it to None.
    if not no_laparams:
        laparams = pdfminer.layout.LAParams()
        params = ("all_texts", "detect_vertical", "word_margin", "char_margin", "line_margin", "boxes_flow")
        for param in params:
            paramv = locals().get(param, None)
            if paramv is not None:
                setattr(laparams, param, paramv)
    else:
        laparams = None

    if output_type == "text" and outfile != "-":
        for override, alttype in OUTPUT_TYPES:
            if outfile.endswith(override):
                output_type = alttype

    if outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            codec = 'utf-8'

        for fname in files:
            with open(fname, "rb") as fp:
                pdfminer.high_level.extract_text_to_fp(fp, **locals())
        return outfp

    else:
        with open(outfile, "wb") as outfp:
            for fname in files:
                with open(fname, "rb") as fp:
                    pdfminer.high_level.extract_text_to_fp(fp, **locals())
        return None


def convert_pdf_to_html(pdf_path, html_path, num_tries=3):
    if isinstance(pdf_path, Path):
        pdf_path = pdf_path.path
    if isinstance(html_path, Path):
        html_path = html_path.path

    for i in range(num_tries):
        extract_text(
            files=[pdf_path], debug=False, disable_caching=False, page_numbers=None, pagenos=None, maxpages=0,
            password='', rotation=0, no_laparams=False, detect_vertical=False, char_margin=2.0,
            word_margin=0.1, line_margin=0.5, boxes_flow=0.5, all_texts=True, outfile=html_path,
            output_type='html', codec='utf-8',
            output_dir=None, layoutmode='normal', scale=1.0, strip_control=False
        )
        if Path(html_path).exists():
            break
        else:
            sleep(2 ** i)
    else:
        error_message = f'error_converting_"{pdf_path}"_to_html'
        Path(html_path).save(obj=error_message)
        raise PdfError(error_message)



