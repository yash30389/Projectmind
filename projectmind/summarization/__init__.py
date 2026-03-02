"""
Phase 2: AI Summarization

Safe, deterministic code analysis and documentation generation.
No autonomous actions - only analysis and suggestions.
"""

from .code_summarizer import CodeSummarizer, SummaryType
from .documentation_generator import DocumentationGenerator

__all__ = [
    "CodeSummarizer",
    "SummaryType",
    "DocumentationGenerator",
]
