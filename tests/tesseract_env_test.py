import pytesseract


def test_tesseract_language_support():
    assert 'eng' in pytesseract.get_languages()
    assert set(pytesseract.get_languages()) >= {'eng', 'osd'}


def test_tesseract_version():
    assert pytesseract.get_tesseract_version().release >= (5, 5, 0)
    assert pytesseract.get_tesseract_version().public == '5.5.0'
