"""
Simple test script to verify our refactoring.
"""

import os
import sys

print("Testing import of tools modules...")

# Test importing from tools package
print("1. Testing tools package exports:")
try:
    from tools import (
        web_search_tool,
        retrieve_relevant_documents_tool,
        list_documents_tool,
        get_document_content_tool,
        execute_sql_query_tool,
        image_analysis_tool,
        execute_safe_code_tool
    )
    print("✓ All tools imported successfully from tools package")
except Exception as e:
    print(f"✗ Error importing from tools package: {str(e)}")

# Test importing from specific modules
print("\n2. Testing direct module imports:")
try:
    from tools.web.search import web_search_tool, brave_web_search, searxng_web_search
    from tools.document.retrieval import retrieve_relevant_documents_tool, list_documents_tool, get_document_content_tool
    from tools.document.sql import execute_sql_query_tool
    from tools.image.analysis import image_analysis_tool
    from tools.code.execution import execute_safe_code_tool
    from tools.common.embedding import get_embedding, embedding_model
    print("✓ All modules imported successfully from specific locations")
except Exception as e:
    print(f"✗ Error importing from specific modules: {str(e)}")

print("\nRefactoring verification complete!")
