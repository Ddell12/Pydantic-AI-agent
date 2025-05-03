"""
Agent tools package.

This package contains all the tools used by the AI agent organized by category:
- web: Web search tools
- document: Document processing and RAG tools
- code: Code execution tools
- image: Image analysis tools
- common: Shared utilities and helpers
"""

# Import all tools for backward compatibility
from .web.search import web_search_tool, brave_web_search, searxng_web_search
from .document.retrieval import (
    retrieve_relevant_documents_tool,
    list_documents_tool,
    get_document_content_tool
)
from .document.sql import execute_sql_query_tool
from .image.analysis import image_analysis_tool
from .code.execution import execute_safe_code_tool
from .common.embedding import get_embedding, embedding_model

__all__ = [
    "web_search_tool",
    "brave_web_search",
    "searxng_web_search",
    "retrieve_relevant_documents_tool",
    "list_documents_tool",
    "get_document_content_tool",
    "execute_sql_query_tool",
    "image_analysis_tool",
    "execute_safe_code_tool",
    "get_embedding",
    "embedding_model"
]
