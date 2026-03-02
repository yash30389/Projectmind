"""
Context-Aware Suggestion Engine.

Generates intelligent suggestions with context references.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from .base_agent import Agent


@dataclass
class Suggestion:
    """A context-aware suggestion."""
    id: str
    title: str
    description: str
    reasoning: str
    context_reference: str
    severity: str  # "warning", "info", "recommendation"
    category: str  # "architecture", "standards", "security", "performance"
    source_agent: str


class ContextAwareSuggestionEngine:
    """Generates intelligent suggestions with context references."""

    def __init__(self, agent: Agent):
        """Initialize suggestion engine.

        Args:
            agent: Agent with context capability
        """
        self.agent = agent
        self.suggestions: List[Suggestion] = []

    def generate_suggestions(
        self,
        code: str,
        analysis_type: str = "general",
        context_topics: Optional[List[str]] = None
    ) -> List[Suggestion]:
        """Generate context-aware suggestions for code.

        Args:
            code: Source code to analyze
            analysis_type: Type of analysis (general, performance, security)
            context_topics: Topics to reference in suggestions

        Returns:
            List of suggestions with context references
        """
        self.suggestions = []
        topics = context_topics or ["standards", "architecture"]

        # Get context for reference
        context_map = {}
        for topic in topics:
            snippet = self.agent.get_context_snippet(topic)
            if snippet:
                context_map[topic] = snippet

        # Generate analysis-specific suggestions
        if analysis_type == "general":
            self._analyze_general(code, context_map)
        elif analysis_type == "performance":
            self._analyze_performance(code, context_map)
        elif analysis_type == "security":
            self._analyze_security(code, context_map)

        return self.suggestions

    def _analyze_general(self, code: str, context_map: Dict[str, str]) -> None:
        """Analyze general code quality with context."""
        lines = len(code.split('\n'))
        functions = len([l for l in code.split('\n') if l.strip().startswith('def ')])
        classes = len([l for l in code.split('\n') if l.strip().startswith('class ')])

        # Check module organization
        if functions > 0 and lines / functions > 100:
            self.suggestions.append(Suggestion(
                id="long_functions",
                title="Long Functions Detected",
                description="Functions should be concise and focused on a single responsibility.",
                reasoning="Long functions are harder to understand, test, and maintain. Breaking them into smaller, focused functions improves code clarity.",
                context_reference="ARCHITECTURE_AND_DECISIONS.md (Separation of Concerns)",
                severity="warning",
                category="architecture",
                source_agent=self.agent.config.name
            ))

        # Check naming conventions
        if code.count('def _') > code.count('def ') * 0.3:
            self.suggestions.append(Suggestion(
                id="private_methods",
                title="Multiple Private Methods",
                description="Review if all private methods should be public for better testability.",
                reasoning="Excessive private methods can make testing difficult. Consider extracting helper methods or refactoring class design.",
                context_reference="TEAM_STANDARDS.md (Testing & Error Handling)",
                severity="info",
                category="standards",
                source_agent=self.agent.config.name
            ))

        # Check complexity patterns
        if code.count('if ') > 10:
            self.suggestions.append(Suggestion(
                id="high_complexity",
                title="High Conditional Complexity",
                description="Consider reducing nested conditionals using early returns or guard clauses.",
                reasoning="Complex conditionals reduce readability and increase bug potential. Simplify using design patterns like state machines or strategy pattern.",
                context_reference="TEAM_STANDARDS.md (Code Organization)",
                severity="warning",
                category="standards",
                source_agent=self.agent.config.name
            ))

    def _analyze_performance(self, code: str, context_map: Dict[str, str]) -> None:
        """Analyze performance patterns with context."""
        # Check for inefficient patterns
        if 'for ' in code and code.count('for ') > 3:
            self.suggestions.append(Suggestion(
                id="nested_loops",
                title="Multiple Loop Structures",
                description="Evaluate if loops can be replaced with vectorized operations or more efficient algorithms.",
                reasoning="Nested loops often have O(n²) or worse complexity. Consider using comprehensions, built-in functions, or algorithms with better complexity.",
                context_reference="ARCHITECTURE_AND_DECISIONS.md (Performance Principles)",
                severity="warning",
                category="performance",
                source_agent=self.agent.config.name
            ))

        # Check for list operations in loops
        if '.append(' in code and 'for ' in code:
            self.suggestions.append(Suggestion(
                id="loop_append",
                title="List Building Pattern Detected",
                description="Consider using list comprehensions instead of loop-based appends.",
                reasoning="List comprehensions are more Pythonic, more readable, and typically faster than building lists with loop append calls.",
                context_reference="TEAM_STANDARDS.md (Python Best Practices)",
                severity="info",
                category="standards",
                source_agent=self.agent.config.name
            ))

    def _analyze_security(self, code: str, context_map: Dict[str, str]) -> None:
        """Analyze security patterns with context."""
        # Check for common security issues
        if 'eval(' in code or 'exec(' in code:
            self.suggestions.append(Suggestion(
                id="dangerous_eval",
                title="Use of eval() or exec()",
                description="Never use eval() or exec() with untrusted input. Use safer alternatives.",
                reasoning="eval() and exec() execute arbitrary Python code, creating critical security vulnerabilities. Use ast.literal_eval() for safe data parsing.",
                context_reference="BUSINESS_CONTEXT.md (Privacy-First Principle)",
                severity="warning",
                category="security",
                source_agent=self.agent.config.name
            ))

        # Check for hardcoded credentials
        if any(pattern in code for pattern in ['password =', 'api_key =', 'secret =']):
            self.suggestions.append(Suggestion(
                id="hardcoded_secrets",
                title="Hardcoded Credentials Detected",
                description="Never hardcode secrets, credentials, or API keys in source code.",
                reasoning="Hardcoded secrets expose sensitive data in repositories, building systems, and logs. Use environment variables or secure vaults.",
                context_reference="BUSINESS_CONTEXT.md (Privacy-First Principle)",
                severity="warning",
                category="security",
                source_agent=self.agent.config.name
            ))

    def get_suggestions_by_category(self, category: str) -> List[Suggestion]:
        """Get suggestions in a specific category.

        Args:
            category: Category to filter by

        Returns:
            List of suggestions for category
        """
        return [s for s in self.suggestions if s.category == category]

    def get_suggestions_by_severity(self, severity: str) -> List[Suggestion]:
        """Get suggestions with a specific severity.

        Args:
            severity: Severity level to filter by

        Returns:
            List of suggestions with given severity
        """
        return [s for s in self.suggestions if s.severity == severity]

    def format_suggestions(self, markdown: bool = False) -> str:
        """Format suggestions for output.

        Args:
            markdown: Whether to format as markdown

        Returns:
            Formatted suggestions string
        """
        if not self.suggestions:
            return "No suggestions at this time." if not markdown else "No suggestions at this time."

        output = []

        if markdown:
            output.append("# Code Suggestions\n")
            for suggestion in self.suggestions:
                output.append(f"## {suggestion.title}")
                output.append(f"- **Severity**: {suggestion.severity.upper()}")
                output.append(f"- **Category**: {suggestion.category}")
                output.append(f"\n{suggestion.description}\n")
                output.append(f"**Why**: {suggestion.reasoning}\n")
                output.append(f"**Reference**: {suggestion.context_reference}\n")
                output.append("---\n")
        else:
            output.append("CODE SUGGESTIONS\n")
            output.append("=" * 60 + "\n")
            for suggestion in self.suggestions:
                output.append(f"\n{suggestion.title.upper()}")
                output.append(f"Severity: {suggestion.severity}")
                output.append(f"Category: {suggestion.category}")
                output.append(f"\n{suggestion.description}\n")
                output.append(f"Why: {suggestion.reasoning}\n")
                output.append(f"Reference: {suggestion.context_reference}\n")
                output.append("-" * 60)

        return "\n".join(output)

    def summary(self) -> Dict[str, Any]:
        """Get summary of suggestions.

        Returns:
            Summary statistics
        """
        return {
            "total_suggestions": len(self.suggestions),
            "by_severity": {
                "warning": len(self.get_suggestions_by_severity("warning")),
                "info": len(self.get_suggestions_by_severity("info")),
                "recommendation": len(self.get_suggestions_by_severity("recommendation"))
            },
            "by_category": {
                "architecture": len(self.get_suggestions_by_category("architecture")),
                "standards": len(self.get_suggestions_by_category("standards")),
                "security": len(self.get_suggestions_by_category("security")),
                "performance": len(self.get_suggestions_by_category("performance"))
            }
        }
