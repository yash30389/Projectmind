"""
Repository scanning without guessing.
Deterministic, complete, trustworthy.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict
import json


IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".egg-info",
    ".tox",
    ".coverage",
    "htmlcov",
    ".mypy_cache",
    ".ruff_cache",
    "target",
    ".gradle",
    "bin",
    "obj",
}

IGNORE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    ".gitignore",
    ".gitkeep",
    ".env.local",
    ".env.*.local",
}

LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".java": "java",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sh": "bash",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".xml": "xml",
    ".sql": "sql",
    ".md": "markdown",
}


@dataclass
class FileMetadata:
    """Metadata about a single file."""

    path: str  # Relative path from repo root
    absolute_path: str
    language: Optional[str]  # Language detected from extension
    size_bytes: int
    lines_of_code: int
    last_modified: float
    is_text: bool
    hash: str = ""  # SHA256 hash

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @staticmethod
    def compute_hash(file_path: str) -> str:
        """Compute SHA256 hash of file."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            return "unknown"


class RepoScanner:
    """
    Scans repository without guessing.
    
    Returns:
    - All files with metadata
    - Files grouped by language
    - Directory structure
    - Import graph (to be filled by language-specific parsers)
    """

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        if not self.root_path.exists():
            raise ValueError(f"Repository path does not exist: {root_path}")

        self.files: List[FileMetadata] = []
        self.files_by_language: Dict[str, List[FileMetadata]] = {}
        self.directory_tree: Dict = {}

    def scan(self, verbose: bool = False) -> "RepoScanner":
        """
        Scan the repository.
        Returns self for chaining.
        """
        self.files = []
        self.files_by_language = {}

        for root, dirs, file_names in os.walk(self.root_path):
            # Remove ignored directories in-place to prevent descending
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file_name in file_names:
                if file_name in IGNORE_FILES:
                    continue

                file_path = Path(root) / file_name
                try:
                    metadata = self._extract_metadata(file_path)
                    self.files.append(metadata)

                    if metadata.language:
                        if metadata.language not in self.files_by_language:
                            self.files_by_language[metadata.language] = []
                        self.files_by_language[metadata.language].append(metadata)

                    if verbose:
                        print(f"Scanned: {metadata.path}")
                except Exception as e:
                    if verbose:
                        print(f"Failed to scan {file_path}: {e}")

        return self

    def _extract_metadata(self, file_path: Path) -> FileMetadata:
        """Extract metadata from a single file."""
        relative_path = file_path.relative_to(self.root_path).as_posix()
        stat = file_path.stat()

        # Detect language
        suffix = file_path.suffix.lower()
        language = LANGUAGE_EXTENSIONS.get(suffix)

        # Check if text file
        is_text = self._is_text_file(file_path)

        # Count lines (if text)
        lines = 0
        if is_text:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = sum(1 for _ in f)
            except Exception:
                lines = 0

        # Compute hash
        file_hash = FileMetadata.compute_hash(str(file_path))

        return FileMetadata(
            path=relative_path,
            absolute_path=str(file_path),
            language=language,
            size_bytes=stat.st_size,
            lines_of_code=lines,
            last_modified=stat.st_mtime,
            is_text=is_text,
            hash=file_hash,
        )

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is text (heuristic)."""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(512)
                return not self._contains_null_byte(chunk)
        except Exception:
            return False

    @staticmethod
    def _contains_null_byte(chunk: bytes) -> bool:
        """Check if chunk contains null bytes."""
        return b"\x00" in chunk

    def get_summary(self) -> Dict:
        """Get scan summary."""
        total_lines = sum(f.lines_of_code for f in self.files)
        total_size = sum(f.size_bytes for f in self.files)

        return {
            "root": str(self.root_path),
            "total_files": len(self.files),
            "total_lines": total_lines,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "languages": {
                lang: len(files) for lang, files in self.files_by_language.items()
            },
        }

    def to_json(self) -> str:
        """Export scan results as JSON."""
        return json.dumps(
            {
                "summary": self.get_summary(),
                "files": [f.to_dict() for f in self.files],
                "by_language": {
                    lang: [f.to_dict() for f in files]
                    for lang, files in self.files_by_language.items()
                },
            },
            indent=2,
            default=str,
        )
