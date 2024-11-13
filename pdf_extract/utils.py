import os
from pathlib import Path


def get_filenames(files: str | os.PathLike[str], extension: str = 'pdf') -> list[Path]:
    items = []
    path = Path(files)
    if path.is_dir():
        items = list(path.glob(f'*.{extension}'))
    elif path.is_file() and path.suffix == f'.{extension}':
        items.append(path)
    return sorted(items)


if __name__ == '__main__':
    pass
