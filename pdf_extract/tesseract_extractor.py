import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union

import pdf2image
import pytesseract
from loguru import logger
from pdf2image import convert_from_path

from pdf_extract.interface import ITextExtractor


# TODO: Add language as argument
@dataclass
class TesseractExtractor(ITextExtractor):
    dpi: int = 350
    fmt: str = 'tiff'
    grayscale: bool = True
    use_pdftocairo: bool = True

    # TODO: Add to config
    tessdata: str = str(Path.home() / 'data/tessdata_best')
    tesseract_config: str = f'--oem 1 --psm 1 --tessdata-dir {tessdata}'

    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike[str]],
        output_folder: Union[str, os.PathLike[str]],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        basename = Path(filename).stem
        images = convert_from_path(
            str(filename),
            first_page=first_page,
            last_page=last_page,  # type: ignore
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        i = 0
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.txt'
            with open(text_filename, 'w', encoding='utf-8') as fp:
                fp.write(pytesseract.image_to_string(image, lang='eng', config=self.tesseract_config))

        logger.success(f'Extracted: {basename}, pages: {i+1}, dpi: {self.dpi}, fmt: {self.fmt}')

    def pdf_to_alto(
        self,
        filename: Union[str, os.PathLike[str]],
        output_folder: Union[str, os.PathLike[str]],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        """Extracts text from PDF-file and saves result as ALTO-XML

        Args:
            filename (Union[str, os.PathLike[str]]): Input filename (PDF-file)
            output_folder (Union[str, os.PathLike[str]]): Output folder
            first_page (int, optional): First page. Defaults to 1.
            last_page (Optional[int], optional): Last page. Defaults to None.
        """
        basename = Path(filename).stem
        images = convert_from_path(
            str(filename),
            first_page=first_page,
            last_page=last_page,  # type: ignore
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        i = 0
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.alto'
            with open(text_filename, 'wb') as fp:
                fp.write(pytesseract.image_to_alto_xml(image, lang='eng', config=self.tesseract_config))

        logger.success(f'Extracted: {basename}, pages: {i+1}, dpi: {self.dpi}, fmt: {self.fmt}')

    def pdf_to_hocr(
        self,
        filename: Union[str, os.PathLike[str]],
        output_folder: Union[str, os.PathLike[str]],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        """Extracts text from PDF-file and saves result as hOCR

        Args:
            filename (Union[str, os.PathLike[str]]): Input filename (PDF-file)
            output_folder (Union[str, os.PathLike[str]]): Output folder
            first_page (int, optional): First page. Defaults to 1.
            last_page (Optional[int], optional): Last page. Defaults to None.
        """
        basename = Path(filename).stem
        images = convert_from_path(
            str(filename),
            first_page=first_page,
            last_page=last_page,  # type: ignore
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        i = 0
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.hocr'
            with open(text_filename, 'wb') as fp:
                hocr = pytesseract.image_to_pdf_or_hocr(
                    image, extension='hocr', lang='eng', config=self.tesseract_config
                )
                fp.write(hocr)

        logger.success(f'Extracted: {basename}, pages: {i+1}, dpi: {self.dpi}, fmt: {self.fmt}')

    def extract_text(
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int | None = 1,
        last_page: int | None = None,
        page_numbers: bool = False,
    ) -> None:
        first_page: int = first_page or 1
        basename = Path(filename).stem

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

        images = convert_from_path(
            str(filename),
            first_page=first_page,
            last_page=last_page,
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        with TemporaryDirectory() as temp_dir:
            for i, image in enumerate(images):
                text_filename = Path(temp_dir) / f'{basename}_{i+first_page:04}.txt'
                with open(text_filename, 'w', encoding='utf-8') as fp:
                    fp.write(pytesseract.image_to_string(image, lang='eng', config=self.tesseract_config))

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

        logger.success(f'Extracted: {basename}, pages: {first_page}-{last_page}, dpi: {self.dpi}, fmt: {self.fmt}')


if __name__ == '__main__':
    pass
