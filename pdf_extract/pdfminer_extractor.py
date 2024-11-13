import os
from io import StringIO
from pathlib import Path

import pdf2image
from loguru import logger
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdf_extract.interface import ITextExtractor


class PDFMinerExtractor(ITextExtractor):
    def pdf_to_txt(
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int = 1,
        last_page: int | None = None,
    ) -> None:
        basename = Path(filename).stem
        num_pages: int = pdf2image.pdfinfo_from_path(str(filename))['Pages']
        last_page = min(last_page or num_pages, num_pages)
        pagestr = StringIO()
        with open(filename, 'rb') as fp_in:
            parser = PDFParser(fp_in)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, pagestr, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for i, page in enumerate(PDFPage.create_pages(doc)):
                if i not in range(first_page - 1, last_page):
                    continue
                interpreter.process_page(page)
                with open(Path(output_folder) / f'{basename}_{i+1:04}.txt', 'w', encoding='utf-8') as fp_out:
                    fp_out.write(pagestr.getvalue())
                pagestr.truncate(0)
                pagestr.seek(0)
        logger.success(f'Extracted: {basename}, pages: {num_pages}')


if __name__ == '__main__':
    pass
