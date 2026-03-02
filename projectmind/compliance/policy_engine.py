"""
Policy Engine: Hard-enforced constraint validation.

Every action is validated against project constraints BEFORE execution.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from projectmind.core.context import ProjectContext, ContextLoader


@dataclass
class PolicyViolation:
    """Represents a policy constraint violation."""

    violated_constraint: str
    severity: str  # "hard", "warning", "info"
    message: str
    suggested_fix: Optional[str] = None


@dataclass
class ActionRequest:
    """Request to validate an action."""

    agent_name: str
    action_type: str  # "edit", "delete", "create", "suggest", "analyze"
    target_file: str
    line_range: Optional[tuple] = None  # (start, end)
    change_summary: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PolicyEngine:
    """
    Validates actions against project constraints.

    Enforces:
    - no_autonomous_changes
    - must_explain_reasoning
    - respect_architecture
    - custom constraints
    """

    # Security-critical file patterns
    SECURITY_CRITICAL_PATTERNS = [
        "**/auth.py",
        "**/security.py",
        "**/crypto.py",
        "**/password.py",
        "**/.env",
        "**/config/secrets.yaml",
    ]

    # Files that should never be auto-edited
    PROTECTED_FILES = [
        "project_context.yaml",
        ".pmind/decisions/*",
        "pyproject.toml",
        "requirements.txt",
    ]

    def __init__(self, context: ProjectContext):
        """Initialize with project context."""
        self.context = context
        self.violations: List[PolicyViolation] = []

    @staticmethod
    def from_file(context_file: str = "project_context.yaml") -> "PolicyEngine":
        """Create from context YAML file."""
        context = ContextLoader.load_from_file(context_file)
        return PolicyEngine(context)

    def validate_action(self, request: ActionRequest) -> bool:
        """
        Validate an action request.

        Returns True if action is allowed, False if denied.
        Populates self.violations with any issues.
        """
        self.violations = []

        # Check core constraints
        if self.context.constraints.no_autonomous_changes:
            if request.action_type in ["edit", "delete", "create"]:
                self.violations.append(
                    PolicyViolation(
                        violated_constraint="no_autonomous_changes",
                        severity="hard",
                        message=f"Autonomous {request.action_type} not allowed",
                        suggested_fix="Use 'suggest' action instead, require human approval",
                    )
                )

        # Check if file is protected
        if self._is_protected_file(request.target_file):
            self.violations.append(
                PolicyViolation(
                    violated_constraint="protect_critical_files",
                    severity="hard",
                    message=f"Cannot modify protected file: {request.target_file}",
                    suggested_fix="Review with team before modifying critical files",
                )
            )

        # Check if file is security-critical
        if self._is_security_critical(request.target_file):
            if request.action_type in ["edit", "delete"]:
                self.violations.append(
                    PolicyViolation(
                        violated_constraint="protect_security_files",
                        severity="hard",
                        message=f"Cannot modify security-critical file: {request.target_file}",
                        suggested_fix="Security review required before changes",
                    )
                )

        # Check custom constraints
        for custom_constraint in self.context.constraints.custom_constraints:
            violation = self._check_custom_constraint(
                request, custom_constraint
            )
            if violation:
                self.violations.append(violation)

        # Hard constraint: if there are any "hard" violations, reject
        hard_violations = [v for v in self.violations if v.severity == "hard"]
        return len(hard_violations) == 0

    def get_violations(self) -> List[PolicyViolation]:
        """Get list of violations from last validation."""
        return self.violations

    def get_refusal_reason(self) -> str:
        """Get human-readable reason why action was refused."""
        if not self.violations:
            return "No violations"

        reasons = []
        for violation in self.violations:
            reasons.append(f"❌ {violation.message}")
            if violation.suggested_fix:
                reasons.append(f"   → {violation.suggested_fix}")

        return "\n".join(reasons)

    def _is_protected_file(self, file_path: str) -> bool:
        """Check if file is in protected list."""
        from fnmatch import fnmatch

        for pattern in self.PROTECTED_FILES:
            if fnmatch(file_path, pattern):
                return True
        return False

    def _is_security_critical(self, file_path: str) -> bool:
        """Check if file is security-critical."""
        from fnmatch import fnmatch

        for pattern in self.SECURITY_CRITICAL_PATTERNS:
            if fnmatch(file_path, pattern):
                return True
        return False

    def _check_custom_constraint(
        self, request: ActionRequest, constraint: str
    ) -> Optional[PolicyViolation]:
        """Check custom constraint against action."""
        # Parse constraint format: "verb noun conditions"
        # Examples:
        # - "Never modify auth files"
        # - "Always explain security changes"
        # - "Require review for database changes"

        lower_constraint = constraint.lower()
        lower_file = request.target_file.lower()

        # Simple pattern matching for common constraints
        if "never" in lower_constraint and "modify" in lower_constraint:
            for keyword in ["auth", "crypto", "password", "secret"]:
                if keyword in lower_constraint and keyword in lower_file:
                    return PolicyViolation(
                        violated_constraint="custom",
                        severity="hard",
                        message=f"Constraint violated: {constraint}",
                        suggested_fix="Review project constraints",
                    )

        if "always" in lower_constraint and "explain" in lower_constraint:
            if not request.change_summary:
                return PolicyViolation(
                    violated_constraint="custom",
                    severity="warning",
                    message=f"Constraint violated: {constraint}",
                    suggested_fix="Provide explanation for changes",
                )

        return None
