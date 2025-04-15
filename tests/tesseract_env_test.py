import os

import pytesseract


def test_tesseract_language_support():
    assert 'eng' in pytesseract.get_languages()
    assert set(pytesseract.get_languages()) >= {'eng', 'osd'}


def test_tesseract_version():
    assert pytesseract.get_tesseract_version().release >= (5, 0, 0)


def test_tesseract_data_path_is_set():
    tessdata_prefix = os.getenv('TESSDATA_PREFIX', '')
    assert os.path.exists(os.path.expanduser(tessdata_prefix))
