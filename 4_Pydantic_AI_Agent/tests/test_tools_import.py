"""
Test to verify that all tools are properly exported from the new modular structure.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_tools_export():
    """Test that all tools can be imported from the tools package directly."""
    from tools import (
        web_search_tool,
        brave_web_search,
        searxng_web_search,
        retrieve_relevant_documents_tool,
        list_documents_tool,
        get_document_content_tool,
        execute_sql_query_tool,
        image_analysis_tool,
        execute_safe_code_tool,
        get_embedding,
        embedding_model
    )
    
    # If we reach here without errors, the imports are working correctly
    assert True

def test_tools_direct_import():
    """Test that all tools can be imported from their specific modules."""
    from tools.web.search import web_search_tool, brave_web_search, searxng_web_search
    from tools.document.retrieval import retrieve_relevant_documents_tool, list_documents_tool, get_document_content_tool
    from tools.document.sql import execute_sql_query_tool
    from tools.image.analysis import image_analysis_tool
    from tools.code.execution import execute_safe_code_tool
    from tools.common.embedding import get_embedding, embedding_model
    
    # If we reach here without errors, the imports are working correctly
    assert True
