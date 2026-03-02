"""
Documentation Agent.

Specialized agent for documentation generation.
"""

from typing import Any, Dict
from .base_agent import Agent, AgentConfig
from .tool_registry import ToolRegistry
from projectmind.summarization import DocumentationGenerator, CodeSummarizer


class DocumentationAgent(Agent):
    """Agent specialized in documentation generation."""

    def __init__(self, config: AgentConfig = None):
        """Initialize documentation agent.

        Args:
            config: Agent configuration
        """
        if config is None:
            config = AgentConfig(
                name="documentation",
                description="Generates documentation from code analysis",
                version="1.0.0"
            )
        super().__init__(config)

        # Initialize documentation tools
        self.doc_generator = DocumentationGenerator()
        self.summarizer = CodeSummarizer()

        # Register tools
        self.register_tool("generate_module_docs", self._generate_module_docs)
        self.register_tool("generate_api_reference", self._generate_api_reference)
        self.register_tool("generate_summary", self._generate_summary)
        self.register_tool("generate_docstrings", self._generate_docstrings)

    def _execute_task(self, task: str, params: Dict[str, Any]) -> Any:
        """Execute documentation task.

        Args:
            task: Task description
            params: Task parameters

        Returns:
            Generated documentation
        """
        if task == "generate_module_docs":
            return self._generate_module_docs(params.get("file_path"))
        elif task == "generate_api_reference":
            return self._generate_api_reference(params.get("code"))
        elif task == "generate_summary":
            return self._generate_summary(params.get("code"))
        elif task == "generate_docstrings":
            return self._generate_docstrings(params.get("code"))
        else:
            raise ValueError(f"Unknown task: {task}")

    def _generate_module_docs(self, file_path: str) -> Dict[str, Any]:
        """Generate documentation for a module.

        Args:
            file_path: Path to Python file

        Returns:
            Module documentation
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Generate documentation
            doc = f"# Module Documentation: {file_path}\n\n"
            doc += self._analyze_module(code)
            
            standards_context = self.get_context_snippet("standards")
            if standards_context:
                doc += "\n## Documentation Standards\nSee TEAM_STANDARDS.md for naming conventions and code organization.\n"

            self.add_memory({
                "type": "documentation_generated",
                "file": file_path,
                "type": "module_docs"
            })

            return {
                "success": True,
                "file": file_path,
                "documentation": doc,
                "type": "module",
                "standards_reference": "TEAM_STANDARDS.md"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_api_reference(self, code: str) -> Dict[str, Any]:
        """Generate API reference from code.

        Args:
            code: Source code

        Returns:
            API reference
        """
        try:
            api_ref = "# API Reference\n\n"

            # Extract functions
            functions = []
            for line in code.split('\n'):
                if line.strip().startswith('def '):
                    func_name = line.split('(')[0].replace('def ', '').strip()
                    functions.append(func_name)

            if functions:
                api_ref += "## Functions\n\n"
                for func in functions:
                    api_ref += f"- `{func}`\n"

            # Extract classes
            classes = []
            for line in code.split('\n'):
                if line.strip().startswith('class '):
                    class_name = line.split('(')[0].replace('class ', '').strip()
                    if class_name:
                        classes.append(class_name)

            if classes:
                api_ref += "\n## Classes\n\n"
                for cls in classes:
                    api_ref += f"- `{cls}`\n"
            
            naming_context = self.get_context_snippet("naming")
            if naming_context:
                api_ref += "\n**Note**: See TEAM_STANDARDS.md for naming conventions and API design patterns.\n"

            return {
                "success": True,
                "reference": api_ref,
                "functions_count": len(functions),
                "classes_count": len(classes),
                "standards_reference": "TEAM_STANDARDS.md"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_summary(self, code: str) -> Dict[str, Any]:
        """Generate code summary.

        Args:
            code: Source code

        Returns:
            Code summary
        """
        try:
            lines = len(code.split('\n'))
            functions = len([l for l in code.split('\n') if l.strip().startswith('def ')])
            classes = len([l for l in code.split('\n') if l.strip().startswith('class ')])

            summary = f"""
# Code Summary

- **Lines of Code**: {lines}
- **Functions**: {functions}
- **Classes**: {classes}
- **Complexity**: {'High' if functions > 10 else 'Medium' if functions > 5 else 'Low'}

## Overview
This code module contains {functions} functions and {classes} classes across {lines} lines of code.

## Architecture
For system design and separation of concerns, see ARCHITECTURE_AND_DECISIONS.md.
"""

            self.add_memory({
                "type": "summary_generated",
                "lines": lines,
                "functions": functions,
                "classes": classes
            })

            return {
                "success": True,
                "summary": summary,
                "stats": {
                    "lines": lines,
                    "functions": functions,
                    "classes": classes
                },
                "architecture_reference": "ARCHITECTURE_AND_DECISIONS.md"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_docstrings(self, code: str) -> Dict[str, str]:
        """Generate docstrings for functions.

        Args:
            code: Source code

        Returns:
            Docstrings for functions
        """
        docstrings = {}

        for line in code.split('\n'):
            if line.strip().startswith('def '):
                func_name = line.split('(')[0].replace('def ', '').strip()
                params = line.split('(')[1].split(')')[0] if '(' in line else ''

                docstring = f'''"""
{func_name} function.

Args:
    {params if params else 'See implementation'}

Returns:
    See implementation
"""'''

                docstrings[func_name] = docstring

        return {
            "success": True,
            "docstrings": docstrings,
            "count": len(docstrings)
        }

    def _analyze_module(self, code: str) -> str:
        """Analyze module and create documentation.

        Args:
            code: Source code

        Returns:
            Module analysis
        """
        analysis = "## Module Structure\n\n"

        # Find imports
        imports = [l.strip() for l in code.split('\n') if l.strip().startswith('import ') or l.strip().startswith('from ')]
        if imports:
            analysis += "### Imports\n"
            for imp in imports[:5]:  # First 5 imports
                analysis += f"- {imp}\n"
            if len(imports) > 5:
                analysis += f"- ... and {len(imports) - 5} more\n"

        # Find functions
        functions = [l.strip() for l in code.split('\n') if l.strip().startswith('def ')]
        if functions:
            analysis += f"\n### Functions ({len(functions)})\n"
            for func in functions[:5]:
                func_name = func.split('(')[0].replace('def ', '')
                analysis += f"- {func_name}\n"
            if len(functions) > 5:
                analysis += f"- ... and {len(functions) - 5} more\n"

        # Find classes
        classes = [l.strip() for l in code.split('\n') if l.strip().startswith('class ')]
        if classes:
            analysis += f"\n### Classes ({len(classes)})\n"
            for cls in classes:
                class_name = cls.split('(')[0].split(':')[0].replace('class ', '')
                analysis += f"- {class_name}\n"

        return analysis
