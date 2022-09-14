import filecmp
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pytest

from pdf_extract.interface import ITextExtractor
from pdf_extract.java_extractor import JavaExtractor, get_pdfbox_path
from pdf_extract.utils import get_filenames

test_dir = Path('tests/fixtures/')


def test_get_pdfbox_path_returns_valid_path_and_emits_no_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        assert get_pdfbox_path().exists()
        assert len(w) == 0


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
        extractor: ITextExtractor = JavaExtractor()
        extractor.pdf_to_txt(file, output_dir, first_page=first_page, last_page=last_page)
        result = len(list(Path(output_dir).iterdir()))
        assert result == expected
        assert not (Path(output_dir) / 'extract.log').exists()


@pytest.mark.java
def test_batch_extract_generates_expected_output():
    """Tests if batch_extract generates expected output. Output should be identical pdfbox_extractor's."""
    with TemporaryDirectory() as output_dir:
        files: List[Path] = get_filenames(test_dir / 'test.pdf')
        extractor: ITextExtractor = JavaExtractor()
        extractor.batch_extract(files, output_dir, first_page=1, last_page=None)

        assert len(sorted(Path(output_dir).glob('*.txt'))) == 8
        assert (Path(output_dir) / 'extract.log').exists()
        assert not filecmp.dircmp(output_dir, test_dir / 'expected/pdfbox').diff_files
        assert len(filecmp.dircmp(output_dir, test_dir / 'not_expected').diff_files) == 1
