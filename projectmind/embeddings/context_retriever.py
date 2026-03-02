"""
Context Retriever: Retrieve relevant code context for queries.

Manages context windows and sliding window retrieval.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ContextWindow:
    """A window of code context."""
    file_path: str
    start_line: int
    end_line: int
    content: str
    relevance_score: float
    element_name: Optional[str] = None


class ContextRetriever:
    """Retrieve code context from files."""

    def __init__(self, project_root: Optional[str] = None):
        """Initialize context retriever."""
        self.project_root = project_root or "."

    def get_context_window(
        self,
        file_path: str,
        start_line: int,
        window_size: int = 20,
    ) -> Optional[ContextWindow]:
        """Get context window around line."""
        file_path_obj = Path(self.project_root) / file_path

        if not file_path_obj.exists():
            return None

        with open(file_path_obj) as f:
            lines = f.readlines()

        # Calculate window bounds
        total_lines = len(lines)
        window_start = max(0, start_line - window_size // 2)
        window_end = min(total_lines, start_line + window_size // 2)

        # Extract context
        context_lines = lines[window_start:window_end]
        content = "".join(context_lines)

        return ContextWindow(
            file_path=file_path,
            start_line=window_start,
            end_line=window_end,
            content=content,
            relevance_score=1.0,
            element_name=None,
        )

    def get_surrounding_context(
        self,
        file_path: str,
        target_line: int,
        context_lines_before: int = 10,
        context_lines_after: int = 10,
    ) -> Optional[ContextWindow]:
        """Get surrounding context (before and after target line)."""
        file_path_obj = Path(self.project_root) / file_path

        if not file_path_obj.exists():
            return None

        with open(file_path_obj) as f:
            lines = f.readlines()

        # Adjust for 0-based indexing
        target_idx = target_line - 1

        # Calculate bounds
        start_idx = max(0, target_idx - context_lines_before)
        end_idx = min(len(lines), target_idx + context_lines_after + 1)

        # Extract context
        context_lines = lines[start_idx:end_idx]
        content = "".join(context_lines)

        return ContextWindow(
            file_path=file_path,
            start_line=start_idx + 1,
            end_line=end_idx,
            content=content,
            relevance_score=1.0,
        )

    def get_function_context(
        self,
        file_path: str,
        function_name: str,
    ) -> Optional[ContextWindow]:
        """Get context for a specific function."""
        file_path_obj = Path(self.project_root) / file_path

        if not file_path_obj.exists():
            return None

        with open(file_path_obj) as f:
            lines = f.readlines()

        # Find function definition
        func_pattern = f"def {function_name}("
        start_line = None

        for i, line in enumerate(lines):
            if func_pattern in line:
                start_line = i
                break

        if start_line is None:
            return None

        # Find end of function (next def or class at same indentation)
        indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = start_line + 1

        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Skip blank lines and more indented lines
            if not line.strip():
                continue

            current_indent = len(line) - len(line.lstrip())

            # If we hit something at same/lower indent level, we're done
            if current_indent <= indent_level and line.strip():
                end_line = i
                break

            end_line = i + 1

        # Extract context
        context_lines = lines[start_line:end_line]
        content = "".join(context_lines)

        return ContextWindow(
            file_path=file_path,
            start_line=start_line + 1,
            end_line=end_line,
            content=content,
            relevance_score=1.0,
            element_name=function_name,
        )

    def merge_contexts(
        self,
        contexts: List[ContextWindow],
    ) -> str:
        """Merge multiple context windows into single string."""
        if not contexts:
            return ""

        # Sort by file and line number
        sorted_contexts = sorted(
            contexts,
            key=lambda c: (c.file_path, c.start_line),
        )

        merged = []

        for ctx in sorted_contexts:
            header = f"\n# File: {ctx.file_path} (lines {ctx.start_line}-{ctx.end_line})\n"
            merged.append(header)
            merged.append(ctx.content)

        return "".join(merged)

    def estimate_tokens(self, context: ContextWindow) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: 4 characters per token
        return len(context.content) // 4
