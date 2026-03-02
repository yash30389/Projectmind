"""
Multi-Agent Orchestration System.

Coordinates specialized agents for complex code analysis and workflow automation.
"""

from .base_agent import Agent, AgentState, AgentResult, AgentConfig
from .tool_registry import ToolRegistry, Tool, ToolDefinition
from .code_analyzer_agent import CodeAnalyzerAgent
from .security_agent import SecurityAgent
from .documentation_agent import DocumentationAgent
from .workflow_orchestrator import (
    WorkflowOrchestrator, WorkflowDefinition, WorkflowResult, WorkflowStep, WorkflowState
)
from .suggestion_engine import ContextAwareSuggestionEngine, Suggestion
from .agent_personas import (
    AgentPersona, PersonaDefinition, PersonaSet, get_persona, get_persona_for_context_topics
)

__all__ = [
    "Agent",
    "AgentState",
    "AgentResult",
    "AgentConfig",
    "ToolRegistry",
    "Tool",
    "ToolDefinition",
    "CodeAnalyzerAgent",
    "SecurityAgent",
    "DocumentationAgent",
    "WorkflowOrchestrator",
    "WorkflowDefinition",
    "WorkflowResult",
    "WorkflowStep",
    "WorkflowState",
    "ContextAwareSuggestionEngine",
    "Suggestion",
    "AgentPersona",
    "PersonaDefinition",
    "PersonaSet",
    "get_persona",
    "get_persona_for_context_topics",
]
