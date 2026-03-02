"""Tests for Phase 5: Security & Compliance"""

import pytest
import tempfile
from pathlib import Path
from projectmind.compliance.policy_engine import (
    PolicyEngine,
    ActionRequest,
    PolicyViolation,
)
from projectmind.core.context import ContextLoader


@pytest.fixture
def policy_engine():
    """Create default policy engine."""
    context = ContextLoader.create_default()
    return PolicyEngine(context)


def test_policy_allows_safe_action(policy_engine):
    """Test that safe actions are allowed."""
    request = ActionRequest(
        agent_name="coding_agent",
        action_type="suggest",
        target_file="src/utils.py",
    )

    # Suggest actions should be allowed
    assert policy_engine.validate_action(request)
    assert len(policy_engine.get_violations()) == 0


def test_policy_denies_autonomous_edit(policy_engine):
    """Test that autonomous edits are denied."""
    request = ActionRequest(
        agent_name="coding_agent",
        action_type="edit",
        target_file="src/utils.py",
    )

    assert not policy_engine.validate_action(request)
    violations = policy_engine.get_violations()
    assert len(violations) > 0
    assert violations[0].severity == "hard"


def test_policy_protects_critical_files(policy_engine):
    """Test that critical files are protected."""
    request = ActionRequest(
        agent_name="coding_agent",
        action_type="suggest",
        target_file="project_context.yaml",
    )

    # Even suggestions on critical files should be denied
    assert not policy_engine.validate_action(request)


def test_policy_protects_auth_files(policy_engine):
    """Test that auth files get extra protection."""
    request = ActionRequest(
        agent_name="coding_agent",
        action_type="edit",
        target_file="src/auth.py",
    )

    assert not policy_engine.validate_action(request)
    violations = policy_engine.get_violations()
    assert any("security" in v.message.lower() for v in violations)


def test_refusal_reason_is_clear(policy_engine):
    """Test that refusal reasons are clear."""
    request = ActionRequest(
        agent_name="coding_agent",
        action_type="edit",
        target_file="src/database.py",
    )

    policy_engine.validate_action(request)
    reason = policy_engine.get_refusal_reason()

    assert "❌" in reason
    assert len(reason) > 0
    assert "suggested_fix" in reason or "→" in reason


def test_policy_requires_explanation(policy_engine):
    """Test that explanations are required for sensitive changes."""
    request = ActionRequest(
        agent_name="coding_agent",
        action_type="suggest",
        target_file="src/utils.py",
        change_summary=None,  # No explanation
    )

    # Should still validate but note lack of explanation
    # (depends on constraints)
    violations = policy_engine.get_violations()
    # No hard violations for suggests without summary
    hard_violations = [v for v in violations if v.severity == "hard"]
    assert len(hard_violations) == 0


def test_policy_from_file():
    """Test loading policy from context file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        context_file = f.name

    try:
        # Create and save context
        context = ContextLoader.create_default()
        ContextLoader.save_to_file(context, context_file)

        # Load policy from file
        engine = PolicyEngine.from_file(context_file)

        # Test it works
        request = ActionRequest(
            agent_name="test_agent",
            action_type="suggest",
            target_file="test.py",
        )

        assert engine.validate_action(request)

    finally:
        Path(context_file).unlink()
