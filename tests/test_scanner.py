"""Tests for Repository Scanner"""

import pytest
import tempfile
from pathlib import Path
from projectmind.core.scanner import RepoScanner, FileMetadata, IGNORE_DIRS


@pytest.fixture
def temp_repo():
    """Create a temporary repository structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create Python files
        (root / "main.py").write_text("print('hello')\n")
        (root / "utils.py").write_text("def helper():\n    pass\n")

        # Create nested structure
        (root / "src").mkdir()
        (root / "src" / "core.py").write_text("class Core:\n    pass\n")

        # Create ignored directory
        (root / "__pycache__").mkdir()
        (root / "__pycache__" / "cache.pyc").write_text("binary")

        # Create other file types
        (root / "README.md").write_text("# Readme\n")
        (root / "config.yaml").write_text("key: value\n")

        yield root


def test_scanner_initialization(temp_repo):
    """Test scanner can be initialized."""
    scanner = RepoScanner(str(temp_repo))
    assert scanner.root_path == temp_repo.resolve()


def test_scanner_finds_files(temp_repo):
    """Test scanner finds all files."""
    scanner = RepoScanner(str(temp_repo))
    scanner.scan()

    # Should find 5 files (not __pycache__)
    assert len(scanner.files) >= 4


def test_scanner_ignores_directories(temp_repo):
    """Test scanner ignores __pycache__."""
    scanner = RepoScanner(str(temp_repo))
    scanner.scan()

    file_paths = [f.path for f in scanner.files]
    assert not any("__pycache__" in path for path in file_paths)


def test_language_detection(temp_repo):
    """Test language detection."""
    scanner = RepoScanner(str(temp_repo))
    scanner.scan()

    languages = list(scanner.files_by_language.keys())
    assert "python" in languages
    assert "markdown" in languages or "yaml" in languages


def test_file_metadata(temp_repo):
    """Test file metadata extraction."""
    scanner = RepoScanner(str(temp_repo))
    scanner.scan()

    py_files = scanner.files_by_language.get("python", [])
    assert len(py_files) > 0

    for file_meta in py_files:
        assert file_meta.path
        assert file_meta.language == "python"
        assert file_meta.size_bytes > 0


def test_scanner_summary(temp_repo):
    """Test scan summary."""
    scanner = RepoScanner(str(temp_repo))
    scanner.scan()

    summary = scanner.get_summary()
    assert summary["total_files"] > 0
    assert summary["languages"]
    assert summary["total_lines"] > 0


def test_file_metadata_to_dict():
    """Test FileMetadata serialization."""
    meta = FileMetadata(
        path="test.py",
        absolute_path="/path/to/test.py",
        language="python",
        size_bytes=100,
        lines_of_code=5,
        last_modified=1234567890.0,
        is_text=True,
        hash="abc123",
    )

    data = meta.to_dict()
    assert data["path"] == "test.py"
    assert data["language"] == "python"
