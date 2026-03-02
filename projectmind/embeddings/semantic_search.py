"""
Semantic Search: Query-based code search using embeddings.

Find relevant code based on natural language queries.
"""

from typing import List, Optional, Tuple
from .embedding_generator import EmbeddingGenerator, Embedding
from .vector_store import VectorStore
from .context_retriever import ContextRetriever, ContextWindow


class SemanticSearch:
    """Semantic search over code using embeddings."""

    def __init__(
        self,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        vector_store: Optional[VectorStore] = None,
        context_retriever: Optional[ContextRetriever] = None,
    ):
        """Initialize semantic search."""
        self.generator = embedding_generator or EmbeddingGenerator()
        self.store = vector_store or VectorStore()
        self.retriever = context_retriever or ContextRetriever()

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.05,
    ) -> List[Tuple[Embedding, float]]:
        """Search for relevant code using query."""
        # Generate embedding for query
        query_embedding = self.generator.generate_embedding(
            query,
            element_name="query",
        )

        # Search in store
        results = self.store.search_by_vector(query_embedding.vector, top_k=top_k * 2)

        # Filter by minimum similarity
        filtered = [
            (emb, score) for emb, score in results
            if score >= min_similarity
        ]

        return filtered[:top_k]

    def search_with_context(
        self,
        query: str,
        top_k: int = 5,
        context_window_size: int = 20,
    ) -> List[Tuple[ContextWindow, float, str]]:
        """Search and return context windows.

        Returns: List of (context_window, similarity_score, element_type) tuples
        """
        # Get search results
        results = self.search(query, top_k=top_k)

        context_results = []

        for embedding, score in results:
            if embedding.source_file and embedding.element_name:
                # Get context window
                context = self.retriever.get_function_context(
                    embedding.source_file,
                    embedding.element_name,
                )

                if context:
                    context.relevance_score = score
                    context_results.append(
                        (context, score, embedding.element_type or "unknown")
                    )

        return context_results

    def find_similar_code(
        self,
        code: str,
        top_k: int = 5,
    ) -> List[Tuple[Embedding, float]]:
        """Find code similar to given code."""
        # Generate embedding for code
        code_embedding = self.generator.generate_embedding(
            code,
            element_name="code",
        )

        # Search for similar
        return self.generator.find_similar(code_embedding, self.store.embeddings, top_k)

    def index_code_file(
        self,
        file_path: str,
        code_elements: List[dict],
    ) -> None:
        """Index code elements from a file.

        code_elements should be list of dicts with:
        - name: element name
        - type: "function", "class", etc.
        - content: code content
        """
        for elem in code_elements:
            embedding = self.generator.generate_embedding(
                elem["content"],
                source_file=file_path,
                element_type=elem["type"],
                element_name=elem["name"],
            )

            self.store.add_embedding(embedding)

    def get_statistics(self) -> dict:
        """Get search engine statistics."""
        return {
            "total_embeddings": self.store.size(),
            "embedding_dimension": self.generator.embedding_dim,
            "vocab_size": self.generator.vocab_size,
        }
