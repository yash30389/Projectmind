"""Tests for Audit Logging"""

import pytest
import tempfile
import json
from pathlib import Path
from projectmind.audit.audit_log import AuditLog, AuditEntry


@pytest.fixture
def temp_audit_dir():
    """Create temporary audit directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_audit_log_creates_entry(temp_audit_dir):
    """Test creating audit log entry."""
    audit = AuditLog(temp_audit_dir)

    entry = audit.log_action(
        agent="coding_agent",
        action="suggest",
        target="src/utils.py",
        status="pending",
        reason="User requested refactoring",
    )

    assert entry.agent == "coding_agent"
    assert entry.action == "suggest"
    assert entry.status == "pending"


def test_audit_log_persists_to_file(temp_audit_dir):
    """Test that entries are persisted."""
    audit = AuditLog(temp_audit_dir)

    audit.log_action(
        agent="agent1",
        action="validate",
        target="file1.py",
        status="approved",
    )

    audit.log_action(
        agent="agent2",
        action="scan",
        target="file2.py",
        status="denied",
    )

    # Create new instance
    audit2 = AuditLog(temp_audit_dir)

    # Should load existing entries
    assert len(audit2.entries) == 2
    assert audit2.entries[0].agent == "agent1"
    assert audit2.entries[1].agent == "agent2"


def test_audit_log_filtering(temp_audit_dir):
    """Test filtering entries."""
    audit = AuditLog(temp_audit_dir)

    for i in range(5):
        audit.log_action(
            agent="agent_a",
            action="action",
            target=f"file{i}.py",
            status="approved" if i % 2 == 0 else "denied",
        )

    audit.log_action(
        agent="agent_b",
        action="action",
        target="file_b.py",
        status="approved",
    )

    # Filter by agent
    agent_a_entries = audit.get_entries(agent="agent_a")
    assert len(agent_a_entries) == 5

    agent_b_entries = audit.get_entries(agent="agent_b")
    assert len(agent_b_entries) == 1

    # Filter by status
    approved = audit.get_entries(status="approved")
    assert len(approved) >= 3


def test_audit_summary(temp_audit_dir):
    """Test audit summary."""
    audit = AuditLog(temp_audit_dir)

    audit.log_action("agent1", "action", "file1.py", "approved")
    audit.log_action("agent1", "action", "file2.py", "denied")
    audit.log_action("agent2", "action", "file3.py", "approved")

    summary = audit.get_summary()

    assert summary["total_entries"] == 3
    assert summary["by_agent"]["agent1"] == 2
    assert summary["by_agent"]["agent2"] == 1
    assert summary["by_status"]["approved"] == 2
    assert summary["by_status"]["denied"] == 1


def test_audit_export_json(temp_audit_dir):
    """Test exporting audit log as JSON."""
    audit = AuditLog(temp_audit_dir)

    audit.log_action("agent1", "action", "file1.py", "approved", "Good change")
    audit.log_action("agent2", "action", "file2.py", "denied", "Security risk")

    output_file = Path(temp_audit_dir) / "report.json"
    audit.export_report(str(output_file), format="json")

    assert output_file.exists()

    with open(output_file) as f:
        data = json.load(f)

    assert "summary" in data
    assert "entries" in data
    assert len(data["entries"]) == 2


def test_audit_export_markdown(temp_audit_dir):
    """Test exporting audit log as markdown."""
    audit = AuditLog(temp_audit_dir)

    audit.log_action("agent1", "action", "file1.py", "approved")
    audit.log_action("agent2", "action", "file2.py", "denied")

    output_file = Path(temp_audit_dir) / "report.md"
    audit.export_report(str(output_file), format="markdown")

    assert output_file.exists()

    with open(output_file) as f:
        content = f.read()

    assert "Audit Report" in content
    assert "agent1" in content
    assert "agent2" in content


def test_audit_chain_integrity(temp_audit_dir):
    """Test hash chain integrity."""
    audit = AuditLog(temp_audit_dir)

    audit.log_action("agent1", "action", "file1.py", "approved")
    audit.log_action("agent2", "action", "file2.py", "denied")

    # Verify chain is intact
    assert audit.verify_chain_integrity()
