from difflib import SequenceMatcher
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

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
