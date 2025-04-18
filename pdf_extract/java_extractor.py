# pyright: reportMissingImports=false
# pylint: disable=import-error, wrong-import-position, import-outside-toplevel, consider-using-from-import
# isort: skip

import os
from dataclasses import dataclass
from pathlib import Path

import jpype
import jpype.imports
from appdirs import AppDirs
from loguru import logger
from packaging.version import Version

from pdf_extract.interface import ITextExtractor

# TODO: Use config file instead
JARFILE = '../lib/pdfextract-1.0-SNAPSHOT.jar'


def get_pdfbox_path() -> Path:
    app_dir = AppDirs('python-pdfbox')
    cache_dir = Path(app_dir.user_cache_dir)
    file_list = list(cache_dir.glob('pdfbox-app-*.jar'))
    if not file_list:
        raise RuntimeError('PDFBox not found')

    versions = [file.stem.split('-')[-1] for file in file_list]
    versions.sort(key=Version)
    latest = versions[-1]

    return Path(f'{cache_dir}/pdfbox-app-{latest}.jar')


@dataclass
class ExtractedPage:
    pdf_page_number: int
    content: str
    titles: list[tuple[str, int]]


@dataclass
class ExtractedPages:
    """Container for extracted raw text, and titles (text and position) for a single issue.

    Note:
      - Page numbers are not corrected for double-pages (represented as a single image in PDF).
    """

    pages: list[ExtractedPage]

    def __len__(self) -> int:
        return len(self.pages) or 0

    def __str__(self) -> str:
        return '\n\n'.join([str(p.content) for p in self.pages])

    def __getitem__(self, index: int) -> ExtractedPage:
        return self.pages[index]

    def get_page(self, page_number: int) -> ExtractedPage:
        # NOTE: Page numbers are 1-based
        if page_number < 1 or page_number > len(self):
            raise IndexError(f'Page number {page_number} out of range')
        return self[page_number - 1]


# TODO: Add java args as option to JavaExtractor class
class JavaExtractor(ITextExtractor):
    def __init__(self, title_font_size: float = 5.5, min_title_length: int = 8, pdfextract_jar_path: str = JARFILE):
        self.title_font_size = title_font_size
        self.min_title_length = min_title_length

        if str(pdfextract_jar_path) not in jpype.getClassPath():
            jpype.addClassPath(pdfextract_jar_path)

        if not jpype.isJVMStarted():
            jpype.addClassPath(get_pdfbox_path())
            jpype.startJVM(
                '-Dorg.apache.commons.logging.Log=org.apache.commons.logging.impl.NoOpLog', convertStrings=False
            )

        import se.umu.humlab.pdfextract as pdfextract  # isort: skip  # noqa: E402

        self.extractor = pdfextract.PDFCourier2Text(self.title_font_size, self.min_title_length)

    def extract_pages(self, filename: str | os.PathLike[str]) -> ExtractedPages:
        filename = str(filename)
        pages = []
        for pdf_page_number, content in enumerate(self.extractor.extractText(filename), start=1):
            titles = [
                [(str(y.title), int(y.position)) for y in x] for x in self.extractor.getTitles()
            ]  # pylint: disable=W0631
            page: ExtractedPage = ExtractedPage(
                pdf_page_number=pdf_page_number,
                content=content,
                titles=titles[pdf_page_number - 1],
            )
            pages.append(page)

        issue: ExtractedPages = ExtractedPages(pages=pages)
        return issue

    def pdf_to_txt(
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int = 1,
        last_page: int | None = None,
    ) -> None:
        basename = Path(filename).stem
        issue: ExtractedPages = self.extract_pages(filename)
        last_page = last_page or len(issue)

        for page in issue.pages[first_page - 1 : int(last_page)]:
            with open(
                Path(output_folder) / f'{basename}_{page.pdf_page_number:04}.txt', 'w', encoding='utf-8'
            ) as fp_out:
                fp_out.write(str(page.content) + '\n')  # NOTE: Added newline to mimic pdfextract
        logger.success(f'Extracted: {basename}, pages: {last_page - first_page + 1}')
