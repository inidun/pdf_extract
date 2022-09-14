import pytesseract


def test_pytesseract_env():
    assert 'eng' in pytesseract.get_languages()
    assert pytesseract.get_tesseract_version().release >= (5, 0, 0)
