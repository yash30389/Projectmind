"""
Code Summarizer: Safe, deterministic code analysis.

Analyzes code without executing it, generating summaries and insights.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import ast
from pathlib import Path


class SummaryType(Enum):
    """Type of summary to generate."""
    BRIEF = "brief"        # One-liner
    DETAILED = "detailed"  # Full description with examples
    FUNCTIONS = "functions" # List of functions/methods
    CLASSES = "classes"    # List of classes
    DEPENDENCIES = "dependencies" # External imports
    METRICS = "metrics"    # Code metrics


@dataclass
class CodeElement:
    """Represents a code element (function, class, etc.)."""
    name: str
    type: str  # "function", "class", "method", "module"
    description: str
    lines: int
    complexity: int = 1  # Cyclomatic complexity estimate
    parameters: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    docstring: Optional[str] = None


@dataclass
class CodeMetrics:
    """Metrics about a code file."""
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    functions: int
    classes: int
    imports: int
    cyclomatic_complexity: int
    maintainability_index: float  # 0-100


@dataclass
class CodeSummary:
    """Summary of code analysis."""
    file_path: str
    summary_type: SummaryType
    brief: str
    detailed: str
    elements: List[CodeElement]
    metrics: Optional[CodeMetrics]
    dependencies: List[str]
    warnings: List[str]
    recommendations: List[str]


class CodeSummarizer:
    """Analyzes code and generates summaries without executing."""

    def __init__(self, project_root: Optional[str] = None):
        """Initialize summarizer."""
        self.project_root = project_root or "."

    def summarize_file(
        self,
        file_path: str,
        summary_type: SummaryType = SummaryType.DETAILED
    ) -> CodeSummary:
        """Summarize a Python file."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, encoding="utf-8") as f:
            content = f.read()

        return self.summarize_code(content, file_path, summary_type)

    def summarize_code(
        self,
        code: str,
        file_path: str = "unknown.py",
        summary_type: SummaryType = SummaryType.DETAILED
    ) -> CodeSummary:
        """Summarize Python code."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return CodeSummary(
                file_path=file_path,
                summary_type=summary_type,
                brief=f"Syntax error in {file_path}",
                detailed=f"Failed to parse: {e}",
                elements=[],
                metrics=None,
                dependencies=[],
                warnings=[f"Syntax error: {e}"],
                recommendations=["Fix syntax errors before analysis"],
            )

        # Extract elements
        elements = self._extract_elements(tree)

        # Extract metrics
        metrics = self._calculate_metrics(code, tree)

        # Extract dependencies
        dependencies = self._extract_dependencies(tree)

        # Generate summaries
        brief = self._generate_brief(elements, metrics)
        detailed = self._generate_detailed(elements, metrics, dependencies)

        # Find issues
        warnings = self._find_issues(code, tree, elements)
        recommendations = self._find_recommendations(elements, metrics)

        return CodeSummary(
            file_path=file_path,
            summary_type=summary_type,
            brief=brief,
            detailed=detailed,
            elements=elements,
            metrics=metrics,
            dependencies=dependencies,
            warnings=warnings,
            recommendations=recommendations,
        )

    def _extract_elements(self, tree: ast.AST) -> List[CodeElement]:
        """Extract functions and classes from AST."""
        elements: List[CodeElement] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node) or ""
                params = [arg.arg for arg in node.args.args]
                complexity = self._estimate_complexity(node)

                elements.append(
                    CodeElement(
                        name=node.name,
                        type="function",
                        description=docstring.split("\n")[0] if docstring else "",
                        lines=node.end_lineno - node.lineno + 1 if node.end_lineno else 1,
                        complexity=complexity,
                        parameters=params,
                        docstring=docstring,
                    )
                )

            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node) or ""
                methods = [
                    m.name for m in node.body
                    if isinstance(m, ast.FunctionDef)
                ]

                elements.append(
                    CodeElement(
                        name=node.name,
                        type="class",
                        description=docstring.split("\n")[0] if docstring else "",
                        lines=node.end_lineno - node.lineno + 1 if node.end_lineno else 1,
                        parameters=methods,
                        docstring=docstring,
                    )
                )

        return elements

    def _calculate_metrics(self, code: str, tree: ast.AST) -> CodeMetrics:
        """Calculate code metrics."""
        lines = code.split("\n")
        total_lines = len(lines)

        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        blank_lines = sum(1 for line in lines if not line.strip())
        code_lines = total_lines - comment_lines - blank_lines

        functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        imports = sum(
            1 for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        )

        cyclomatic_complexity = self._calculate_cyclomatic_complexity(tree)
        maintainability_index = self._calculate_maintainability(
            code_lines, cyclomatic_complexity, comment_lines
        )

        return CodeMetrics(
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            imports=imports,
            cyclomatic_complexity=cyclomatic_complexity,
            maintainability_index=maintainability_index,
        )

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _calculate_maintainability(
        self,
        code_lines: int,
        complexity: int,
        comment_lines: int
    ) -> float:
        """Calculate maintainability index (0-100)."""
        if code_lines == 0:
            return 100.0

        comment_ratio = (comment_lines / code_lines) * 100 if code_lines > 0 else 0
        volume = code_lines * 0.5  # Simplified
        index = 171 - (5.2 * (volume ** 0.4)) - (0.23 * complexity) + (50 * (comment_ratio ** 0.1))

        return max(0, min(100, index))

    def _estimate_complexity(self, func_node: ast.FunctionDef) -> int:
        """Estimate function complexity."""
        complexity = 1

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1

        return complexity

    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract external imports."""
        dependencies = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split(".")[0])

        return sorted(list(dependencies))

    def _generate_brief(
        self,
        elements: List[CodeElement],
        metrics: CodeMetrics
    ) -> str:
        """Generate brief summary."""
        return f"Python module with {metrics.functions} functions and {metrics.classes} classes ({metrics.code_lines} lines of code)"

    def _generate_detailed(
        self,
        elements: List[CodeElement],
        metrics: CodeMetrics,
        dependencies: List[str]
    ) -> str:
        """Generate detailed summary."""
        lines = [
            f"**Code Summary**",
            f"- Total Lines: {metrics.total_lines}",
            f"- Code Lines: {metrics.code_lines}",
            f"- Functions: {metrics.functions}",
            f"- Classes: {metrics.classes}",
            f"- Cyclomatic Complexity: {metrics.cyclomatic_complexity}",
            f"- Maintainability: {metrics.maintainability_index:.0f}/100",
        ]

        if dependencies:
            lines.append(f"\n**Dependencies**")
            for dep in dependencies[:10]:  # Top 10
                lines.append(f"- {dep}")

        if elements:
            lines.append(f"\n**Key Elements**")
            for elem in elements[:5]:  # Top 5
                lines.append(f"- {elem.name} ({elem.type}): {elem.description or 'No description'}")

        return "\n".join(lines)

    def _find_issues(self, code: str, tree: ast.AST, elements: List[CodeElement]) -> List[str]:
        """Find potential issues."""
        issues = []

        # Check for missing docstrings
        undocumented = [e for e in elements if not e.docstring]
        if len(undocumented) > 0:
            issues.append(f"{len(undocumented)} functions/classes without docstrings")

        # Check for complexity
        high_complexity = [e for e in elements if e.complexity > 5]
        if high_complexity:
            issues.append(f"{len(high_complexity)} elements with high complexity")

        # Check for long functions
        long_functions = [e for e in elements if e.type == "function" and e.lines > 50]
        if long_functions:
            issues.append(f"{len(long_functions)} functions exceed 50 lines")

        return issues

    def _find_recommendations(
        self,
        elements: List[CodeElement],
        metrics: CodeMetrics
    ) -> List[str]:
        """Find recommendations."""
        recommendations = []

        if metrics.maintainability_index < 70:
            recommendations.append("Consider refactoring - maintainability is below 70")

        if metrics.cyclomatic_complexity > 10:
            recommendations.append("Reduce cyclomatic complexity with smaller functions")

        undocumented = sum(1 for e in elements if not e.docstring)
        if undocumented > len(elements) * 0.5:
            recommendations.append("Add docstrings to improve code documentation")

        return recommendations
