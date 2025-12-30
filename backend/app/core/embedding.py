"""
Embedding service using sentence-transformers and BAAI/bge-large-en-v1.5.
Provides conceptual vectors for questions and search queries.
"""

from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from typing import List, Union

# Global model instance for singleton-like usage
_MODEL = None

def get_embedding_model():
    """Load the BGE-Large model once and reuse it."""
    global _MODEL
    if _MODEL is None:
        # Use CPU by default, or MPS/CUDA if available for speed
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        # bge-small-en-v1.5 is the lightweight version of the SOTA retrieval model
        _MODEL = SentenceTransformer('BAAI/bge-small-en-v1.5', device=device)
    return _MODEL

def generate_embeddings(texts: Union[str, List[str]]) -> np.ndarray:
    """
    Generate vector embeddings for input text(s).
    The model produces 1024-dimensional vectors.
    """
    model = get_embedding_model()
    
    # BGE models benefit from specific instruction prefix for queries vs documents
    # However, for pure similarity we can use them directly or add prefixes
    # For now, we'll use them directly as common practice with ST
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings
