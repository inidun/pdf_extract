from pathlib import Path


def test_pdfextract_jar_exists():
    jar_path = Path('lib/pdfextract-1.0-SNAPSHOT.jar')
    assert jar_path.exists(), f'JAR file does not exist: {jar_path}'
    assert jar_path.is_file(), f'Path is not a file: {jar_path}'
    assert jar_path.stat().st_size > 0, f'JAR file is empty: {jar_path}'
