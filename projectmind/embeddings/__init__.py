"""
Phase 3: Embeddings & Retrieval

Semantic code search and context-aware retrieval.
Uses efficient vector embeddings and similarity matching.
"""

from .embedding_generator import EmbeddingGenerator, Embedding
from .vector_store import VectorStore
from .context_retriever import ContextRetriever
from .semantic_search import SemanticSearch

__all__ = [
    "EmbeddingGenerator",
    "Embedding",
    "VectorStore",
    "ContextRetriever",
    "SemanticSearch",
]
