"""
Layer A: Repository Intelligence Layer

This is the ground truth layer that walks the entire directory tree,
detects languages, and extracts metadata without any guessing.

No AI here - pure deterministic scanning.
"""

__all__ = ["RepoScanner", "FileMetadata", "PythonParser"]
