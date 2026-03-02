"""Refusal logic: Safe ways to say no."""

from typing import List, Optional


class RefusalLogic:
    """Generate clear, safe refusal messages."""

    REFUSAL_TEMPLATES = {
        "no_autonomous": "I cannot autonomously {action} {target}. This requires human approval per project policy.",
        "protected_file": "{target} is a protected system file. Manual review required before changes.",
        "security_risk": "Security risk detected in {target}. Cannot proceed without approval.",
        "missing_explanation": "Changes to {target} require a clear explanation of the reasoning.",
        "custom": "{reason}",
    }

    @staticmethod
    def generate_refusal(
        reason: str,
        action: str = "",
        target: str = "",
        custom_reason: str = ""
    ) -> str:
        """Generate a clear refusal message."""
        if reason == "custom":
            return RefusalLogic.REFUSAL_TEMPLATES["custom"].format(reason=custom_reason)

        template = RefusalLogic.REFUSAL_TEMPLATES.get(reason, RefusalLogic.REFUSAL_TEMPLATES["custom"])

        return template.format(action=action, target=target, reason=custom_reason or reason)

    @staticmethod
    def format_refusal_with_suggestions(
        reason: str,
        suggestions: Optional[List[str]] = None
    ) -> str:
        """Format refusal with helpful suggestions."""
        lines = [
            f"❌ {reason}",
            "",
            "Suggested alternatives:",
        ]

        if suggestions:
            for suggestion in suggestions:
                lines.append(f"  → {suggestion}")
        else:
            lines.append("  → Request human review for manual approval")
            lines.append("  → Review project constraints in project_context.yaml")
            lines.append("  → Check for security issues in target files")

        return "\n".join(lines)
