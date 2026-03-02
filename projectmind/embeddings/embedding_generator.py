"""
Embedding Generator: Convert code to vector embeddings.

Uses efficient lightweight embeddings for code understanding.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass, field
import hashlib
import numpy as np
from pathlib import Path


@dataclass
class Embedding:
    """Vector embedding of code."""
    id: str
    content: str  # Original code/text
    vector: List[float]  # Embedding vector
    metadata: Dict[str, str] = field(default_factory=dict)
    source_file: Optional[str] = None
    element_type: Optional[str] = None  # "function", "class", "module"
    element_name: Optional[str] = None


class EmbeddingGenerator:
    """Generate embeddings for code elements."""

    # Simple vocabulary for code tokens (lightweight alternative to transformers)
    CODE_TOKENS = {
        "def": 1, "class": 2, "import": 3, "from": 4, "return": 5,
        "if": 6, "else": 7, "for": 8, "while": 9, "try": 10,
        "except": 11, "with": 12, "pass": 13, "break": 14, "continue": 15,
        "lambda": 16, "yield": 17, "async": 18, "await": 19, "self": 20,
        "None": 21, "True": 22, "False": 23, "and": 24, "or": 25,
    }

    EMBEDDING_DIM = 128  # Lightweight embedding dimension

    def __init__(self):
        """Initialize embedding generator."""
        self.vocab_size = len(self.CODE_TOKENS) + 1000  # +1000 for other tokens
        self.embedding_dim = self.EMBEDDING_DIM

    def generate_embedding(
        self,
        content: str,
        source_file: Optional[str] = None,
        element_type: Optional[str] = None,
        element_name: Optional[str] = None,
    ) -> Embedding:
        """Generate embedding for code content."""
        # Generate ID
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        embedding_id = f"{element_name or 'code'}_{content_hash}"

        # Tokenize
        tokens = self._tokenize(content)

        # Generate vector
        vector = self._generate_vector(tokens)

        return Embedding(
            id=embedding_id,
            content=content,
            vector=vector,
            source_file=source_file,
            element_type=element_type,
            element_name=element_name,
            metadata={
                "token_count": str(len(tokens)),
                "content_length": str(len(content)),
            },
        )

    def generate_embeddings_batch(
        self,
        contents: List[str],
        source_file: Optional[str] = None,
    ) -> List[Embedding]:
        """Generate embeddings for multiple code pieces."""
        embeddings = []

        for i, content in enumerate(contents):
            embedding = self.generate_embedding(
                content,
                source_file=source_file,
                element_name=f"batch_{i}",
            )
            embeddings.append(embedding)

        return embeddings

    def _tokenize(self, content: str) -> List[int]:
        """Tokenize code content with character n-grams for better semantics."""
        tokens = []

        # Add character 3-grams for semantic similarity
        content_clean = content.lower().replace('\n', ' ').replace('\t', ' ')
        
        # Add 3-grams
        for i in range(len(content_clean) - 2):
            ngram = content_clean[i:i+3]
            # Use character-level features
            ngram_hash = (hash(ngram) % 200) + 1000
            tokens.append(ngram_hash)
        
        # Split by whitespace and special characters for word-level tokens
        words = content.split()

        for word in words:
            # Remove punctuation
            word_clean = word.strip("()[]{}.,;:\"'").lower()

            if word_clean in self.CODE_TOKENS:
                tokens.append(self.CODE_TOKENS[word_clean])
            elif len(word_clean) > 0:
                # Use word length + first char for similarity
                prefix = word_clean[0]
                word_hash = (hash(prefix + str(len(word_clean))) % 100) + len(self.CODE_TOKENS)
                tokens.append(word_hash)

        return tokens[:500]  # Limit to 500 tokens

    def _generate_vector(self, tokens: List[int]) -> List[float]:
        """Generate embedding vector from tokens."""
        # Initialize with zeros
        vector = np.zeros(self.embedding_dim, dtype=np.float32)

        if not tokens:
            return vector.tolist()

        # Use all unique tokens to generate embeddings
        unique_tokens = list(set(tokens))
        
        # Multiple embeddings for diversity
        token_embeddings = np.zeros((len(unique_tokens), self.embedding_dim))

        for i, token_id in enumerate(unique_tokens):
            # Deterministic embedding based on token ID
            np.random.seed(token_id)
            token_embeddings[i] = np.random.randn(self.embedding_dim) * 0.1

        # Average embeddings
        vector = np.mean(token_embeddings, axis=0) if len(unique_tokens) > 0 else vector

        # Add position-based features (words at different positions matter)
        # Weight tokens by their position and frequency
        for i, token_id in enumerate(tokens):
            weight = 1.0 / (i + 1.0)  # Decay with position
            np.random.seed(token_id + 12345)  # Different seed for position info
            pos_vector = np.random.randn(self.embedding_dim) * (weight * 0.05)
            vector = vector + pos_vector

        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    def similarity(self, embedding1: Embedding, embedding2: Embedding) -> float:
        """Calculate cosine similarity between two embeddings."""
        vec1 = np.array(embedding1.vector)
        vec2 = np.array(embedding2.vector)

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)

        return float(similarity)

    def find_similar(
        self,
        query_embedding: Embedding,
        embeddings: List[Embedding],
        top_k: int = 5,
    ) -> List[tuple]:
        """Find most similar embeddings to query.

        Returns: List of (embedding, similarity_score) tuples
        """
        similarities = [
            (emb, self.similarity(query_embedding, emb))
            for emb in embeddings
        ]

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]
