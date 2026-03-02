"""
Python-specific parser for extracting functions, classes, and imports.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class PythonFunction:
    """Metadata about a Python function."""

    name: str
    line_number: int
    end_line_number: int
    decorators: List[str]
    parameters: List[str]
    docstring: Optional[str] = None
    is_async: bool = False


@dataclass
class PythonClass:
    """Metadata about a Python class."""

    name: str
    line_number: int
    end_line_number: int
    base_classes: List[str]
    methods: List[PythonFunction]
    docstring: Optional[str] = None


@dataclass
class PythonImport:
    """Metadata about a Python import."""

    module: str
    alias: Optional[str] = None
    line_number: int = 0
    is_from: bool = False
    imported_names: List[str] = None

    def __post_init__(self):
        if self.imported_names is None:
            self.imported_names = []


@dataclass
class PythonFileAnalysis:
    """Complete analysis of a Python file."""

    file_path: str
    functions: List[PythonFunction]
    classes: List[PythonClass]
    imports: List[PythonImport]
    module_docstring: Optional[str] = None
    has_syntax_error: bool = False
    error_message: Optional[str] = None


class PythonParser:
    """Parse Python files without running them."""

    @staticmethod
    def analyze_file(file_path: str) -> PythonFileAnalysis:
        """
        Analyze a Python file and extract all metadata.
        Returns analysis even if file has syntax errors.
        """
        absolute_path = Path(file_path).resolve()

        if not absolute_path.exists():
            return PythonFileAnalysis(
                file_path=file_path,
                functions=[],
                classes=[],
                imports=[],
                has_syntax_error=True,
                error_message=f"File does not exist: {file_path}",
            )

        try:
            with open(absolute_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except Exception as e:
            return PythonFileAnalysis(
                file_path=file_path,
                functions=[],
                classes=[],
                imports=[],
                has_syntax_error=True,
                error_message=f"Failed to read file: {e}",
            )

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return PythonFileAnalysis(
                file_path=file_path,
                functions=[],
                classes=[],
                imports=[],
                has_syntax_error=True,
                error_message=f"Syntax error: {e}",
            )

        # Extract module docstring
        module_docstring = ast.get_docstring(tree)

        # Extract top-level imports, functions, classes
        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(PythonParser._parse_import(node))
            elif isinstance(node, ast.ImportFrom):
                imports.extend(PythonParser._parse_import_from(node))
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                if isinstance(node, ast.Module) or not any(
                    isinstance(parent, (ast.ClassDef,)) for parent in ast.walk(tree)
                ):
                    func = PythonParser._parse_function(node)
                    if func:
                        functions.append(func)
            elif isinstance(node, ast.ClassDef):
                cls = PythonParser._parse_class(node)
                if cls:
                    classes.append(cls)

        # Re-parse to get proper nesting
        functions = []
        classes = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = PythonParser._parse_function(node)
                if func:
                    functions.append(func)
            elif isinstance(node, ast.ClassDef):
                cls = PythonParser._parse_class(node)
                if cls:
                    classes.append(cls)

        return PythonFileAnalysis(
            file_path=file_path,
            functions=functions,
            classes=classes,
            imports=imports,
            module_docstring=module_docstring,
            has_syntax_error=False,
        )

    @staticmethod
    def _parse_import(node: ast.Import) -> List[PythonImport]:
        """Parse import statement."""
        imports = []
        for alias in node.names:
            imports.append(
                PythonImport(
                    module=alias.name,
                    alias=alias.asname,
                    line_number=node.lineno,
                    is_from=False,
                )
            )
        return imports

    @staticmethod
    def _parse_import_from(node: ast.ImportFrom) -> List[PythonImport]:
        """Parse from X import Y statement."""
        module = node.module or ""
        if node.level:
            module = "." * node.level + module

        imported_names = [alias.name for alias in node.names]

        return [
            PythonImport(
                module=module,
                line_number=node.lineno,
                is_from=True,
                imported_names=imported_names,
            )
        ]

    @staticmethod
    def _parse_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Optional[
        PythonFunction
    ]:
        """Parse function definition."""
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                decorators.append(dec.func.id)

        parameters = []
        for arg in node.args.args:
            parameters.append(arg.arg)

        docstring = ast.get_docstring(node)

        return PythonFunction(
            name=node.name,
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            decorators=decorators,
            parameters=parameters,
            docstring=docstring,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )

    @staticmethod
    def _parse_class(node: ast.ClassDef) -> Optional[PythonClass]:
        """Parse class definition."""
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(PythonParser._unparse_name(base))

        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = PythonParser._parse_function(item)
                if method:
                    methods.append(method)

        docstring = ast.get_docstring(node)

        return PythonClass(
            name=node.name,
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            base_classes=base_classes,
            methods=methods,
            docstring=docstring,
        )

    @staticmethod
    def _unparse_name(node) -> str:
        """Unparse an AST node to get its string representation."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{PythonParser._unparse_name(node.value)}.{node.attr}"
        return ""
