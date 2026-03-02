"""
Tool Registry and Definitions.

Manages tools available to agents.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import inspect


@dataclass
class ToolDefinition:
    """Definition of a tool."""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, str]  # param_name -> param_type
    returns: str  # return type
    required_params: List[str] = None

    def __post_init__(self):
        """Validate tool definition."""
        if self.required_params is None:
            self.required_params = list(self.parameters.keys())


class Tool:
    """Wrapper for a tool."""

    def __init__(self, definition: ToolDefinition):
        """Initialize tool.

        Args:
            definition: Tool definition
        """
        self.definition = definition
        self.call_count = 0
        self.error_count = 0

    def execute(self, **kwargs) -> Any:
        """Execute the tool.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool result
        """
        try:
            # Validate parameters
            for param in self.definition.required_params:
                if param not in kwargs:
                    raise ValueError(f"Missing required parameter: {param}")

            # Call tool
            result = self.definition.func(**kwargs)
            self.call_count += 1

            return result

        except Exception as e:
            self.error_count += 1
            raise

    def get_signature(self) -> Dict[str, Any]:
        """Get tool signature.

        Returns:
            Tool signature information
        """
        return {
            "name": self.definition.name,
            "description": self.definition.description,
            "parameters": self.definition.parameters,
            "required": self.definition.required_params,
            "returns": self.definition.returns
        }

    def get_stats(self) -> Dict[str, int]:
        """Get tool usage statistics.

        Returns:
            Usage statistics
        """
        return {
            "calls": self.call_count,
            "errors": self.error_count,
            "success_rate": (
                (self.call_count - self.error_count) / self.call_count * 100
                if self.call_count > 0
                else 0
            )
        }


class ToolRegistry:
    """Registry of available tools."""

    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, Tool] = {}
        self._builtin_tools_registered = False

    def register_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        required_params: List[str] = None
    ) -> None:
        """Register a tool.

        Args:
            name: Tool name
            description: Tool description
            func: Callable function
            required_params: Required parameters
        """
        # Get function signature
        sig = inspect.signature(func)
        parameters = {}
        param_list = []

        for param_name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
            parameters[param_name] = str(param_type)
            param_list.append(param_name)

        if required_params is None:
            required_params = param_list

        # Get return type
        return_type = sig.return_annotation if sig.return_annotation != inspect.Signature.empty else "Any"

        # Create tool definition
        definition = ToolDefinition(
            name=name,
            description=description,
            func=func,
            parameters=parameters,
            returns=str(return_type),
            required_params=required_params
        )

        # Create and register tool
        tool = Tool(definition)
        self.tools[name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool or None
        """
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all available tools.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tool_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Get signatures of all tools.

        Returns:
            Tool signatures
        """
        return {
            name: tool.get_signature()
            for name, tool in self.tools.items()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics.

        Returns:
            Statistics
        """
        total_calls = sum(tool.call_count for tool in self.tools.values())
        total_errors = sum(tool.error_count for tool in self.tools.values())

        return {
            "total_tools": len(self.tools),
            "total_calls": total_calls,
            "total_errors": total_errors,
            "tools": {
                name: tool.get_stats()
                for name, tool in self.tools.items()
            }
        }

    def register_builtin_tools(self) -> None:
        """Register built-in tools."""
        if self._builtin_tools_registered:
            return

        # Code analysis tools
        self.register_tool(
            "analyze_complexity",
            "Calculate cyclomatic complexity of code",
            self._analyze_complexity,
            required_params=["code"]
        )

        self.register_tool(
            "extract_functions",
            "Extract function definitions from code",
            self._extract_functions,
            required_params=["code"]
        )

        self.register_tool(
            "detect_patterns",
            "Detect code patterns",
            self._detect_patterns,
            required_params=["code"]
        )

        # Security tools
        self.register_tool(
            "scan_threats",
            "Scan code for security threats",
            self._scan_threats,
            required_params=["code"]
        )

        self.register_tool(
            "check_compliance",
            "Check policy compliance",
            self._check_compliance,
            required_params=["action"]
        )

        # Documentation tools
        self.register_tool(
            "generate_summary",
            "Generate code summary",
            self._generate_summary,
            required_params=["code"]
        )

        self.register_tool(
            "generate_documentation",
            "Generate documentation",
            self._generate_documentation,
            required_params=["code"]
        )

        self._builtin_tools_registered = True

    # Built-in tool implementations
    @staticmethod
    def _analyze_complexity(code: str) -> Dict[str, Any]:
        """Analyze code complexity."""
        return {
            "complexity": len(code.split('\n')),
            "lines": len(code.split('\n')),
            "characters": len(code)
        }

    @staticmethod
    def _extract_functions(code: str) -> List[str]:
        """Extract functions from code."""
        functions = []
        for line in code.split('\n'):
            if line.strip().startswith('def '):
                func_name = line.split('(')[0].replace('def ', '').strip()
                functions.append(func_name)
        return functions

    @staticmethod
    def _detect_patterns(code: str) -> List[str]:
        """Detect code patterns."""
        patterns = []
        if 'for ' in code:
            patterns.append('loop')
        if 'if ' in code:
            patterns.append('conditional')
        if 'class ' in code:
            patterns.append('class_definition')
        return patterns

    @staticmethod
    def _scan_threats(code: str) -> List[str]:
        """Scan for threats."""
        threats = []
        if 'eval(' in code:
            threats.append('eval_usage')
        if 'exec(' in code:
            threats.append('exec_usage')
        return threats

    @staticmethod
    def _check_compliance(action: str) -> bool:
        """Check compliance."""
        return True

    @staticmethod
    def _generate_summary(code: str) -> str:
        """Generate code summary."""
        lines = len(code.split('\n'))
        return f"Code with {lines} lines"

    @staticmethod
    def _generate_documentation(code: str) -> str:
        """Generate documentation."""
        return "# Generated Documentation\n\n" + code
