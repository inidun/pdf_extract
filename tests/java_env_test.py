import os
import subprocess
from pathlib import Path


def test_java_is_available():
    result = subprocess.run(['java', '-version'], stderr=subprocess.PIPE, text=True, check=True)
    assert result.returncode == 0, 'Java is not available'
    version_line = result.stderr.splitlines()[0]
    version = version_line.split('"')[1]
    assert version, 'Java version not found'


def test_java_home_is_set():
    assert 'JAVA_HOME' in os.environ, 'JAVA_HOME is not set'


def test_pdfextract_jar_exists():
    jar_path = Path('lib/pdfextract-1.0-SNAPSHOT.jar')
    assert jar_path.exists(), f'JAR file does not exist: {jar_path}'
    assert jar_path.is_file(), f'Path is not a file: {jar_path}'
    assert jar_path.stat().st_size > 0, f'JAR file is empty: {jar_path}'
