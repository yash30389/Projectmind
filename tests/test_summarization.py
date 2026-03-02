"""Tests for Phase 2: AI Summarization"""

import pytest
from projectmind.summarization import (
    CodeSummarizer,
    SummaryType,
    DocumentationGenerator,
)


@pytest.fixture
def summarizer():
    """Create code summarizer."""
    return CodeSummarizer()


def test_summarize_simple_function(summarizer):
    """Test summarizing a simple function."""
    code = """
def add(a, b):
    '''Add two numbers.'''
    return a + b
"""

    summary = summarizer.summarize_code(code, "math.py")

    assert summary.brief
    assert summary.metrics.functions == 1
    assert summary.metrics.classes == 0


def test_summarize_class(summarizer):
    """Test summarizing a class."""
    code = """
class Calculator:
    '''A simple calculator.'''
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
"""

    summary = summarizer.summarize_code(code, "calc.py")

    assert summary.metrics.classes == 1
    assert summary.metrics.functions == 2
    assert any("Calculator" in e.name for e in summary.elements)


def test_extract_docstrings(summarizer):
    """Test extracting docstrings."""
    code = """
def documented_function(x):
    '''This function has documentation.
    
    Args:
        x: Input value
    
    Returns:
        Doubled value
    '''
    return x * 2

def undocumented_function(y):
    return y + 1
"""

    summary = summarizer.summarize_code(code)

    documented = [e for e in summary.elements if e.docstring]
    assert len(documented) >= 1


def test_calculate_metrics(summarizer):
    """Test metric calculation."""
    code = """# This is a comment
def function1():
    pass

def function2():
    pass

# Another comment

class MyClass:
    pass
"""

    summary = summarizer.summarize_code(code)

    assert summary.metrics.functions == 2
    assert summary.metrics.classes == 1
    assert summary.metrics.comment_lines >= 2
    assert summary.metrics.code_lines > 0


def test_detect_issues(summarizer):
    """Test issue detection."""
    code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 100:
                if x > 1000:
                    return "big"
            return "medium"
        return "small"
    return "negative"
"""

    summary = summarizer.summarize_code(code)

    assert len(summary.recommendations) > 0


def test_maintainability_score(summarizer):
    """Test maintainability calculation."""
    well_documented_code = """
def well_documented_function(x):
    '''This function is well documented.'''
    # Comment explaining the logic
    return x * 2
"""

    summary = summarizer.summarize_code(well_documented_code)
    assert summary.metrics.maintainability_index >= 50


def test_extract_dependencies(summarizer):
    """Test extracting dependencies."""
    code = """
import os
import sys
from pathlib import Path
from typing import List
import json
"""

    summary = summarizer.summarize_code(code)

    assert "os" in summary.dependencies
    assert "sys" in summary.dependencies
    assert "pathlib" in summary.dependencies
    assert "typing" in summary.dependencies
    assert "json" in summary.dependencies


def test_syntax_error_handling(summarizer):
    """Test handling of syntax errors."""
    code = "def broken(: pass"

    summary = summarizer.summarize_code(code)

    assert len(summary.warnings) > 0
    assert "Syntax error" in summary.warnings[0]


def test_complexity_calculation(summarizer):
    """Test cyclomatic complexity calculation."""
    code = """
def simple():
    return 1

def complex_function(x, y):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x
    else:
        if y > 0:
            return y
        else:
            return 0
"""

    summary = summarizer.summarize_code(code)
    assert summary.metrics.cyclomatic_complexity > 1


def test_documentation_generation(summarizer):
    """Test generating documentation."""
    code = """
def calculate(x, y):
    '''Calculate sum of two numbers.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        Sum of x and y
    '''
    return x + y
"""

    summary = summarizer.summarize_code(code, "math.py", SummaryType.DETAILED)
    doc = DocumentationGenerator.generate_markdown(summary)

    assert "math.py" in doc
    assert "calculate" in doc
    assert "Metrics" in doc
