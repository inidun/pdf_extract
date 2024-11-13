import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

# TODO: No pdf2image, get page numbers from Java
import pdf2image
import pdfbox
from loguru import logger
from tqdm import tqdm

from pdf_extract.interface import ITextExtractor


@dataclass
class PDFBoxExtractor(ITextExtractor):
    p: pdfbox.PDFBox = pdfbox.PDFBox()
    encoding: str = 'utf-8'
    html: bool = False
    sort: bool = False
    ignore_beads: bool = False
    console: bool = False

    def pdf_to_txt(
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int = 1,
        last_page: int | None = None,
    ) -> None:
        basename = Path(filename).stem
        # TODO Remove num_pages
        num_pages: int = pdf2image.pdfinfo_from_path(str(filename))['Pages']
        last_page = min(last_page or num_pages, num_pages)

        # TODO
        # for page in p.get_pages('filename'): -> sorted list of strings (or list of strings + titles, or markup)
        for page in range(first_page, last_page + 1):
            output_filename = Path(output_folder) / f'{basename}_{page:04}.txt'
            self.p.extract_text(
                filename,
                output_path=output_filename,
                encoding=self.encoding,
                html=self.html,
                sort=self.sort,
                ignore_beads=self.ignore_beads,
                start_page=page,
                end_page=page,
                console=self.console,
            )
        # FIXME: Report correct number of pages. Should be `last_page - first_page + 1`
        logger.success(f'Extracted: {basename}, pages: {num_pages}')

    def batch_extract(
        self,
        files: list[Path],
        output_folder: str | os.PathLike[str],
        *,
        first_page: int = 1,
        last_page: int | None = None,
    ) -> None:
        logfile = Path(output_folder) / 'extract.log'
        if logfile.exists():
            files = self._skip_completed(files, logfile)
        if len(files) == 0:
            return
        file_logger = self._add_logger(logfile)

        total_files = len(files)
        for i, filename in enumerate(files, start=1):
            print(f'Processing {filename.stem}\t{i:03}/{total_files}', end='\r')
            self.pdf_to_txt(filename, output_folder, first_page, last_page)

        self._remove_logger(file_logger)

    # TODO: Optimize
    def extract_text(
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int | None = 1,
        last_page: int | None = None,
        # page_sep: str = '',
        page_numbers: bool = False,
    ) -> None:
        first_page: int = first_page or 1
        basename = Path(filename).stem
        p = pdfbox.PDFBox()

        num_pages = pdf2image.pdfinfo_from_path(str(filename))['Pages']
        if last_page is None or last_page > num_pages:
            last_page = int(num_pages)

        ouput_filename: str = (
            f'{basename}_{first_page}-{last_page}.txt' if last_page < num_pages or first_page > 1 else f'{basename}.txt'
        )

        output_filepath: Path = Path(output_folder) / ouput_filename

        if output_filepath.exists():
            logger.info(f'Skipping {basename}: Already extracted')
            return

        logger.info(f'Processing {basename}, pages: {first_page}-{last_page}')

        with TemporaryDirectory() as temp_dir:
            for page in tqdm(range(first_page, last_page + 1), desc='Extracting pages'):
                output_filename = Path(temp_dir) / f'{basename}_{page:04}.txt'
                p.extract_text(
                    filename,
                    output_path=output_filename,
                    encoding=self.encoding,
                    html=self.html,
                    sort=self.sort,
                    ignore_beads=self.ignore_beads,
                    start_page=page,
                    end_page=page,
                    console=self.console,
                )

            with open(Path(output_folder) / ouput_filename, 'w', encoding='utf-8') as outfile:
                if page_numbers:
                    outfile.write(f'# {basename}\n\n')

                for file in sorted(Path(temp_dir).glob('*.txt')):
                    with open(file, 'r', encoding='utf-8') as infile:
                        if page_numbers:
                            page_number: int = int(file.stem.rsplit('_', 1)[-1])
                            outfile.write(f'\n## Page {page_number}\n\n')

                        contents = infile.read()
                        outfile.write(contents)

        logger.success(f'Extracted: {basename}, pages: {first_page}-{last_page}')


if __name__ == '__main__':
    pass
