"""
Threat Detection: Proactive security scanning.
"""

import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ThreatSeverity(Enum):
    """Threat severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Threat:
    """Detected security threat."""

    type: str  # "injection", "hardcoded_secret", "unsafe_function", etc.
    severity: ThreatSeverity
    location: str  # File and line
    description: str
    recommendation: str


class ThreatDetector:
    """Proactive threat detection."""

    # Dangerous functions and patterns
    UNSAFE_PATTERNS = {
        r"eval\s*\(": ("eval() usage", ThreatSeverity.CRITICAL),
        r"exec\s*\(": ("exec() usage", ThreatSeverity.CRITICAL),
        r"pickle\.load": ("unsafe pickle", ThreatSeverity.HIGH),
        r"subprocess\.call\(['\"].*shell=True": ("shell injection risk", ThreatSeverity.HIGH),
        r"os\.system": ("os.system usage", ThreatSeverity.HIGH),
        r"SELECT.*FROM.*WHERE.*\+|f['\"].*{.*}.*['\"]": ("SQL injection risk", ThreatSeverity.HIGH),
    }

    # Hardcoded secret patterns
    SECRET_PATTERNS = {
        r"password\s*=\s*['\"][^'\"]+['\"]": ("Hardcoded password", ThreatSeverity.CRITICAL),
        r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]": ("Hardcoded API key", ThreatSeverity.CRITICAL),
        r"secret\s*=\s*['\"][^'\"]+['\"]": ("Hardcoded secret", ThreatSeverity.CRITICAL),
        r"token\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]": ("Hardcoded token", ThreatSeverity.HIGH),
    }

    # Risky operations
    RISKY_OPERATIONS = {
        "*.pop()": "Unsafe list operation",
        "*.split(None)": "Unsafe string split",
        "*.format()": "String format injection risk",
    }

    def scan_code(self, code: str, file_path: str) -> List[Threat]:
        """Scan code for threats."""
        threats = []

        lines = code.split("\n")
        for line_num, line in enumerate(lines, 1):
            threats.extend(self._scan_line(line, file_path, line_num))

        return threats

    def scan_suggestions(
        self, suggestions: List[str], context: Optional[Dict[str, Any]] = None
    ) -> List[Threat]:
        """Scan AI suggestions for threats."""
        threats = []

        for i, suggestion in enumerate(suggestions):
            # Scan each suggestion for threats
            suggestion_threats = self.scan_code(suggestion, f"suggestion_{i}")
            threats.extend(suggestion_threats)

        return threats

    def _scan_line(self, line: str, file_path: str, line_num: int) -> List[Threat]:
        """Scan single line for threats."""
        threats = []

        # Check unsafe patterns
        for pattern, (description, severity) in self.UNSAFE_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                threats.append(
                    Threat(
                        type="unsafe_function",
                        severity=severity,
                        location=f"{file_path}:{line_num}",
                        description=f"Found: {description}",
                        recommendation="Avoid using this function. Use safer alternatives.",
                    )
                )

        # Check hardcoded secrets
        for pattern, (description, severity) in self.SECRET_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                threats.append(
                    Threat(
                        type="hardcoded_secret",
                        severity=severity,
                        location=f"{file_path}:{line_num}",
                        description=description,
                        recommendation="Move secrets to environment variables or secure vaults.",
                    )
                )

        # Check for common injection vectors
        if self._has_injection_risk(line):
            threats.append(
                Threat(
                    type="injection_risk",
                    severity=ThreatSeverity.HIGH,
                    location=f"{file_path}:{line_num}",
                    description="Possible injection vulnerability",
                    recommendation="Use parameterized queries or escape user input.",
                )
            )

        return threats

    def _has_injection_risk(self, line: str) -> bool:
        """Check for common injection patterns."""
        injection_patterns = [
            r"\+\s*['\"]",  # String concatenation with variable
            r"f['\"].*{.*}.*['\"]",  # f-string with variable
            r"format\(.*\)",  # .format() with variable
        ]

        for pattern in injection_patterns:
            if re.search(pattern, line):
                return True

        return False

    def get_threat_summary(self, threats: List[Threat]) -> Dict[str, Any]:
        """Summarize threats by severity."""
        by_severity = {}
        by_type = {}

        for threat in threats:
            severity = threat.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_type[threat.type] = by_type.get(threat.type, 0) + 1

        critical = len([t for t in threats if t.severity == ThreatSeverity.CRITICAL])
        high = len([t for t in threats if t.severity == ThreatSeverity.HIGH])

        return {
            "total": len(threats),
            "critical": critical,
            "high": high,
            "by_severity": by_severity,
            "by_type": by_type,
            "safe": critical == 0 and high == 0,
        }
