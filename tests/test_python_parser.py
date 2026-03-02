"""Tests for Python Parser"""

import pytest
import tempfile
from pathlib import Path
from projectmind.core.python_parser import PythonParser, PythonFileAnalysis


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
\"\"\"Module docstring.\"\"\"

import os
from pathlib import Path
from typing import List, Dict

def simple_function():
    \"\"\"Simple function docstring.\"\"\"
    return 42

@decorator
async def async_function(x: int, y: str) -> Dict:
    \"\"\"Async function with decorators.\"\"\"
    pass

class MyClass(BaseClass):
    \"\"\"Class docstring.\"\"\"
    
    def __init__(self):
        self.value = 0
    
    def method_one(self, arg1):
        pass
    
    @property
    def prop(self):
        return self.value
""")
        f.flush()
        yield f.name
        try:
            Path(f.name).unlink()
        except (PermissionError, OSError):
            pass


def test_parser_analyzes_file(temp_python_file):
    """Test parser can analyze a file."""
    analysis = PythonParser.analyze_file(temp_python_file)
    assert not analysis.has_syntax_error
    assert analysis.file_path == temp_python_file


def test_parser_extracts_module_docstring(temp_python_file):
    """Test module docstring extraction."""
    analysis = PythonParser.analyze_file(temp_python_file)
    assert analysis.module_docstring == "Module docstring."


def test_parser_extracts_imports(temp_python_file):
    """Test import extraction."""
    analysis = PythonParser.analyze_file(temp_python_file)
    assert len(analysis.imports) >= 3

    modules = [imp.module for imp in analysis.imports]
    assert "os" in modules
    assert "pathlib" in modules


def test_parser_extracts_functions(temp_python_file):
    """Test function extraction."""
    analysis = PythonParser.analyze_file(temp_python_file)
    assert len(analysis.functions) >= 2

    func_names = [f.name for f in analysis.functions]
    assert "simple_function" in func_names
    assert "async_function" in func_names


def test_parser_detects_async(temp_python_file):
    """Test async function detection."""
    analysis = PythonParser.analyze_file(temp_python_file)
    async_funcs = [f for f in analysis.functions if f.is_async]
    assert len(async_funcs) > 0


def test_parser_extracts_classes(temp_python_file):
    """Test class extraction."""
    analysis = PythonParser.analyze_file(temp_python_file)
    assert len(analysis.classes) >= 1

    cls = analysis.classes[0]
    assert cls.name == "MyClass"
    assert "BaseClass" in cls.base_classes
    assert len(cls.methods) >= 2


def test_parser_handles_syntax_error():
    """Test parser handles syntax errors gracefully."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("this is not valid python syntax >>>")
        f.flush()

        analysis = PythonParser.analyze_file(f.name)
        assert analysis.has_syntax_error
        assert analysis.error_message

        try:
            Path(f.name).unlink()
        except (PermissionError, OSError):
            pass


def test_parser_handles_missing_file():
    """Test parser handles missing files."""
    analysis = PythonParser.analyze_file("/nonexistent/file.py")
    assert analysis.has_syntax_error
