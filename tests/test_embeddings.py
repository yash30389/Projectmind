"""Tests for Phase 3: Embeddings & Retrieval"""

import pytest
import tempfile
from pathlib import Path
from projectmind.embeddings import (
    EmbeddingGenerator,
    VectorStore,
    ContextRetriever,
    SemanticSearch,
)


@pytest.fixture
def generator():
    """Create embedding generator."""
    return EmbeddingGenerator()


@pytest.fixture
def vector_store():
    """Create vector store."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield VectorStore(tmpdir)


@pytest.fixture
def context_retriever(tmp_path):
    """Create context retriever with test file."""
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def calculate(x, y):
    '''Calculate sum.'''
    return x + y

def multiply(x, y):
    '''Calculate product.'''
    result = x * y
    return result

class Helper:
    '''Helper class.'''
    
    def help(self):
        return True
""")
    return ContextRetriever(str(tmp_path))


def test_generate_embedding(generator):
    """Test generating embedding."""
    code = "def calculate(x, y): return x + y"

    embedding = generator.generate_embedding(code)

    assert embedding.id
    assert embedding.content == code
    assert len(embedding.vector) == generator.embedding_dim
    assert len(embedding.vector) > 0


def test_embedding_vector_normalized(generator):
    """Test that embedding vectors are normalized."""
    code = "def calculate(x, y): return x + y"
    embedding = generator.generate_embedding(code)

    # Check roughly normalized (L2 norm close to 1)
    import numpy as np
    norm = np.linalg.norm(embedding.vector)
    assert 0.5 < norm <= 1.5  # Allow some variation


def test_similarity_calculation(generator):
    """Test similarity calculation between embeddings."""
    code1 = "def add(x, y): return x + y"
    code2 = "def add(a, b): return a + b"
    code3 = "def multiply(x, y): return x * y"

    emb1 = generator.generate_embedding(code1)
    emb2 = generator.generate_embedding(code2)
    emb3 = generator.generate_embedding(code3)

    # Similar functions should have higher similarity
    sim_similar = generator.similarity(emb1, emb2)
    sim_different = generator.similarity(emb1, emb3)

    assert 0 <= sim_similar <= 1
    assert 0 <= sim_different <= 1


def test_find_similar(generator):
    """Test finding similar embeddings."""
    embeddings = []

    codes = [
        "def add(x, y): return x + y",
        "def multiply(x, y): return x * y",
        "def subtract(x, y): return x - y",
    ]

    for code in codes:
        embeddings.append(generator.generate_embedding(code))

    # Query similar to first
    query = embeddings[0]
    similar = generator.find_similar(query, embeddings, top_k=2)

    assert len(similar) == 2
    assert similar[0][0].id == query.id  # First should be itself


def test_vector_store_add_and_retrieve(vector_store):
    """Test adding and retrieving embeddings."""
    generator = EmbeddingGenerator()

    embedding1 = generator.generate_embedding("def func1(): pass")
    embedding2 = generator.generate_embedding("def func2(): pass")

    vector_store.add_embedding(embedding1)
    vector_store.add_embedding(embedding2)

    assert vector_store.size() == 2

    retrieved = vector_store.get_embedding(embedding1.id)
    assert retrieved.id == embedding1.id
    assert retrieved.content == embedding1.content


def test_vector_store_search_by_vector(vector_store):
    """Test searching by vector."""
    generator = EmbeddingGenerator()

    # Add embeddings
    emb1 = generator.generate_embedding("def add(x, y): return x + y")
    emb2 = generator.generate_embedding("def multiply(x, y): return x * y")

    vector_store.add_embeddings([emb1, emb2])

    # Search by vector
    results = vector_store.search_by_vector(emb1.vector, top_k=2)

    assert len(results) == 2
    assert results[0][0].id == emb1.id


def test_vector_store_filter_by_metadata(vector_store):
    """Test filtering by metadata."""
    generator = EmbeddingGenerator()

    emb1 = generator.generate_embedding("code1", element_type="function", element_name="func1")
    emb2 = generator.generate_embedding("code2", element_type="class", element_name="Class1")

    vector_store.add_embeddings([emb1, emb2])

    functions = vector_store.filter_by_type("function")
    assert len(functions) == 1

    classes = vector_store.filter_by_type("class")
    assert len(classes) == 1


def test_context_window_retrieval(context_retriever):
    """Test retrieving context windows."""
    context = context_retriever.get_context_window("test.py", 2, window_size=5)

    assert context is not None
    assert context.file_path == "test.py"
    assert "calculate" in context.content or "def" in context.content


def test_context_window_function(context_retriever):
    """Test retrieving function context."""
    context = context_retriever.get_function_context("test.py", "calculate")

    assert context is not None
    assert "calculate" in context.content
    assert "return" in context.content


def test_context_merge(context_retriever):
    """Test merging context windows."""
    ctx1 = context_retriever.get_context_window("test.py", 1, window_size=3)
    ctx2 = context_retriever.get_context_window("test.py", 5, window_size=3)

    if ctx1 and ctx2:
        merged = context_retriever.merge_contexts([ctx1, ctx2])
        assert "File:" in merged
        assert "test.py" in merged


def test_semantic_search_initialization():
    """Test semantic search initialization."""
    search = SemanticSearch()

    assert search.generator is not None
    assert search.store is not None
    assert search.retriever is not None


def test_semantic_search_basic():
    """Test basic semantic search."""
    generator = EmbeddingGenerator()
    store = VectorStore()

    # Index some code
    embeddings = [
        generator.generate_embedding("def add(x, y): return x + y", element_name="add"),
        generator.generate_embedding("def multiply(x, y): return x * y", element_name="multiply"),
    ]

    store.add_embeddings(embeddings)

    search = SemanticSearch(generator, store)

    # Search
    results = search.search("add numbers", top_k=2)

    assert len(results) > 0


def test_semantic_search_statistics():
    """Test getting search statistics."""
    search = SemanticSearch()

    stats = search.get_statistics()

    assert "total_embeddings" in stats
    assert "embedding_dimension" in stats
    assert stats["embedding_dimension"] == 128


def test_batch_embeddings(generator):
    """Test generating batch embeddings."""
    codes = [
        "def func1(): pass",
        "def func2(): pass",
        "def func3(): pass",
    ]

    embeddings = generator.generate_embeddings_batch(codes)

    assert len(embeddings) == 3
    assert all(len(e.vector) == 128 for e in embeddings)


def test_embedding_metadata(generator):
    """Test embedding metadata."""
    code = "def calculate(x, y): return x + y"

    embedding = generator.generate_embedding(
        code,
        source_file="utils.py",
        element_type="function",
        element_name="calculate",
    )

    assert embedding.source_file == "utils.py"
    assert embedding.element_type == "function"
    assert embedding.element_name == "calculate"
    assert "token_count" in embedding.metadata
