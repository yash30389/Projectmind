"""
Agent Personas.

Different agent personalities based on context focus areas.
"""

from typing import List, Optional
from enum import Enum


class AgentPersona(str, Enum):
    """Agent personality types."""
    ARCHITECT = "architect"  # Focuses on architecture and design
    GUARDIAN = "guardian"     # Focuses on security and compliance
    CRAFTSMAN = "craftsman"   # Focuses on code quality and standards
    MENTOR = "mentor"         # Focuses on learning and best practices
    GENERALIST = "generalist" # Balanced across all areas


class PersonaDefinition:
    """Definition of an agent persona."""

    def __init__(
        self,
        name: AgentPersona,
        description: str,
        focus_topics: List[str],
        primary_concern: str,
        recommendation_style: str,
        question_template: str
    ):
        """Initialize persona definition.

        Args:
            name: Persona name
            description: Human-readable description
            focus_topics: Context topics this persona emphasizes
            primary_concern: What this persona prioritizes
            recommendation_style: How this persona makes recommendations
            question_template: Template for critical questions
        """
        self.name = name
        self.description = description
        self.focus_topics = focus_topics
        self.primary_concern = primary_concern
        self.recommendation_style = recommendation_style
        self.question_template = question_template

    def apply_to_analysis(self, suggestions: List[dict]) -> List[dict]:
        """Apply persona lens to analysis suggestions.

        Args:
            suggestions: Raw suggestions from analysis

        Returns:
            Persona-filtered and reframed suggestions
        """
        # Filter suggestions relevant to this persona's focus
        relevant = []
        for suggestion in suggestions:
            category = suggestion.get("category", "")
            if self._is_relevant(category):
                enhanced = suggestion.copy()
                enhanced["persona_angle"] = self._reframe(suggestion)
                enhanced["critical_question"] = self.question_template.format(
                    aspect=suggestion.get("title", "aspect")
                )
                relevant.append(enhanced)
        return relevant

    def _is_relevant(self, category: str) -> bool:
        """Check if category is relevant to persona."""
        # Map categories to focus topics
        category_focus = {
            "architecture": "architecture",
            "standards": "naming",
            "security": "business",
            "performance": "architecture"
        }
        return category_focus.get(category, "") in self.focus_topics

    def _reframe(self, suggestion: dict) -> str:
        """Reframe suggestion from persona perspective."""
        return f"From a {self.name.value} perspective: {self.recommendation_style}"


# Predefined personas
PERSONAS = {
    AgentPersona.ARCHITECT: PersonaDefinition(
        name=AgentPersona.ARCHITECT,
        description="Focuses on system design, architecture, and separation of concerns",
        focus_topics=["architecture", "design", "decisions"],
        primary_concern="Is the system well-designed and maintainable?",
        recommendation_style="Recommends architectural patterns and system organization",
        question_template="Does this {aspect} align with our architectural principles?"
    ),
    AgentPersona.GUARDIAN: PersonaDefinition(
        name=AgentPersona.GUARDIAN,
        description="Focuses on security, privacy, and compliance",
        focus_topics=["business", "goals", "principles"],
        primary_concern="Is the system secure and privacy-respecting?",
        recommendation_style="Emphasizes security implications and privacy concerns",
        question_template="Are our privacy principles reflected in {aspect}?"
    ),
    AgentPersona.CRAFTSMAN: PersonaDefinition(
        name=AgentPersona.CRAFTSMAN,
        description="Focuses on code quality, standards, and best practices",
        focus_topics=["standards", "conventions", "naming"],
        primary_concern="Is the code clean, readable, and maintainable?",
        recommendation_style="Provides detailed feedback on code style and organization",
        question_template="Does {aspect} follow our team standards?"
    ),
    AgentPersona.MENTOR: PersonaDefinition(
        name=AgentPersona.MENTOR,
        description="Focuses on learning, improvement, and best practices",
        focus_topics=["standards", "testing", "error_handling"],
        primary_concern="Will developers learn and improve from this?",
        recommendation_style="Explains reasoning and educates about alternatives",
        question_template="What can we learn from {aspect}?"
    ),
    AgentPersona.GENERALIST: PersonaDefinition(
        name=AgentPersona.GENERALIST,
        description="Balanced focus across architecture, standards, and security",
        focus_topics=["architecture", "standards", "business"],
        primary_concern="Is this code good overall?",
        recommendation_style="Provides balanced, practical recommendations",
        question_template="Is {aspect} effective and appropriate?"
    ),
}


def get_persona(name: AgentPersona) -> PersonaDefinition:
    """Get a persona definition.

    Args:
        name: Persona name

    Returns:
        Persona definition
    """
    return PERSONAS.get(name, PERSONAS[AgentPersona.GENERALIST])


def get_persona_for_context_topics(topics: List[str]) -> AgentPersona:
    """Determine best persona for given context topics.

    Args:
        topics: List of context topics

    Returns:
        Recommended persona
    """
    # Score each persona against the topics
    scores = {}
    for persona_name, persona in PERSONAS.items():
        score = sum(1 for topic in topics if topic in persona.focus_topics)
        scores[persona_name] = score

    # Return persona with highest score
    if scores:
        return max(scores, key=scores.get)
    return AgentPersona.GENERALIST


class PersonaSet:
    """A set of personas working together."""

    def __init__(self, personas: Optional[List[AgentPersona]] = None):
        """Initialize persona set.

        Args:
            personas: List of personas (defaults to all)
        """
        self.personas = personas or list(PERSONAS.keys())

    def get_all_perspectives(self, aspect: str) -> dict:
        """Get all persona perspectives on an aspect.

        Args:
            aspect: Aspect to get perspectives on

        Returns:
            Dictionary of perspectives by persona
        """
        perspectives = {}
        for persona_name in self.personas:
            persona = get_persona(persona_name)
            perspective = {
                "focus": persona.primary_concern,
                "approach": persona.recommendation_style,
                "critical_question": persona.question_template.format(aspect=aspect),
                "relevant_topics": persona.focus_topics
            }
            perspectives[persona_name.value] = perspective
        return perspectives

    def summarize_perspectives(self) -> str:
        """Get summary of all perspectives in this set.

        Returns:
            Human-readable summary
        """
        lines = ["## Multi-Persona Analysis Approach\n"]

        for persona_name in self.personas:
            persona = get_persona(persona_name)
            lines.append(f"### {persona_name.value.upper()}")
            lines.append(f"**Focus**: {persona.primary_concern}")
            lines.append(f"**Approach**: {persona.recommendation_style}")
            lines.append(f"**Topics**: {', '.join(persona.focus_topics)}\n")

        return "\n".join(lines)
