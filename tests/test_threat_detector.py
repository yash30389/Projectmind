"""Tests for Threat Detection"""

import pytest
from projectmind.security.threat_detector import (
    ThreatDetector,
    ThreatSeverity,
)


@pytest.fixture
def detector():
    """Create threat detector."""
    return ThreatDetector()


def test_detects_eval_usage(detector):
    """Test detection of eval() usage."""
    code = """
import os
result = eval(user_input)
"""

    threats = detector.scan_code(code, "test.py")

    assert len(threats) > 0
    assert any("eval" in t.description.lower() for t in threats)


def test_detects_hardcoded_password(detector):
    """Test detection of hardcoded passwords."""
    code = """
password = "super_secret_123"
db.connect(password=password)
"""

    threats = detector.scan_code(code, "config.py")

    assert len(threats) > 0
    assert any("password" in t.description.lower() for t in threats)


def test_detects_hardcoded_api_key(detector):
    """Test detection of hardcoded API keys."""
    code = """
api_key = "sk_live_1234567890abcdef"
requests.get(f"https://api.example.com?key={api_key}")
"""

    threats = detector.scan_code(code, "api.py")

    assert len(threats) > 0


def test_detects_sql_injection_risk(detector):
    """Test detection of SQL injection."""
    code = """
query = "SELECT * FROM users WHERE id = " + str(user_id)
result = db.execute(query)
"""

    threats = detector.scan_code(code, "db.py")

    assert len(threats) > 0
    assert any("injection" in t.description.lower() for t in threats)


def test_detects_os_system_usage(detector):
    """Test detection of os.system()."""
    code = """
os.system(f"rm -rf {filename}")
"""

    threats = detector.scan_code(code, "cleanup.py")

    assert len(threats) > 0


def test_safe_code_no_threats(detector):
    """Test that safe code has no threats."""
    code = """
def safe_function(x):
    '''A safe function.'''
    return x * 2

result = safe_function(42)
"""

    threats = detector.scan_code(code, "safe.py")

    assert len(threats) == 0


def test_threat_severity_levels(detector):
    """Test threat severity classification."""
    code_critical = """
eval(user_input)
password = "secret123"
"""

    threats = detector.scan_code(code_critical, "test.py")

    critical_threats = [t for t in threats if t.severity == ThreatSeverity.CRITICAL]
    assert len(critical_threats) >= 1


def test_threat_summary(detector):
    """Test threat summary generation."""
    code = """
eval(x)
api_key = "key123"
query = "SELECT * FROM users WHERE id = " + str(uid)
"""

    threats = detector.scan_code(code, "test.py")

    summary = detector.get_threat_summary(threats)

    assert summary["total"] >= 2
    assert "critical" in summary
    assert "by_severity" in summary
    assert "by_type" in summary


def test_scan_suggestions(detector):
    """Test scanning AI suggestions."""
    suggestions = [
        "eval(user_input)",
        "password = 'secret'",
        "safe_code = x * 2",
    ]

    threats = detector.scan_suggestions(suggestions)

    assert len(threats) > 0
    assert any("eval" in t.description.lower() for t in threats)
