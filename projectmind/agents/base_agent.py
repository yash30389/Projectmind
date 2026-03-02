"""
Base Agent Framework.

Provides foundation for all specialized agents.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid
from datetime import datetime
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Agent execution states."""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    description: str
    version: str = "1.0.0"
    timeout: int = 300  # 5 minutes
    max_retries: int = 3
    verbose: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution."""
    agent_name: str
    success: bool
    output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error: Optional[str] = None


class Agent:
    """Base class for all agents."""

    def __init__(self, config: AgentConfig):
        """Initialize agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.id = str(uuid.uuid4())
        self.state = AgentState.IDLE
        self.created_at = datetime.now()
        self.tools = {}
        self.context = {}
        self.memory = []
        
        # Load knowledge system context
        self._load_knowledge_context()

    def register_tool(self, tool_name: str, tool_func) -> None:
        """Register a tool for this agent.

        Args:
            tool_name: Name of the tool
            tool_func: Callable tool function
        """
        self.tools[tool_name] = tool_func
        if self.config.verbose:
            print(f"[{self.config.name}] Registered tool: {tool_name}")

    def _load_knowledge_context(self) -> None:
        """Load business context, architecture, and standards.
        
        Loads knowledge system documentation into agent for context-aware decisions.
        """
        try:
            # Get project root (parent of projectmind folder)
            project_root = Path(__file__).parent.parent.parent
            
            self.business_context = self._load_markdown(
                project_root / "docs" / "BUSINESS_CONTEXT.md"
            )
            self.architecture = self._load_markdown(
                project_root / "docs" / "ARCHITECTURE_AND_DECISIONS.md"
            )
            self.standards = self._load_markdown(
                project_root / "docs" / "TEAM_STANDARDS.md"
            )
            self.project_context = self._load_yaml(
                project_root / "project_context.yaml"
            )
            
            if self.config.verbose:
                print(f"[{self.config.name}] Knowledge context loaded")
                
        except Exception as e:
            logger.warning(f"Could not load knowledge context: {e}")
            self.business_context = ""
            self.architecture = ""
            self.standards = ""
            self.project_context = {}

    def _load_markdown(self, path: Path) -> str:
        """Load markdown file contents.
        
        Args:
            path: Path to markdown file
            
        Returns:
            File contents as string
        """
        try:
            if path.exists():
                return path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"Could not load {path}: {e}")
        return ""

    def _load_yaml(self, path: Path) -> dict:
        """Load YAML configuration.
        
        Args:
            path: Path to YAML file
            
        Returns:
            Parsed YAML as dictionary
        """
        try:
            if path.exists():
                with open(path, encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Could not load {path}: {e}")
        return {}

    def get_context_snippet(self, topic: str) -> str:
        """Retrieve relevant context by topic.
        
        Args:
            topic: Topic to retrieve context for
                   Examples: "architecture", "decisions", "business", "naming"
        
        Returns:
            Relevant context snippet
        """
        context_sources = {
            "architecture": self.architecture,
            "decisions": self.architecture,
            "design": self.architecture,
            "business": self.business_context,
            "goals": self.business_context,
            "values": self.business_context,
            "principles": self.business_context,
            "naming": self.standards,
            "testing": self.standards,
            "error_handling": self.standards,
            "logging": self.standards,
            "standards": self.standards,
            "conventions": self.standards,
        }
        return context_sources.get(topic, "")

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set agent context.

        Args:
            context: Context dictionary
        """
        self.context.update(context)

    def add_memory(self, entry: Dict[str, Any]) -> None:
        """Add entry to agent memory.

        Args:
            entry: Memory entry
        """
        entry["timestamp"] = datetime.now().isoformat()
        self.memory.append(entry)

    def get_memory(self) -> List[Dict[str, Any]]:
        """Get agent memory.

        Returns:
            List of memory entries
        """
        return self.memory

    def clear_memory(self) -> None:
        """Clear agent memory."""
        self.memory = []

    def execute(self, task: str, params: Dict[str, Any]) -> AgentResult:
        """Execute a task.

        Args:
            task: Task description
            params: Task parameters

        Returns:
            AgentResult with outcome
        """
        try:
            self.state = AgentState.RUNNING
            start_time = datetime.now()

            # Log task
            self.add_memory({
                "type": "task",
                "task": task,
                "params": params,
                "status": "started"
            })

            # Execute task (override in subclasses)
            output = self._execute_task(task, params)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Log completion
            self.add_memory({
                "type": "task",
                "task": task,
                "status": "completed",
                "execution_time": execution_time
            })

            self.state = AgentState.COMPLETED

            return AgentResult(
                agent_name=self.config.name,
                success=True,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            self.state = AgentState.FAILED

            # Log error
            self.add_memory({
                "type": "error",
                "task": task,
                "error": str(e)
            })

            return AgentResult(
                agent_name=self.config.name,
                success=False,
                output=None,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )

    def _execute_task(self, task: str, params: Dict[str, Any]) -> Any:
        """Execute a specific task (override in subclasses).

        Args:
            task: Task description
            params: Task parameters

        Returns:
            Task output
        """
        raise NotImplementedError("Subclasses must implement _execute_task")

    def get_status(self) -> Dict[str, Any]:
        """Get agent status.

        Returns:
            Status dictionary
        """
        return {
            "id": self.id,
            "name": self.config.name,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "tools": list(self.tools.keys()),
            "memory_entries": len(self.memory),
            "context_keys": list(self.context.keys())
        }

    def reset(self) -> None:
        """Reset agent state."""
        self.state = AgentState.IDLE
        self.context = {}
        self.clear_memory()

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.config.name} (id={self.id[:8]}, state={self.state.value})>"
