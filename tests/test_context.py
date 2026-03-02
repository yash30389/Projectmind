"""Tests for Context Management"""

import pytest
import tempfile
from pathlib import Path
from projectmind.core.context import (
    ContextLoader,
    ProjectContext,
    ProjectConstraints,
    ProjectVision,
)


def test_create_default_context():
    """Test creating default context."""
    context = ContextLoader.create_default()

    assert context.vision.name == "ProjectMind"
    assert context.constraints.no_autonomous_changes is True
    assert context.constraints.must_explain_reasoning is True


def test_save_and_load_context():
    """Test saving and loading context."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        context_file = f.name

    try:
        # Create and save
        original = ContextLoader.create_default()
        ContextLoader.save_to_file(original, context_file)

        # Load
        loaded = ContextLoader.load_from_file(context_file)

        # Verify
        assert loaded.vision.name == original.vision.name
        assert loaded.constraints.no_autonomous_changes == original.constraints.no_autonomous_changes
    finally:
        Path(context_file).unlink()


def test_context_to_dict():
    """Test context serialization."""
    context = ContextLoader.create_default()
    data = context.to_dict()

    assert "vision" in data
    assert "constraints" in data
    assert "tech_stack" in data


def test_load_missing_context():
    """Test loading non-existent context file."""
    with pytest.raises(FileNotFoundError):
        ContextLoader.load_from_file("/nonexistent/context.yaml")
