import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pytest

from pdf_extract.interface import ITextExtractor
from pdf_extract.java_extractor import ExtractedPage, ExtractedPages, JavaExtractor, get_pdfbox_path
from pdf_extract.utils import get_filenames

test_dir = Path('tests/fixtures/')


class TestGetPdfboxPath:
    def test_get_pdfbox_path_returns_valid_path(self):
        assert get_pdfbox_path().exists()

    def test_get_pdfbox_path_raises_runtime_error_when_pdfbox_not_found(self, monkeypatch):
        with TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir)
            monkeypatch.setattr('pdf_extract.java_extractor.AppDirs.user_cache_dir', app_dir)

            with pytest.raises(RuntimeError):
                get_pdfbox_path()

    def test_get_pdfbox_path_returns_latest_path(self, monkeypatch):
        with TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir)
            monkeypatch.setattr('pdf_extract.java_extractor.AppDirs.user_cache_dir', app_dir)
            (app_dir / 'pdfbox-app-1.0.0.jar').touch()
            (app_dir / 'pdfbox-app-1.0.1.jar').touch()
            assert get_pdfbox_path().name == 'pdfbox-app-1.0.1.jar'


class TestExtractedPages:
    def test_extracted_pages_str_returns_concatenated_content(self):
        pages = ExtractedPages([ExtractedPage(1, 'a', []), ExtractedPage(2, 'b', [])])
        assert str(pages) == 'a\n\nb'

    def test_extracted_pages_len_returns_number_of_pages(self):
        pages = ExtractedPages([ExtractedPage(1, 'a', []), ExtractedPage(2, 'b', [])])
        assert len(pages) == 2

    def test_extracted_pages_getitem_returns_extracted_page(self):
        pages = ExtractedPages([ExtractedPage(1, 'a', []), ExtractedPage(2, 'b', [])])
        assert pages[0].content == 'a'
        assert pages[1].content == 'b'

    def test_extracted_pages_get_page_returns_extracted_page(self):
        pages = ExtractedPages([ExtractedPage(1, 'a', []), ExtractedPage(2, 'b', [])])
        assert pages.get_page(1).content == 'a'
        assert pages.get_page(2).content == 'b'

    def test_extracted_pages_get_page_raises_index_error_when_page_number_out_of_range(self):
        pages = ExtractedPages([ExtractedPage(1, 'a', []), ExtractedPage(2, 'b', [])])
        with pytest.raises(IndexError):
            pages.get_page(3)

    def test_extracted_pages_get_page_raises_index_error_when_page_number_is_zero(self):
        pages = ExtractedPages([ExtractedPage(1, 'a', []), ExtractedPage(2, 'b', [])])
        with pytest.raises(IndexError):
            pages.get_page(0)

    def test_extracted_pages_get_page_raises_index_error_when_page_number_is_negative(self):
        pages = ExtractedPages([ExtractedPage(1, 'a', []), ExtractedPage(2, 'b', [])])
        with pytest.raises(IndexError):
            pages.get_page(-1)

    def test_extracted_pages_get_page_raises_index_error_when_pages_is_empty(self):
        pages = ExtractedPages([])
        with pytest.raises(IndexError):
            pages.get_page(1)


@pytest.mark.java
class TestJavaExtractor:
    @pytest.mark.parametrize(
        'input_pdf, first_page, last_page, expected',
        [
            ('2_pages_1_empty.pdf', 1, None, 2),
            ('3_pages.pdf', 2, 100, 2),
            ('3_pages.pdf', 100, None, 0),
        ],
    )
    def test_pdf_to_txt_returns_correct_number_of_pages(self, input_pdf, first_page, last_page, expected):
        with TemporaryDirectory() as output_dir:
            file: Path = Path(test_dir / 'pdf' / input_pdf)
            extractor: ITextExtractor = JavaExtractor()
            extractor.pdf_to_txt(file, output_dir, first_page=first_page, last_page=last_page)
            result = len(list(Path(output_dir).iterdir()))
            assert result == expected
            assert not (Path(output_dir) / 'extract.log').exists()

    def test_batch_extract_generates_expected_output(self):
        """Tests if batch_extract generates expected output. Output should be identical pdfbox_extractor's."""
        with TemporaryDirectory() as output_dir:
            files: List[Path] = get_filenames(test_dir / 'test.pdf')
            extractor: ITextExtractor = JavaExtractor()
            extractor.batch_extract(files, output_dir, first_page=1, last_page=None)

            assert len(sorted(Path(output_dir).glob('*.txt'))) == 8
            assert (Path(output_dir) / 'extract.log').exists()
            assert not filecmp.dircmp(output_dir, test_dir / 'expected/pdfbox').diff_files
            assert len(filecmp.dircmp(output_dir, test_dir / 'not_expected').diff_files) == 1
