from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from pdf_extract.cli import extract, get_extractor
from pdf_extract.java_extractor import JavaExtractor
from pdf_extract.pdfbox_extractor import PDFBoxExtractor
from pdf_extract.pdfminer_extractor import PDFMinerExtractor
from pdf_extract.pdfplumber_extractor import PDFPlumberExtractor
from pdf_extract.tesseract_extractor import TesseractExtractor


@pytest.mark.java
@pytest.mark.parametrize(
    'method, instance',
    [
        ('JavaExtractor', JavaExtractor),
        ('PDFBox', PDFBoxExtractor),
        ('PDFMiner', PDFMinerExtractor),
        ('PDFPlumber', PDFPlumberExtractor),
        ('Tesseract', TesseractExtractor),
    ],
)
def test_get_extractor_returns_subclass_of_itextextractor(method, instance):
    extractor = get_extractor(method)
    assert isinstance(extractor, instance)


def test_get_extractor_with_unknown_method_raises_value_error():
    with pytest.raises(ValueError):
        get_extractor('Unknown method')


@pytest.mark.java
@pytest.mark.parametrize(
    'extractor, first_page, last_page, expected',
    [
        ('JavaExtractor', 1, None, 5),
        ('JavaExtractor', 2, 100, 3),
        ('JavaExtractor', 100, None, 0),
        ('PDFBox', 1, None, 5),
        ('PDFBox', 2, 100, 3),
        ('PDFBox', 100, None, 0),
        ('PDFBoxHTML', 1, None, 5),
        ('PDFBoxHTML', 2, 100, 3),
        ('PDFBoxHTML', 100, None, 0),
        ('PDFMiner', 1, None, 5),
        ('PDFMiner', 2, 100, 3),
        ('PDFMiner', 100, None, 0),
        ('PDFPlumber', 1, None, 5),
        ('PDFPlumber', 2, 100, 3),
        ('PDFPlumber', 100, None, 0),
        pytest.param('Tesseract', 1, None, 5, marks=pytest.mark.slow),  # FIXME: Patch tesseract settings
        pytest.param('Tesseract', 2, 100, 3, marks=pytest.mark.slow),
        pytest.param('Tesseract', 100, None, 0, marks=pytest.mark.slow),
    ],
)
def test_extract(extractor, first_page, last_page, expected):
    with TemporaryDirectory() as output_dir:
        extract(
            Path('tests/fixtures/pdf'),
            output_dir,
            first_page=first_page,
            last_page=last_page,
            extractor=extractor,
        )
        result = len(sorted(Path(output_dir).glob('*.txt')))
        assert result == expected
        assert (Path(output_dir) / 'extract.log').exists()


@pytest.mark.java
@pytest.mark.parametrize(
    'extractor, first_page, last_page, expected',
    [
        ('JavaExtractor', 1, None, 2),
        ('PDFBox', 1, None, 2),
        ('PDFBoxHTML', 1, None, 2),
        ('PDFMiner', 1, None, 2),
        ('PDFPlumber', 1, None, 2),
        pytest.param('Tesseract', 1, None, 2, marks=pytest.mark.slow),  # FIXME: Patch tesseract settings
    ],
)
def test_extract_with_logfile_partially_completed_jobs(extractor, first_page, last_page, expected):
    with TemporaryDirectory() as output_dir:
        with open(Path(output_dir) / 'extract.log', 'w', encoding='utf-8') as fp:
            fp.write('2022-01-01 12:00:00.000 | SUCCESS | Extracted: 3_pages, pages: 3')
        assert (Path(output_dir) / 'extract.log').exists()
        extract(
            Path('tests/fixtures/pdf'),
            output_dir,
            first_page=first_page,
            last_page=last_page,
            extractor=extractor,
        )
        result = len(sorted(Path(output_dir).glob('*.txt')))
        assert result == expected


@pytest.mark.java
@pytest.mark.parametrize(
    'extractor, first_page, last_page, expected',
    [
        ('JavaExtractor', 1, None, 0),
        ('PDFBox', 1, None, 0),
        ('PDFBoxHTML', 1, None, 0),
        ('PDFMiner', 1, None, 0),
        ('PDFPlumber', 1, None, 0),
        ('Tesseract', 1, None, 0),  # FIXME: Patch tesseract settings
    ],
)
def test_extract_with_logfile_fully_completed_jobs(extractor, first_page, last_page, expected):
    with TemporaryDirectory() as output_dir:
        with open(Path(output_dir) / 'extract.log', 'w', encoding='utf-8') as fp:
            fp.writelines(
                [
                    '2022-01-01 12:00:00.000 | SUCCESS | Extracted: 3_pages, pages: 3\n',
                    '2022-01-01 12:01:00.000 | SUCCESS | Extracted: 2_pages_1_empty, pages: 2',
                ]
            )
        assert (Path(output_dir) / 'extract.log').exists()
        extract(
            Path('tests/fixtures/pdf'),
            output_dir,
            first_page=first_page,
            last_page=last_page,
            extractor=extractor,
        )
        result = len(sorted(Path(output_dir).glob('*.txt')))
        assert result == expected
