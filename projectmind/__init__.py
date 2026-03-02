"""
ProjectMind: Local, project-aware AI engineering system.

Four-layer architecture:
  1. Repository Intelligence: Deterministic repo scanning
  2. Context & Memory: Project vision, goals, constraints
  3. CLI Interface: Explicit, auditable developer tool
  4. Architecture Discipline: Governance and documentation

Features:
  - Full codebase understanding without hallucination
  - AI agents with role-based responsibilities
  - Human-in-the-loop decision making
  - Compliance and security guardrails
"""

__version__ = "0.1.0"
__author__ = "ProjectMind Team"

from projectmind.core.scanner import RepoScanner, FileMetadata
from projectmind.core.python_parser import PythonParser, PythonFileAnalysis
from projectmind.core.context import ContextLoader, ProjectContext

__all__ = [
    "RepoScanner",
    "FileMetadata",
    "PythonParser",
    "PythonFileAnalysis",
    "ContextLoader",
    "ProjectContext",
]
