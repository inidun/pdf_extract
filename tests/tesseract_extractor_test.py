import filecmp
from difflib import SequenceMatcher
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pytest

from pdf_extract.interface import ITextExtractor
from pdf_extract.tesseract_extractor import TesseractExtractor
from pdf_extract.utils import get_filenames

test_dir = Path('tests/fixtures/')


def test_extract_extracts_right_amount_of_files():
    with TemporaryDirectory() as output_dir:
        files: List[Path] = get_filenames(test_dir / 'test.pdf')
        extractor: ITextExtractor = TesseractExtractor(dpi=1, fmt='png')
        extractor.batch_extract(files, output_dir)

        assert len(sorted(Path(output_dir).glob('*.txt'))) == 8
        assert (Path(output_dir) / 'extract.log').exists()


def test_pdf_to_alto_generates_expected_output():
    file = test_dir / 'test.pdf'
    expected = test_dir / 'expected/alto/test_0001.alto'
    extractor: TesseractExtractor = TesseractExtractor()

    with TemporaryDirectory() as output_dir:
        extractor.pdf_to_alto(file, output_dir, first_page=1, last_page=1)
        result = Path(output_dir) / 'test_0001.alto'
        assert result.exists()

        with open(result, 'r', encoding='utf-8') as r, open(expected, 'r', encoding='utf-8') as e:
            assert SequenceMatcher(None, r.read(), e.read()).quick_ratio() > 0.99


def test_pdf_to_hocr_generates_expected_output():
    file = test_dir / 'test.pdf'
    expected = test_dir / 'expected/hocr/test_0001.hocr'
    extractor: TesseractExtractor = TesseractExtractor(dpi=50, fmt='png')

    with TemporaryDirectory() as output_dir:
        extractor.pdf_to_hocr(file, output_dir, first_page=1, last_page=1)
        result = Path(output_dir) / 'test_0001.hocr'
        assert result.exists()

        with open(result, 'r', encoding='utf-8') as r, open(expected, 'r', encoding='utf-8') as e:
            assert SequenceMatcher(None, r.read(), e.read()).quick_ratio() > 0.99


@pytest.mark.skip('Files not guaranteed to be identical')
@pytest.mark.parametrize(
    'input_file, first_page, page_numbers, expected_filename',
    [
        ('pdf/2_pages_1_empty.pdf', 2, False, 'extract_text/2_pages_1_empty_2-2.txt'),
        ('pdf/2_pages_1_empty.pdf', None, False, 'extract_text/2_pages_1_empty.txt'),
        ('pdf/2_pages_1_empty.pdf', 2, True, 'extract_text_with_page_numbers/2_pages_1_empty_2-2.txt'),
        ('pdf/2_pages_1_empty.pdf', None, True, 'extract_text_with_page_numbers/2_pages_1_empty.txt'),
    ],
)
def test_extract_text_generates_expected_output(input_file, first_page, page_numbers, expected_filename):
    file = test_dir / input_file
    extractor: TesseractExtractor = TesseractExtractor(dpi=350, fmt='png')
    expected = test_dir / 'expected/tesseract' / expected_filename

    with TemporaryDirectory() as output_dir:
        extractor.extract_text(file, output_dir, first_page=first_page, page_numbers=page_numbers)
        result = Path(output_dir) / Path(expected_filename).name
        assert result.exists()
        assert filecmp.cmp(result, expected) is True
