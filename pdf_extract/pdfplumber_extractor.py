import os
from pathlib import Path
from typing import Any

import pdfplumber
from loguru import logger

from pdf_extract.interface import ITextExtractor


class PDFPlumberExtractor(ITextExtractor):
    def pdf_to_txt(
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int = 1,
        last_page: int | None = None,
    ) -> None:
        basename = Path(filename).stem
        with pdfplumber.open(filename) as pdf:  # type: ignore[arg-type]
            num_pages: int = len(pdf.pages)
            last_page = min(last_page or num_pages, num_pages)
            pages = range(first_page - 1, last_page)
            for i in pages:
                page = pdf.pages[i]
                if page is not None:
                    data = page.extract_text()
                    if data is None:
                        data = ''
                    output_path = Path(output_folder) / f'{basename}_{i+1:04}.txt'
                    with open(output_path, 'w', encoding='utf-8') as fp:
                        fp.write(data)
        logger.success(f'Extracted: {basename}, pages: {num_pages}')

    def extract_text(
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int | None = 1,
        last_page: int | None = None,
        page_numbers: bool = False,
    ) -> None:
        first_page: int = first_page or 1
        basename = Path(filename).stem

        # TODO: Add as arguments
        extract_text_config: dict[str, Any] = {'layout': False}
        extract_words_config: dict[str, Any] = {'use_text_flow': False}

        with pdfplumber.open(filename) as pdf:  # type: ignore[arg-type]
            num_pages: int = len(pdf.pages)
            last_page = min(last_page or num_pages, num_pages)

            ouput_filename: str = (
                f'{basename}_{first_page}-{last_page}.txt'
                if last_page < num_pages or first_page > 1
                else f'{basename}.txt'
            )

            output_filepath: Path = Path(output_folder) / ouput_filename

            if output_filepath.exists():
                logger.info(f'Skipping {basename}: Already extracted')
                return

            logger.info(f'Processing {basename}, pages: {first_page}-{last_page}')

            text: list[str] = []

            pages = range(first_page - 1, last_page)
            for i in pages:
                if page_numbers:
                    text.append(f'## Page {i+1}\n')
                page = pdf.pages[i]
                if page is not None:
                    text.append(page.extract_text(**extract_text_config, **extract_words_config) or '')

        with open(output_filepath, 'w', encoding='utf-8') as fp:
            fp.write('\n\n'.join(text))

        logger.success(f'Extracted: {basename}, pages: {first_page}-{last_page}')


if __name__ == '__main__':
    pass
