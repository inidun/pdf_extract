import csv
import os
from pathlib import Path
from typing import TypedDict

import argh
from loguru import logger

from pdf_extract.pdfbox_extractor import PDFBoxExtractor
from pdf_extract.utils import get_filenames


class Job(TypedDict):
    filename: str | os.PathLike
    output_folder: str | os.PathLike
    first_page: int
    last_page: int | None
    page_numbers: bool


def extract(
    input_folder: str | os.PathLike, output_folder: str | os.PathLike, metadata_file: str | os.PathLike
) -> None:

    input_folder: Path = Path(input_folder)
    output_folder: Path = Path(output_folder)

    pdf_filenames: list[Path] = get_filenames(input_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    extractor: PDFBoxExtractor = PDFBoxExtractor()

    logfile = Path(output_folder) / 'extract.log'
    file_logger = logger.add(
        Path(logfile),
        format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}',
    )

    with open(metadata_file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        pdf_pages = {f"{x['year']}_{x['filename']}.pdf": x['pdf_page_numbers'] for x in reader}

    jobs = []

    for filename in pdf_filenames:
        if filename.name not in pdf_pages:
            logger.warning(f'error: {filename.stem} not found')
            continue

        pages_to_extract = str(pdf_pages.get(str(filename.name)))
        page_spans = [list(map(int, p.split('-'))) for p in pages_to_extract.split(';')]

        for first_page, last_page in page_spans:
            jobs.append(
                Job(
                    filename=filename,
                    output_folder=output_folder,
                    first_page=first_page,
                    last_page=last_page,
                    page_numbers=True,
                )
            )

            logger.info(f'Added job: {filename.name:20} ({first_page}-{last_page})')

    for job in jobs:
        extractor.extract_text(**job)

    logger.remove(file_logger)


if __name__ == '__main__':
    argh.dispatch_command(extract)
