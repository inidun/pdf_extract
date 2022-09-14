import filecmp

# import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pytest

from pdf_extract.interface import ITextExtractor
from pdf_extract.pdfplumber_extractor import PDFPlumberExtractor
from pdf_extract.utils import get_filenames

test_dir = Path('tests/fixtures/')


def test_extract_generates_expected_output():
    with TemporaryDirectory() as output_dir:
        files: List[Path] = get_filenames(test_dir / 'pdf')
        extractor: ITextExtractor = PDFPlumberExtractor()
        extractor.batch_extract(files, output_dir)

        assert len(sorted(Path(output_dir).glob('*.txt'))) == 5
        assert not filecmp.dircmp(output_dir, test_dir / 'expected/pdfplumber').diff_files
        assert (Path(output_dir) / 'extract.log').exists()


@pytest.mark.parametrize(
    'first_page, last_page, expected',
    [
        (1, None, 5),  # empty page
        (2, 100, 3),  # last page out of bounds
        (100, None, 0),  # first page out of bounds
    ],
)
def test_extract_returns_correct_number_of_pages(first_page, last_page, expected):
    with TemporaryDirectory() as output_dir:
        files: List[Path] = get_filenames(test_dir / 'pdf')
        extractor: ITextExtractor = PDFPlumberExtractor()
        extractor.batch_extract(files, output_dir, first_page=first_page, last_page=last_page)
        result = len(sorted(Path(output_dir).glob('*.txt')))
        assert result == expected
        assert (Path(output_dir) / 'extract.log').exists()


@pytest.mark.parametrize(
    'input_pdf, first_page, last_page, expected',
    [
        ('2_pages_1_empty.pdf', 1, None, 2),
        ('3_pages.pdf', 2, 100, 2),
        ('3_pages.pdf', 100, None, 0),
    ],
)
def test_pdf_to_txt_returns_correct_number_of_pages(input_pdf, first_page, last_page, expected):
    with TemporaryDirectory() as output_dir:
        file: Path = Path(test_dir / 'pdf' / input_pdf)
        extractor: ITextExtractor = PDFPlumberExtractor()
        extractor.pdf_to_txt(file, output_dir, first_page=first_page, last_page=last_page)
        result = len(list(Path(output_dir).iterdir()))
        assert result == expected
        assert not (Path(output_dir) / 'extract.log').exists()
