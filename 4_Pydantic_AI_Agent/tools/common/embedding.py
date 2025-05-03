"""
Embedding utilities for vector operations.

This module provides functions for generating and working with embeddings.
"""

from openai import AsyncOpenAI
import os

# Default embedding model if not specified in environment
embedding_model = os.getenv('EMBEDDING_MODEL') or 'text-embedding-3-small'

async def get_embedding(text: str, embedding_client: AsyncOpenAI) -> list[float]:
    """
    Get embedding vector from OpenAI.
    
    Args:
        text: The text to embed
        embedding_client: The OpenAI client to use for embedding
        
    Returns:
        list[float]: The embedding vector
    """
    try:
        text = text.replace("\n", " ")
        result = await embedding_client.embeddings.create(
            input=[text], 
            model=embedding_model
        )
        return result.data[0].embedding
    except Exception as e:
        raise e
