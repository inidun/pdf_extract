import os
from pathlib import Path
from typing import List, Optional, Union

import argh
from argh import arg

from .interface import ITextExtractor
from .java_extractor import JavaExtractor
from .pdfbox_extractor import PDFBoxExtractor
from .pdfminer_extractor import PDFMinerExtractor
from .pdfplumber_extractor import PDFPlumberExtractor
from .tesseract_extractor import TesseractExtractor
from .utils import get_filenames


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


@arg('--extractor', choices=['JavaExtractor', 'PDFBox', 'PDFBoxHTML', 'PDFMiner', 'PDFPlumber', 'Tesseract'])  # type: ignore
def extract(
    input_path: Union[str, os.PathLike],
    output_folder: Union[str, os.PathLike],
    first_page: int = 1,
    last_page: Optional[int] = None,
    extractor: str = 'PDFBox',
) -> None:

    Path(output_folder).mkdir(exist_ok=True, parents=True)
    files: List[Path] = get_filenames(input_path)

    if last_page is not None:
        last_page = int(last_page)

    extractor: ITextExtractor = get_extractor(extractor)
    extractor.batch_extract(files, output_folder, first_page=first_page, last_page=last_page)


if __name__ == '__main__':
    argh.dispatch_command(extract)
