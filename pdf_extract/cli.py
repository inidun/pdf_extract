import os
from pathlib import Path

import argh
from argh import arg

from pdf_extract.interface import ITextExtractor
from pdf_extract.java_extractor import JavaExtractor
from pdf_extract.pdfbox_extractor import PDFBoxExtractor
from pdf_extract.pdfminer_extractor import PDFMinerExtractor
from pdf_extract.pdfplumber_extractor import PDFPlumberExtractor
from pdf_extract.tesseract_extractor import TesseractExtractor
from pdf_extract.utils import get_filenames


def get_extractor(extractor: str) -> ITextExtractor:
    if extractor == 'JavaExtractor':
        return JavaExtractor()
    if extractor == 'PDFBox':
        return PDFBoxExtractor()
    if extractor == 'PDFBoxHTML':
        return PDFBoxExtractor(html=True)
    if extractor == 'PDFMiner':
        return PDFMinerExtractor()
    if extractor == 'PDFPlumber':
        return PDFPlumberExtractor()
    if extractor == 'Tesseract':
        return TesseractExtractor()
    raise ValueError(extractor)


@arg('--extractor', choices=['JavaExtractor', 'PDFBox', 'PDFBoxHTML', 'PDFMiner', 'PDFPlumber', 'Tesseract'])
def extract(
    input_path: str | os.PathLike[str],
    output_folder: str | os.PathLike[str],
    first_page: int = 1,
    last_page: int | None = None,
    extractor: str = 'PDFBox',
) -> None:
    Path(output_folder).mkdir(exist_ok=True, parents=True)
    files: list[Path] = get_filenames(input_path)

    if last_page is not None:
        last_page = int(last_page)

    extractor: ITextExtractor = get_extractor(extractor)
    extractor.batch_extract(files, output_folder, first_page=first_page, last_page=last_page)


if __name__ == '__main__':
    argh.dispatch_command(extract)
