"""
Security Agent.

Specialized agent for security analysis and threat detection.
"""

from typing import Any, Dict, List, Optional
from .base_agent import Agent, AgentConfig
from .tool_registry import ToolRegistry
from projectmind.security import ThreatDetector
from projectmind.compliance import PolicyEngine


class SecurityAgent(Agent):
    """Agent specialized in security analysis."""

    def __init__(self, config: AgentConfig = None):
        """Initialize security agent.

        Args:
            config: Agent configuration
        """
        if config is None:
            config = AgentConfig(
                name="security",
                description="Analyzes code for security threats and compliance violations",
                version="1.0.0"
            )
        super().__init__(config)

        # Initialize security tools
        self.threat_detector = ThreatDetector()
        self.policy_engine: Optional[PolicyEngine] = None

        # Register tools
        self.register_tool("scan_threats", self._scan_threats)
        self.register_tool("check_compliance", self._check_compliance)
        self.register_tool("validate_action", self._validate_action)
        self.register_tool("generate_security_report", self._generate_security_report)

    def _get_policy_engine(self) -> PolicyEngine:
        """Get or create policy engine.

        Returns:
            Policy engine instance
        """
        if self.policy_engine is None:
            from projectmind.core import ProjectContext
            context = ProjectContext()
            self.policy_engine = PolicyEngine(context)
        return self.policy_engine

    def _execute_task(self, task: str, params: Dict[str, Any]) -> Any:
        """Execute security task.

        Args:
            task: Task description
            params: Task parameters

        Returns:
            Security analysis results
        """
        if task == "scan_threats":
            return self._scan_threats(params.get("code"))
        elif task == "check_compliance":
            return self._check_compliance(params.get("action"))
        elif task == "validate_action":
            return self._validate_action(params.get("action"), params.get("request"))
        elif task == "generate_security_report":
            return self._generate_security_report(params.get("code"))
        else:
            raise ValueError(f"Unknown task: {task}")

    def _scan_threats(self, code: str) -> Dict[str, Any]:
        """Scan code for security threats.

        Args:
            code: Source code

        Returns:
            Threat detection results
        """
        try:
            threats = self.threat_detector.detect_threats(code)
            business_context = self.get_context_snippet("business")

            result = {
                "success": True,
                "threats_found": len(threats),
                "threats": [
                    {
                        "type": threat.threat_type,
                        "severity": threat.severity,
                        "line": threat.line_number,
                        "message": threat.description
                    }
                    for threat in threats
                ],
                "summary": f"Found {len(threats)} security issues"
            }
            if any("data" in t.threat_type.lower() for t in threats):
                result["context_note"] = "See BUSINESS_CONTEXT.md - Privacy-First Principle"
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _check_compliance(self, action: str) -> Dict[str, Any]:
        """Check if action complies with policies.

        Args:
            action: Action to check

        Returns:
            Compliance check results
        """
        try:
            from projectmind.compliance import ActionRequest

            request = ActionRequest(
                action_type="security_check",
                action_data={"action": action}
            )

            policy_engine = self._get_policy_engine()
            result = policy_engine.validate(request)

            return {
                "action": action,
                "compliant": result.allowed,
                "reason": result.reason if not result.allowed else "Action allowed"
            }
        except Exception as e:
            return {
                "action": action,
                "error": str(e)
            }

    def _validate_action(self, action: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an action against policies.

        Args:
            action: Action type
            request: Action request data

        Returns:
            Validation results
        """
        try:
            from projectmind.compliance import ActionRequest

            ar = ActionRequest(
                action_type=action,
                action_data=request
            )

            policy_engine = self._get_policy_engine()
            result = policy_engine.validate(ar)

            self.add_memory({
                "type": "validation",
                "action": action,
                "allowed": result.allowed,
                "reason": result.reason
            })

            return {
                "action": action,
                "allowed": result.allowed,
                "reason": result.reason,
                "requires_explanation": not result.allowed
            }
        except Exception as e:
            return {
                "action": action,
                "error": str(e)
            }

    def _generate_security_report(self, code: str) -> Dict[str, Any]:
        """Generate comprehensive security report.

        Args:
            code: Source code

        Returns:
            Security report
        """
        threats = self.threat_detector.detect_threats(code)

        # Categorize threats
        by_severity = {}
        for threat in threats:
            severity = threat.severity
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(threat.threat_type)

        return {
            "total_threats": len(threats),
            "by_severity": by_severity,
            "threats": [
                {
                    "type": threat.threat_type,
                    "severity": threat.severity,
                    "description": threat.description
                }
                for threat in threats
            ],
            "recommendation": "Fix all high and critical severity issues"
        }
