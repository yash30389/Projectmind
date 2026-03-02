"""
Layer B: Context & Memory Layer

Stores and loads project vision, goals, and constraints.
This is your AI's long-term memory and alignment mechanism.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml
import json


@dataclass
class ProjectVision:
    """Project vision and purpose."""

    name: str
    description: str
    target_users: str
    key_principles: List[str]


@dataclass
class ProjectConstraints:
    """Rules the AI must follow."""

    no_autonomous_changes: bool = True
    must_explain_reasoning: bool = True
    respect_architecture: bool = True
    custom_constraints: List[str] = None

    def __post_init__(self):
        if self.custom_constraints is None:
            self.custom_constraints = []


@dataclass
class ProjectContext:
    """Complete project context for AI."""

    vision: ProjectVision
    constraints: ProjectConstraints
    tech_stack: List[str]
    architecture_notes: str
    team_size: int
    deployment_target: str

    def to_dict(self) -> Dict:
        return {
            "vision": {
                "name": self.vision.name,
                "description": self.vision.description,
                "target_users": self.vision.target_users,
                "key_principles": self.vision.key_principles,
            },
            "constraints": {
                "no_autonomous_changes": self.constraints.no_autonomous_changes,
                "must_explain_reasoning": self.constraints.must_explain_reasoning,
                "respect_architecture": self.constraints.respect_architecture,
                "custom_constraints": self.constraints.custom_constraints,
            },
            "tech_stack": self.tech_stack,
            "architecture_notes": self.architecture_notes,
            "team_size": self.team_size,
            "deployment_target": self.deployment_target,
        }


class ContextLoader:
    """Load and manage project context from YAML."""

    DEFAULT_CONTEXT_FILE = "project_context.yaml"

    @staticmethod
    def create_default() -> ProjectContext:
        """Create default project context."""
        return ProjectContext(
            vision=ProjectVision(
                name="ProjectMind",
                description="Local, project-aware AI engineering system",
                target_users="Software engineers and teams",
                key_principles=[
                    "Explainability",
                    "Determinism",
                    "Human-in-the-loop",
                    "No autonomous harm",
                ],
            ),
            constraints=ProjectConstraints(
                no_autonomous_changes=True,
                must_explain_reasoning=True,
                respect_architecture=True,
                custom_constraints=[
                    "AI cannot edit files directly",
                    "All suggestions must include reasoning",
                    "Respect existing architecture decisions",
                    "Refuse unsafe requests",
                ],
            ),
            tech_stack=["Python 3.9+", "Click CLI", "PyYAML", "Pydantic"],
            architecture_notes="Four-layer system: Repository Intelligence, Context & Memory, CLI, Architecture Discipline",
            team_size=1,
            deployment_target="Local machine",
        )

    @staticmethod
    def save_to_file(context: ProjectContext, file_path: str = DEFAULT_CONTEXT_FILE):
        """Save context to YAML file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        yaml_content = yaml.dump(context.to_dict(), default_flow_style=False, sort_keys=False)
        with open(path, "w") as f:
            f.write(yaml_content)

    @staticmethod
    def load_from_file(file_path: str = DEFAULT_CONTEXT_FILE) -> ProjectContext:
        """Load context from YAML file."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Context file not found: {file_path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        return ContextLoader._from_dict(data)

    @staticmethod
    def _from_dict(data: Dict[str, Any]) -> ProjectContext:
        """Convert dictionary to ProjectContext."""
        vision_data = data.get("vision", {})
        vision = ProjectVision(
            name=vision_data.get("name", "Unknown"),
            description=vision_data.get("description", ""),
            target_users=vision_data.get("target_users", ""),
            key_principles=vision_data.get("key_principles", []),
        )

        constraints_data = data.get("constraints", {})
        constraints = ProjectConstraints(
            no_autonomous_changes=constraints_data.get("no_autonomous_changes", True),
            must_explain_reasoning=constraints_data.get("must_explain_reasoning", True),
            respect_architecture=constraints_data.get("respect_architecture", True),
            custom_constraints=constraints_data.get("custom_constraints", []),
        )

        return ProjectContext(
            vision=vision,
            constraints=constraints,
            tech_stack=data.get("tech_stack", []),
            architecture_notes=data.get("architecture_notes", ""),
            team_size=data.get("team_size", 1),
            deployment_target=data.get("deployment_target", ""),
        )
