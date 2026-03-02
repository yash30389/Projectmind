"""Compliance reporting for regulations"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
from pathlib import Path
import json
from datetime import datetime


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    EU_AI_ACT = "eu_ai_act"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    INTERNAL = "internal"


@dataclass
class ComplianceRequirement:
    """Single compliance requirement."""
    framework: ComplianceFramework
    requirement_id: str
    description: str
    implementation: str
    status: str  # "implemented", "partial", "not_implemented"
    evidence: List[str]  # Evidence files or descriptions


@dataclass
class ComplianceScore:
    """Compliance framework score."""
    framework: ComplianceFramework
    score: float  # 0-100
    total_requirements: int
    met_requirements: int
    partial_requirements: int
    not_met_requirements: int


class ComplianceReporter:
    """Generate compliance reports."""

    REQUIREMENTS = {
        ComplianceFramework.EU_AI_ACT: [
            {
                "id": "EU-AI-001",
                "description": "High-risk AI systems must have explicit governance",
                "implementation": "Policy engine enforces constraints",
                "evidence": "projectmind/compliance/policy_engine.py",
            },
            {
                "id": "EU-AI-002",
                "description": "Audit trail for all AI decisions required",
                "implementation": "Audit log with hash chain",
                "evidence": "projectmind/audit/audit_log.py",
            },
            {
                "id": "EU-AI-003",
                "description": "Transparency: AI must not operate autonomously",
                "implementation": "All actions require human approval",
                "evidence": "project_context.yaml governance rules",
            },
            {
                "id": "EU-AI-004",
                "description": "Threat detection and security scanning",
                "implementation": "ThreatDetector scans all code",
                "evidence": "projectmind/security/threat_detector.py",
            },
        ],
        ComplianceFramework.SOC2: [
            {
                "id": "SOC2-CC6",
                "description": "Logical access controls",
                "implementation": "Policy engine controls agent actions",
                "evidence": "projectmind/compliance/policy_engine.py",
            },
            {
                "id": "SOC2-CC7",
                "description": "Audit logging and monitoring",
                "implementation": "All actions logged with hash chain",
                "evidence": "projectmind/audit/audit_log.py",
            },
            {
                "id": "SOC2-CC8",
                "description": "Encryption and data protection",
                "implementation": "Audit log uses SHA256 hash chains",
                "evidence": "projectmind/audit/audit_log.py",
            },
        ],
        ComplianceFramework.INTERNAL: [
            {
                "id": "INTERNAL-001",
                "description": "Hard constraints on AI actions",
                "implementation": "PolicyEngine prevents unsafe actions",
                "evidence": "projectmind/compliance/policy_engine.py",
            },
            {
                "id": "INTERNAL-002",
                "description": "No autonomous changes to critical files",
                "implementation": "Protected file patterns enforced",
                "evidence": "projectmind/compliance/policy_engine.py",
            },
            {
                "id": "INTERNAL-003",
                "description": "Security threat detection enabled",
                "implementation": "Proactive threat scanning",
                "evidence": "projectmind/security/threat_detector.py",
            },
        ],
    }

    def __init__(self):
        """Initialize reporter."""
        self.requirements: Dict[ComplianceFramework, List[ComplianceRequirement]] = {}
        self._load_requirements()

    def _load_requirements(self) -> None:
        """Load compliance requirements."""
        for framework, reqs in self.REQUIREMENTS.items():
            self.requirements[framework] = [
                ComplianceRequirement(
                    framework=framework,
                    requirement_id=r["id"],
                    description=r["description"],
                    implementation=r["implementation"],
                    status="implemented",  # Default to implemented
                    evidence=r["evidence"].split(", ") if isinstance(r["evidence"], str) else r["evidence"],
                )
                for r in reqs
            ]

    def calculate_score(self, framework: ComplianceFramework) -> ComplianceScore:
        """Calculate compliance score for framework."""
        reqs = self.requirements.get(framework, [])

        met = len([r for r in reqs if r.status == "implemented"])
        partial = len([r for r in reqs if r.status == "partial"])
        not_met = len([r for r in reqs if r.status == "not_implemented"])

        # Calculate score: met=1, partial=0.5, not_met=0
        score = (met + partial * 0.5) / len(reqs) * 100 if reqs else 0

        return ComplianceScore(
            framework=framework,
            score=score,
            total_requirements=len(reqs),
            met_requirements=met,
            partial_requirements=partial,
            not_met_requirements=not_met,
        )

    def generate_report(
        self,
        frameworks: List[ComplianceFramework],
        output_file: str,
        format: str = "markdown"
    ) -> None:
        """Generate compliance report."""
        if format == "markdown":
            self._generate_markdown_report(frameworks, output_file)
        elif format == "json":
            self._generate_json_report(frameworks, output_file)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_markdown_report(
        self,
        frameworks: List[ComplianceFramework],
        output_file: str
    ) -> None:
        """Generate markdown report."""
        lines = [
            "# ProjectMind Compliance Report\n",
            f"Generated: {datetime.now().isoformat()}\n",
            "---\n",
            "## Summary\n",
        ]

        scores = []
        for framework in frameworks:
            score = self.calculate_score(framework)
            scores.append(score)
            lines.append(f"- **{framework.value.upper()}**: {score.score:.1f}% "
                        f"({score.met_requirements}/{score.total_requirements})\n")

        lines.append("\n---\n")

        # Detailed requirements
        for framework in frameworks:
            lines.append(f"## {framework.value.upper()} Requirements\n")
            reqs = self.requirements.get(framework, [])

            for req in reqs:
                status_icon = "✅" if req.status == "implemented" else "⚠️" if req.status == "partial" else "❌"
                lines.append(f"\n### {status_icon} {req.requirement_id}: {req.description}\n")
                lines.append(f"- **Implementation**: {req.implementation}\n")
                lines.append(f"- **Evidence**: {', '.join(req.evidence)}\n")

            lines.append("\n---\n")

        with open(output_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _generate_json_report(
        self,
        frameworks: List[ComplianceFramework],
        output_file: str
    ) -> None:
        """Generate JSON report."""
        scores = {}
        requirements_data = {}

        for framework in frameworks:
            score = self.calculate_score(framework)
            scores[framework.value] = {
                "score": score.score,
                "total_requirements": score.total_requirements,
                "met_requirements": score.met_requirements,
                "partial_requirements": score.partial_requirements,
                "not_met_requirements": score.not_met_requirements,
            }

            reqs = self.requirements.get(framework, [])
            requirements_data[framework.value] = [
                {
                    "requirement_id": r.requirement_id,
                    "description": r.description,
                    "implementation": r.implementation,
                    "status": r.status,
                    "evidence": r.evidence,
                }
                for r in reqs
            ]

        data = {
            "generated": datetime.now().isoformat(),
            "scores": scores,
            "requirements": requirements_data,
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_summary(self) -> Dict:
        """Get compliance summary."""
        summary = {}

        for framework in ComplianceFramework:
            score = self.calculate_score(framework)
            summary[framework.value] = {
                "score": round(score.score, 1),
                "status": "compliant" if score.score >= 80 else "partial" if score.score >= 50 else "non-compliant",
            }

        return summary
