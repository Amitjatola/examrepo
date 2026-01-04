"""
Embedding service using sentence-transformers and BAAI/bge-large-en-v1.5.
Provides conceptual vectors for questions and search queries.
"""

from typing import List, Union

# Global model instance for singleton-like usage
_MODEL = None

def get_embedding_model():
    """Load the BGE-Large model once and reuse it."""
    # MOCKED FOR DEPLOYMENT WITHOUT ML DEPS
    global _MODEL
    _MODEL = "mock"
    return _MODEL

def generate_embeddings(texts: Union[str, List[str]]) -> list:
    """
    Generate vector embeddings for input text(s).
    The model produces 384-dimensional vectors.
    """
    # MOCKED: Return dummy zeros
    if isinstance(texts, str):
        return [0.0] * 384
    return [[0.0] * 384 for _ in texts]
