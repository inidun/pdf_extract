import abc
import os
import sys
from pathlib import Path

from loguru import logger
from tqdm import tqdm


class ITextExtractor(abc.ABC):
    @abc.abstractmethod
    def pdf_to_txt(
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int = 1,
        last_page: int | None = None,
    ) -> None:
        """Extracts text from PDF-file and saves result as text files (one file per page).

        Args:
            filename (str | os.PathLike[str]): Input filename (PDF-file)
            output_folder (str | os.PathLike[str]): Output folder
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (int, optional): Last page to extract. Defaults to None.
        """

    def batch_extract(
        self,
        files: list[Path],
        output_folder: str | os.PathLike[str],
        *,
        first_page: int = 1,
        last_page: int | None = None,
    ) -> None:
        """Extracts text from multiple PDF-files and saves result as text files (one file per page).

        Args:
            files (list[Path]): List of PDF-files to process
            output_folder (str | os.PathLike[str]): Output folder
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (int , optional): Last page to extract. Defaults to None.
        """
        logfile = Path(output_folder) / 'extract.log'
        if logfile.exists():
            files = self._skip_completed(files, logfile)
        if len(files) == 0:
            return
        file_logger = self._add_logger(logfile)

        logger.patch(lambda msg: tqdm.write(msg, end=''))
        pbar = tqdm(files, desc='File')
        for filename in pbar:
            pbar.set_description(f'Processing {filename.stem}')
            self.pdf_to_txt(filename, output_folder, first_page, last_page)

        self._remove_logger(file_logger)

    def _add_logger(self, logfile: str | os.PathLike[str]) -> int:
        logger.configure(handlers=[{'sink': sys.stderr, 'level': 'WARNING'}])
        file_logger = logger.add(
            Path(logfile),
            format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}',
        )
        return file_logger

    def _remove_logger(self, file_logger: int) -> None:
        logger.remove(file_logger)
        logger.configure(handlers=[{'sink': sys.stderr, 'level': 'INFO'}])

    def _skip_completed(self, files: list[Path], logfile: str | os.PathLike[str]) -> list[Path]:
        expr = r'(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) \| (?P<lvl>[A-Z]+) \| (?P<msg>\w+: (?P<id>\w+).*)'
        completed = {line['id'] for line in logger.parse(logfile, expr) if line['lvl'] == 'SUCCESS'}
        logger.info(f'Skipping {len(completed)} files: {completed}')
        files = [file for file in files if all(c not in str(file) for c in completed)]
        return files


if __name__ == '__main__':
    pass
