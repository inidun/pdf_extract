import pytesseract

from pdf_extract import __version__


def test_version():
    assert __version__ == '0.1.0'


def test_tesseract_installation():
    assert set(pytesseract.get_languages()) >= {'eng', 'osd'}
    assert pytesseract.get_tesseract_version().release >= (5, 3, 0)
    assert pytesseract.get_tesseract_version().public == '5.3.1'
