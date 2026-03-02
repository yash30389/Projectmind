"""
Code Analyzer Agent.

Specialized agent for code analysis and metrics.
"""

from typing import Any, Dict
from .base_agent import Agent, AgentConfig, AgentResult
from .tool_registry import ToolRegistry
from projectmind.summarization import CodeSummarizer
from projectmind.core.python_parser import PythonParser


class CodeAnalyzerAgent(Agent):
    """Agent specialized in code analysis."""

    def __init__(self, config: AgentConfig = None):
        """Initialize code analyzer agent.

        Args:
            config: Agent configuration
        """
        if config is None:
            config = AgentConfig(
                name="code_analyzer",
                description="Analyzes code for quality, complexity, and maintainability",
                version="1.0.0"
            )
        super().__init__(config)

        # Initialize tools
        self.tool_registry = ToolRegistry()
        self.tool_registry.register_builtin_tools()

        self.summarizer = CodeSummarizer()
        self.parser = PythonParser()

        # Register specialized tools
        self.register_tool("analyze_file", self._analyze_file)
        self.register_tool("analyze_complexity", self._analyze_complexity)
        self.register_tool("extract_functions", self._extract_functions)
        self.register_tool("calculate_metrics", self._calculate_metrics)
        self.register_tool("detect_issues", self._detect_issues)

    def _execute_task(self, task: str, params: Dict[str, Any]) -> Any:
        """Execute analysis task.

        Args:
            task: Task description
            params: Task parameters

        Returns:
            Analysis results
        """
        if task == "analyze_file":
            return self._analyze_file(params.get("file_path"))
        elif task == "analyze_complexity":
            return self._analyze_complexity(params.get("code"))
        elif task == "extract_functions":
            return self._extract_functions(params.get("code"))
        elif task == "calculate_metrics":
            return self._calculate_metrics(params.get("code"))
        elif task == "detect_issues":
            return self._detect_issues(params.get("code"))
        else:
            raise ValueError(f"Unknown task: {task}")

    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Analysis results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Parse file
            analysis = self.parser.analyze(file_path)

            # Summarize
            summary = self.summarizer.summarize_code(code)

            return {
                "file": file_path,
                "success": True,
                "analysis": analysis,
                "summary": summary,
                "metrics": {
                    "functions": len(analysis.get("functions", [])),
                    "classes": len(analysis.get("classes", [])),
                    "imports": len(analysis.get("imports", []))
                }
            }
        except Exception as e:
            return {
                "file": file_path,
                "success": False,
                "error": str(e)
            }

    def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze code complexity.

        Args:
            code: Source code

        Returns:
            Complexity metrics
        """
        lines = len(code.split('\n'))
        functions = len([l for l in code.split('\n') if l.strip().startswith('def ')])
        classes = len([l for l in code.split('\n') if l.strip().startswith('class ')])

        return {
            "lines": lines,
            "functions": functions,
            "classes": classes,
            "average_function_length": lines / functions if functions > 0 else 0
        }

    def _extract_functions(self, code: str) -> Dict[str, Any]:
        """Extract functions from code.

        Args:
            code: Source code

        Returns:
            Function information
        """
        functions = []
        for line in code.split('\n'):
            if line.strip().startswith('def '):
                func_name = line.split('(')[0].replace('def ', '').strip()
                functions.append(func_name)

        return {
            "count": len(functions),
            "functions": functions
        }

    def _calculate_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code metrics.

        Args:
            code: Source code

        Returns:
            Metrics dictionary
        """
        lines = len(code.split('\n'))
        blank_lines = len([l for l in code.split('\n') if not l.strip()])
        comment_lines = len([l for l in code.split('\n') if l.strip().startswith('#')])

        return {
            "total_lines": lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "code_lines": lines - blank_lines - comment_lines,
            "comment_ratio": comment_lines / lines if lines > 0 else 0
        }

    def _detect_issues(self, code: str) -> Dict[str, Any]:
        """Detect code issues.

        Args:
            code: Source code

        Returns:
            Issues found
        """
        issues = []
        references = []

        # Long functions - check against separation of concerns
        current_func = None
        func_lines = 0
        for line in code.split('\n'):
            if line.strip().startswith('def '):
                if current_func and func_lines > 50:
                    issues.append(f"Function '{current_func}' is too long ({func_lines} lines)")
                    references.append("See ARCHITECTURE_AND_DECISIONS.md - Separation of Concerns")
                current_func = line.split('(')[0].replace('def ', '').strip()
                func_lines = 0
            else:
                func_lines += 1

        # Complexity patterns
        if code.count('if ') > 10:
            issues.append("High conditional complexity")
            references.append("Consider refactoring per TEAM_STANDARDS.md")

        if code.count('for ') > 5 and code.count('for ') in [l for l in code.split('\n') if 'for ' in l]:
            issues.append("Multiple nested loops")
            references.append("See TEAM_STANDARDS.md - Code refactoring patterns")

        return {
            "count": len(issues),
            "issues": issues,
            "references": references
        }
