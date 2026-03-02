"""
Vector Store: Persistent storage for embeddings.

Manages collection of embeddings with efficient retrieval.
"""

from typing import List, Optional, Dict
from pathlib import Path
import json
import numpy as np
from .embedding_generator import Embedding


class VectorStore:
    """Store and retrieve embeddings efficiently."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize vector store."""
        self.storage_path = Path(storage_path or ".pmind/embeddings")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.embeddings: List[Embedding] = []
        self._load_from_disk()

    def add_embedding(self, embedding: Embedding) -> None:
        """Add embedding to store."""
        # Remove duplicates by ID
        self.embeddings = [e for e in self.embeddings if e.id != embedding.id]
        self.embeddings.append(embedding)

    def add_embeddings(self, embeddings: List[Embedding]) -> None:
        """Add multiple embeddings."""
        for embedding in embeddings:
            self.add_embedding(embedding)

    def get_embedding(self, embedding_id: str) -> Optional[Embedding]:
        """Retrieve embedding by ID."""
        for embedding in self.embeddings:
            if embedding.id == embedding_id:
                return embedding
        return None

    def search_by_vector(
        self,
        vector: List[float],
        top_k: int = 5,
    ) -> List[tuple]:
        """Search embeddings by vector similarity.

        Returns: List of (embedding, similarity_score) tuples
        """
        if not self.embeddings:
            return []

        query_vec = np.array(vector)
        results = []

        for embedding in self.embeddings:
            emb_vec = np.array(embedding.vector)

            # Cosine similarity
            similarity = np.dot(query_vec, emb_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(emb_vec) + 1e-10
            )
            results.append((embedding, float(similarity)))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def filter_by_metadata(
        self,
        key: str,
        value: str,
    ) -> List[Embedding]:
        """Filter embeddings by metadata."""
        return [
            e for e in self.embeddings
            if e.metadata.get(key) == value
        ]

    def filter_by_source(self, source_file: str) -> List[Embedding]:
        """Get all embeddings from a specific source file."""
        return [e for e in self.embeddings if e.source_file == source_file]

    def filter_by_type(self, element_type: str) -> List[Embedding]:
        """Get all embeddings of a specific element type."""
        return [e for e in self.embeddings if e.element_type == element_type]

    def size(self) -> int:
        """Return number of embeddings in store."""
        return len(self.embeddings)

    def clear(self) -> None:
        """Clear all embeddings."""
        self.embeddings = []

    def save_to_disk(self) -> None:
        """Save embeddings to disk."""
        # Save metadata
        metadata = {
            "total_embeddings": len(self.embeddings),
            "files": sorted(set(e.source_file for e in self.embeddings if e.source_file)),
        }

        # Save summaries (vectors too large, store separately)
        summaries = []
        for i, emb in enumerate(self.embeddings):
            summaries.append({
                "id": emb.id,
                "content": emb.content[:200],  # First 200 chars
                "source_file": emb.source_file,
                "element_type": emb.element_type,
                "element_name": emb.element_name,
                "metadata": emb.metadata,
            })

            # Save vector separately
            vector_file = self.storage_path / f"vector_{i}.npy"
            np.save(vector_file, np.array(emb.vector))

        # Save metadata and summaries
        metadata_file = self.storage_path / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        summary_file = self.storage_path / "summaries.json"
        with open(summary_file, "w") as f:
            json.dump(summaries, f, indent=2)

    def _load_from_disk(self) -> None:
        """Load embeddings from disk."""
        metadata_file = self.storage_path / "metadata.json"
        summary_file = self.storage_path / "summaries.json"

        if not metadata_file.exists() or not summary_file.exists():
            return

        try:
            with open(summary_file) as f:
                summaries = json.load(f)

            self.embeddings = []
            for i, summary in enumerate(summaries):
                vector_file = self.storage_path / f"vector_{i}.npy"

                if vector_file.exists():
                    vector = np.load(vector_file).tolist()

                    embedding = Embedding(
                        id=summary["id"],
                        content=summary["content"],
                        vector=vector,
                        source_file=summary.get("source_file"),
                        element_type=summary.get("element_type"),
                        element_name=summary.get("element_name"),
                        metadata=summary.get("metadata", {}),
                    )

                    self.embeddings.append(embedding)

        except Exception as e:
            print(f"Warning: Failed to load embeddings: {e}")
