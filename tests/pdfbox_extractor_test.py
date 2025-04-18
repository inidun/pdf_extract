import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pdfbox
import pytest

from pdf_extract.interface import ITextExtractor
from pdf_extract.pdfbox_extractor import PDFBoxExtractor
from pdf_extract.utils import get_filenames

test_dir = Path('tests/fixtures/')


@pytest.mark.java
class TestPDFBoxExtractText:

    def test_python_pdfbox_extract_text_generates_correct_output(self):
        file = test_dir / 'test.pdf'
        expected_output = test_dir / 'test.txt'
        p = pdfbox.PDFBox()

        with TemporaryDirectory() as output_dir:
            output_path = (Path(output_dir) / f'{file.stem}.txt').resolve()
            p.extract_text(file, output_path=output_path)

            assert output_path.exists()
            assert len(list(Path(output_dir).iterdir())) == 1
            assert filecmp.cmp(output_path, expected_output) is True

    def test_extract_text_generates_expected_output(self):
        file = test_dir / 'test.pdf'
        expected = test_dir / 'test.txt'
        extractor: PDFBoxExtractor = PDFBoxExtractor()

        with TemporaryDirectory() as output_dir:
            extractor.extract_text(file, output_dir)
            result = Path(output_dir) / f'{file.stem}.txt'
            assert result.exists()
            assert filecmp.cmp(result, expected) is True

    def test_extract_text_with_page_numbers_generates_expected_output(self):
        file = test_dir / 'test.pdf'
        expected = test_dir / 'expected/pdfbox_page_numbers/test.txt'
        extractor: PDFBoxExtractor = PDFBoxExtractor()

        with TemporaryDirectory() as output_dir:
            extractor.extract_text(file, output_dir, page_numbers=True)
            result = Path(output_dir) / f'{file.stem}.txt'
            assert result.exists()
            assert filecmp.cmp(result, expected) is True

    @pytest.mark.parametrize(
        'input_pdf, first_page, last_page, expected',
        [
            ('test.pdf', 1, None, 'test.txt'),
            ('test.pdf', 2, None, 'test_2-8.txt'),
            ('test.pdf', 1, 4, 'test_1-4.txt'),
            ('test.pdf', 3, 5, 'test_3-5.txt'),
            ('test.pdf', 6, 9, 'test_6-8.txt'),
        ],
    )
    def test_extract_text_adds_page_numbers_to_filename_if_not_all_pages_are_extracted(
        self, input_pdf, first_page, last_page, expected
    ):
        file = test_dir / input_pdf

        extractor: PDFBoxExtractor = PDFBoxExtractor()

        with TemporaryDirectory() as output_dir:
            extractor.extract_text(file, output_dir, first_page=first_page, last_page=last_page)

            result = Path(output_dir) / expected
            assert result.exists()

    def test_extract_text_when_output_file_exists_skips_extraction(self, caplog):
        file = test_dir / 'test.pdf'
        expected = test_dir / 'test.txt'
        extractor: PDFBoxExtractor = PDFBoxExtractor()

        with TemporaryDirectory() as output_dir:
            output_file = Path(output_dir) / f'{file.stem}.txt'
            output_file.write_text('test')
            extractor.extract_text(file, output_dir)
            result = Path(output_dir) / f'{file.stem}.txt'
            assert result.exists()
            assert filecmp.cmp(result, expected) is False
            assert result.read_text() == 'test'
            assert 'Skipping' in caplog.text
            assert 'Already extracted' in caplog.text


@pytest.mark.java
class TestPDFBoxBatchExtract:
    def test_batch_extract_generates_expected_output(self):
        files: List[Path] = get_filenames(test_dir / 'test.pdf')
        extractor: ITextExtractor = PDFBoxExtractor()

        with TemporaryDirectory() as output_dir:
            extractor.batch_extract(files, output_dir)

            assert len(sorted(Path(output_dir).glob('*.txt'))) == 8
            assert (Path(output_dir) / 'extract.log').exists()
            assert not filecmp.dircmp(output_dir, test_dir / 'expected/pdfbox').diff_files
            assert len(filecmp.dircmp(output_dir, test_dir / 'not_expected').diff_files) == 1
