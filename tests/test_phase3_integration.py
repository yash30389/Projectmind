"""Integration tests for Phase 3 with Phases 1, 2, 5"""

import pytest
import tempfile
from pathlib import Path
from projectmind.core.scanner import RepoScanner
from projectmind.summarization import CodeSummarizer
from projectmind.embeddings import SemanticSearch, EmbeddingGenerator, VectorStore
from projectmind.compliance import PolicyEngine
from projectmind.core.context import ContextLoader


def test_index_scanned_files():
    """Test indexing files found by scanner."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create test files
        src_dir = tmpdir / "src"
        src_dir.mkdir()

        (src_dir / "utils.py").write_text("""
def add(x, y):
    '''Add two numbers.'''
    return x + y

def multiply(x, y):
    '''Multiply two numbers.'''
    return x * y
""")

        (src_dir / "helpers.py").write_text("""
class Helper:
    '''Helper class.'''
    
    def help(self):
        return True
""")

        # Scan
        scanner = RepoScanner(str(tmpdir))
        scanner.scan()

        # Summarize and index
        summarizer = CodeSummarizer()
        generator = EmbeddingGenerator()
        store = VectorStore()

        py_files = list(src_dir.glob("*.py"))
        for py_file in py_files:
            summary = summarizer.summarize_file(str(py_file))

            for elem in summary.elements:
                embedding = generator.generate_embedding(
                    elem.description or f"def {elem.name}",
                    source_file=str(py_file.relative_to(tmpdir)),
                    element_type=elem.type,
                    element_name=elem.name,
                )
                store.add_embedding(embedding)

        assert store.size() > 0


def test_policy_before_search():
    """Test that policy validates before search."""
    context = ContextLoader.create_default()
    engine = PolicyEngine(context)

    from projectmind.compliance import ActionRequest

    # Analyze request should be allowed
    request = ActionRequest(
        agent_name="searcher",
        action_type="analyze",
        target_file="src/utils.py",
        change_summary="Search for similar code",
    )

    assert engine.validate_action(request)


def test_semantic_search_workflow():
    """Test complete semantic search workflow."""
    generator = EmbeddingGenerator()
    store = VectorStore()

    # Index some code
    code_samples = [
        {"name": "add", "code": "def add(x, y): return x + y"},
        {"name": "subtract", "code": "def subtract(x, y): return x - y"},
        {"name": "multiply", "code": "def multiply(x, y): return x * y"},
    ]

    embeddings = []
    for sample in code_samples:
        emb = generator.generate_embedding(
            sample["code"],
            element_name=sample["name"],
            element_type="function",
        )
        embeddings.append(emb)
        store.add_embedding(emb)

    # Search
    search = SemanticSearch(generator, store)
    results = search.search("add numbers together", top_k=2)

    assert len(results) > 0
    assert results[0][1] >= 0  # Has similarity score


def test_batch_indexing():
    """Test indexing multiple files."""
    generator = EmbeddingGenerator()
    store = VectorStore()

    files = [
        "utils.py",
        "helpers.py",
        "models.py",
    ]

    for file in files:
        embeddings = generator.generate_embeddings_batch(
            [f"def func_{file}(): pass"],
            source_file=file,
        )
        store.add_embeddings(embeddings)

    assert store.size() == 3

    utils_items = store.filter_by_source("utils.py")
    assert len(utils_items) == 1


def test_search_respects_constraints():
    """Test that search respects policy constraints."""
    context = ContextLoader.create_default()
    engine = PolicyEngine(context)

    from projectmind.compliance import ActionRequest

    # Search on critical file
    request = ActionRequest(
        agent_name="searcher",
        action_type="analyze",
        target_file="project_context.yaml",
    )

    # Should be denied
    assert not engine.validate_action(request)
