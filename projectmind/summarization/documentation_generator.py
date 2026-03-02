"""
Documentation Generator: Create API documentation from code analysis.

Generates markdown documentation from code summaries.
"""

from typing import List, Dict, Optional
from pathlib import Path
from .code_summarizer import CodeSummary, CodeElement


class DocumentationGenerator:
    """Generate documentation from code analysis."""

    @staticmethod
    def generate_markdown(summary: CodeSummary) -> str:
        """Generate Markdown documentation."""
        sections = [
            f"# {Path(summary.file_path).name}",
            "",
            f"**File**: `{summary.file_path}`",
            "",
        ]

        # Overview
        sections.extend([
            "## Overview",
            summary.brief,
            "",
        ])

        # Metrics
        if summary.metrics:
            sections.extend(DocumentationGenerator._metrics_section(summary.metrics))

        # Dependencies
        if summary.dependencies:
            sections.extend(DocumentationGenerator._dependencies_section(summary.dependencies))

        # Functions and Classes
        if summary.elements:
            sections.extend(DocumentationGenerator._elements_section(summary.elements))

        # Issues
        if summary.warnings:
            sections.extend(DocumentationGenerator._warnings_section(summary.warnings))

        # Recommendations
        if summary.recommendations:
            sections.extend(DocumentationGenerator._recommendations_section(summary.recommendations))

        return "\n".join(sections)

    @staticmethod
    def _metrics_section(metrics) -> List[str]:
        """Generate metrics section."""
        return [
            "## Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Lines | {metrics.total_lines} |",
            f"| Code Lines | {metrics.code_lines} |",
            f"| Comment Lines | {metrics.comment_lines} |",
            f"| Blank Lines | {metrics.blank_lines} |",
            f"| Functions | {metrics.functions} |",
            f"| Classes | {metrics.classes} |",
            f"| Imports | {metrics.imports} |",
            f"| Cyclomatic Complexity | {metrics.cyclomatic_complexity} |",
            f"| Maintainability Index | {metrics.maintainability_index:.0f}/100 |",
            "",
        ]

    @staticmethod
    def _dependencies_section(dependencies: List[str]) -> List[str]:
        """Generate dependencies section."""
        lines = ["## Dependencies", ""]

        for dep in dependencies:
            lines.append(f"- `{dep}`")

        lines.append("")
        return lines

    @staticmethod
    def _elements_section(elements: List[CodeElement]) -> List[str]:
        """Generate elements section."""
        lines = ["## Elements", ""]

        functions = [e for e in elements if e.type == "function"]
        classes = [e for e in elements if e.type == "class"]

        if functions:
            lines.extend(["### Functions", ""])
            for func in functions:
                lines.append(f"#### `{func.name}`")
                if func.docstring:
                    lines.append(f"\n{func.docstring}\n")
                else:
                    lines.append("*No documentation*\n")

                if func.parameters:
                    lines.append(f"**Parameters**: {', '.join(func.parameters)}")

                lines.append(f"**Complexity**: {func.complexity}")
                lines.append(f"**Lines**: {func.lines}")
                lines.append("")

        if classes:
            lines.extend(["### Classes", ""])
            for cls in classes:
                lines.append(f"#### `{cls.name}`")
                if cls.docstring:
                    lines.append(f"\n{cls.docstring}\n")
                else:
                    lines.append("*No documentation*\n")

                if cls.parameters:
                    lines.append(f"**Methods**: {', '.join(cls.parameters)}")

                lines.append(f"**Lines**: {cls.lines}")
                lines.append("")

        return lines

    @staticmethod
    def _warnings_section(warnings: List[str]) -> List[str]:
        """Generate warnings section."""
        lines = ["## Issues", ""]

        for warning in warnings:
            lines.append(f"⚠️ {warning}")

        lines.append("")
        return lines

    @staticmethod
    def _recommendations_section(recommendations: List[str]) -> List[str]:
        """Generate recommendations section."""
        lines = ["## Recommendations", ""]

        for rec in recommendations:
            lines.append(f"💡 {rec}")

        lines.append("")
        return lines

    @staticmethod
    def save_documentation(
        summary: CodeSummary,
        output_path: str
    ) -> None:
        """Save documentation to file."""
        markdown = DocumentationGenerator.generate_markdown(summary)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)

    @staticmethod
    def generate_api_reference(summaries: List[CodeSummary]) -> str:
        """Generate API reference from multiple summaries."""
        sections = [
            "# API Reference",
            "",
        ]

        for summary in summaries:
            sections.append(f"## {Path(summary.file_path).stem}")
            sections.append(f"**File**: `{summary.file_path}`")
            sections.append("")

            if summary.elements:
                sections.append("### Public Interface")
                sections.append("")

                for elem in summary.elements:
                    if not elem.name.startswith("_"):  # Public only
                        sections.append(f"- `{elem.name}` ({elem.type})")
                        if elem.description:
                            sections.append(f"  - {elem.description}")

                sections.append("")

        return "\n".join(sections)
