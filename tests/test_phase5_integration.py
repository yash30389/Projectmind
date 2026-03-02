"""Integration tests for Phase 5 with Phase 1"""

import pytest
import tempfile
from pathlib import Path
from projectmind.core.context import ContextLoader
from projectmind.core.scanner import RepoScanner
from projectmind.core.python_parser import PythonParser
from projectmind.compliance import PolicyEngine, ActionRequest
from projectmind.audit import AuditLog
from projectmind.security import ThreatDetector
from projectmind.compliance import ComplianceReporter, ComplianceFramework


def test_complete_workflow():
    """Test complete Phase 1 + Phase 5 workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create test project structure
        src_dir = tmpdir / "src"
        src_dir.mkdir()

        # Write a Python file with some code
        test_file = src_dir / "utils.py"
        test_file.write_text("""
def safe_function(x):
    '''A safe function.'''
    return x * 2

def risky_function(user_input):
    '''A risky function.'''
    result = eval(user_input)
    return result
""")

        # Phase 1: Scan repository
        scanner = RepoScanner(str(tmpdir))
        scanner.scan()
        metadata = scanner.files

        assert len(metadata) > 0
        assert any("utils.py" in f.path for f in metadata)

        # Phase 1: Parse Python
        parser = PythonParser()
        python_files = [f for f in metadata if f.path.endswith(".py")]
        assert len(python_files) > 0

        # Phase 5: Create policy engine
        context = ContextLoader.create_default()
        engine = PolicyEngine(context)

        # Phase 5: Validate action
        request = ActionRequest(
            agent_name="test_agent",
            action_type="suggest",
            target_file="src/utils.py",
            change_summary="Add documentation",
        )

        assert engine.validate_action(request)

        # Phase 5: Detect threats
        detector = ThreatDetector()
        code = test_file.read_text()
        threats = detector.scan_code(code, "src/utils.py")

        # Should detect eval() as threat
        assert len(threats) > 0
        assert any("eval" in t.description.lower() for t in threats)

        # Phase 5: Log action
        audit = AuditLog(str(tmpdir / ".audit"))
        entry = audit.log_action(
            agent="test_agent",
            action="suggestion",
            target="src/utils.py",
            status="approved",
        )

        assert entry.agent == "test_agent"
        assert entry.target == "src/utils.py"


def test_policy_threat_detector_integration():
    """Test policy engine with threat detector."""
    context = ContextLoader.create_default()
    engine = PolicyEngine(context)
    detector = ThreatDetector()

    risky_code = """
password = "admin123"
db.connect(password)
"""

    # Detect threats
    threats = detector.scan_code(risky_code, "config.py")
    assert len(threats) > 0

    # Policy should deny changes to potentially compromised files
    request = ActionRequest(
        agent_name="agent",
        action_type="edit",
        target_file="config.py",
    )

    assert not engine.validate_action(request)


def test_audit_compliance_integration():
    """Test audit logging with compliance reporting."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit = AuditLog(tmpdir)

        # Log various actions
        audit.log_action("agent1", "validate", "file1.py", "approved")
        audit.log_action("agent1", "scan", "file2.py", "approved")
        audit.log_action("agent2", "suggest", "file3.py", "approved")

        # Generate compliance report
        reporter = ComplianceReporter()

        # Audit log should be considered evidence
        summary = reporter.get_summary()

        assert "internal" in summary
        assert summary["internal"]["score"] > 0


def test_multi_framework_compliance():
    """Test multiple compliance frameworks."""
    reporter = ComplianceReporter()

    frameworks = [
        ComplianceFramework.INTERNAL,
        ComplianceFramework.EU_AI_ACT,
        ComplianceFramework.SOC2,
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "report.json"

        reporter.generate_report(frameworks, str(output_file), format="json")

        assert output_file.exists()

        # Verify report has all frameworks
        import json
        with open(output_file) as f:
            data = json.load(f)

        assert "eu_ai_act" in data["requirements"]
        assert "soc2" in data["requirements"]
        assert "internal" in data["requirements"]
