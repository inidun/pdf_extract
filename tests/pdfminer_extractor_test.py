# pylint: disable=consider-using-with

from difflib import SequenceMatcher
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from pdf_extract.interface import ITextExtractor
from pdf_extract.pdfminer_extractor import PDFMinerExtractor
from pdf_extract.utils import get_filenames

test_dir = Path('tests/fixtures/')


def test_extract_generates_expected_output():
    with TemporaryDirectory() as output_dir:
        files: List[Path] = get_filenames(test_dir / 'test.pdf')
        extractor: ITextExtractor = PDFMinerExtractor()
        extractor.batch_extract(files, output_dir)

        num_extracted = len(sorted(Path(output_dir).glob('*.txt')))
        assert num_extracted == 8

        # FIXME: Improve
        for i in range(0, num_extracted):
            text1 = open(sorted(Path(output_dir).glob('*.txt'))[i], encoding='utf-8').read()
            text2 = open(sorted(Path(test_dir / 'expected/pdfminer').iterdir())[i], encoding='utf-8').read()
            m = SequenceMatcher(None, text1, text2)
            assert m.quick_ratio() > 0.99
