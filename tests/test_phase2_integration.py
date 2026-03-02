"""Integration tests for Phase 2 with Phase 1 and Phase 5"""

import pytest
import tempfile
from pathlib import Path
from projectmind.core.scanner import RepoScanner
from projectmind.summarization import CodeSummarizer, SummaryType, DocumentationGenerator
from projectmind.security import ThreatDetector
from projectmind.compliance import PolicyEngine
from projectmind.core.context import ContextLoader


def test_summarize_project_code():
    """Test summarizing ProjectMind's own code."""
    scanner = RepoScanner("projectmind/core")
    scanner.scan()

    summarizer = CodeSummarizer()

    # Summarize scanner.py
    py_file = "projectmind/core/scanner.py"
    summary = summarizer.summarize_file(py_file, SummaryType.DETAILED)

    assert summary.metrics.functions > 0
    assert summary.metrics.classes > 0
    assert len(summary.dependencies) > 0
    assert summary.metrics.maintainability_index > 0


def test_summarize_with_threat_detection():
    """Test summarizing code and detecting threats."""
    risky_code = """
def unsafe_function(user_input):
    '''Process user input - unsafely.'''
    result = eval(user_input)
    password = "admin123"
    return result
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(risky_code)
        temp_file = f.name

    try:
        # Summarize
        summarizer = CodeSummarizer()
        summary = summarizer.summarize_code(risky_code, temp_file)

        # Detect threats
        detector = ThreatDetector()
        threats = detector.scan_code(risky_code, temp_file)

        # Should find both issues
        assert len(summary.elements) > 0  # Found function
        assert len(threats) > 0  # Found threats

    finally:
        Path(temp_file).unlink()


def test_policy_validation_before_summarization():
    """Test that policy validates before summarization."""
    context = ContextLoader.create_default()
    engine = PolicyEngine(context)

    # Create request to analyze file
    from projectmind.compliance import ActionRequest

    request = ActionRequest(
        agent_name="summarizer",
        action_type="analyze",
        target_file="src/utils.py",
        change_summary="Generate documentation",
    )

    # Should be allowed (analyze is safe)
    assert engine.validate_action(request)


def test_generate_documentation_from_scan():
    """Test generating docs from scanner output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create sample Python files
        src_dir = tmpdir / "src"
        src_dir.mkdir()

        (src_dir / "utils.py").write_text("""
def calculate(x, y):
    '''Calculate sum.'''
    return x + y

def multiply(x, y):
    '''Calculate product.'''
    return x * y
""")

        (src_dir / "helpers.py").write_text("""
class Helper:
    '''Helper class.'''
    
    def help(self):
        return True
""")

        # Scan directory
        scanner = RepoScanner(str(tmpdir))
        scanner.scan()

        # Summarize all Python files
        summarizer = CodeSummarizer()
        summaries = []

        for py_file in src_dir.glob("*.py"):
            summary = summarizer.summarize_file(str(py_file))
            summaries.append(summary)

        assert len(summaries) == 2

        # Generate API reference
        api_ref = DocumentationGenerator.generate_api_reference(summaries)
        assert "calculate" in api_ref
        assert "Helper" in api_ref


def test_summarization_respects_policy():
    """Test that summarization doesn't bypass policy."""
    context = ContextLoader.create_default()
    engine = PolicyEngine(context)

    # Try to validate change to critical file
    from projectmind.compliance import ActionRequest

    request = ActionRequest(
        agent_name="summarizer",
        action_type="suggest_changes",
        target_file="project_context.yaml",
    )

    # Should be denied (critical file)
    assert not engine.validate_action(request)


def test_complex_code_analysis():
    """Test analyzing complex code."""
    complex_code = """
class DataProcessor:
    '''Process data with multiple methods.'''
    
    def __init__(self):
        self.data = []
    
    def process_item(self, item):
        '''Process single item.
        
        Args:
            item: Data to process
        
        Returns:
            Processed result
        '''
        if item is None:
            return None
        
        if isinstance(item, str):
            return item.upper()
        
        if isinstance(item, int):
            return item * 2
        
        return item
    
    def process_batch(self, items):
        '''Process multiple items.'''
        return [self.process_item(i) for i in items]

import json
import os
from pathlib import Path
"""

    summarizer = CodeSummarizer()
    summary = summarizer.summarize_code(complex_code)

    assert summary.metrics.classes == 1
    # __init__, process_item, process_batch = 3 functions total
    assert summary.metrics.functions == 3
    assert len(summary.dependencies) >= 3
    assert summary.metrics.cyclomatic_complexity > 1
    assert "process_batch" in [e.name for e in summary.elements]
