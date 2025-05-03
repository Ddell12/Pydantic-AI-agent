import pytest
import sys
import os
import json
import base64
from unittest.mock import patch, MagicMock, AsyncMock, call

# Mock environment variables before importing modules that use them
with patch.dict(os.environ, {
    'LLM_PROVIDER': 'openai',
    'LLM_BASE_URL': 'https://api.openai.com/v1',
    'LLM_API_KEY': 'test-api-key',
    'LLM_CHOICE': 'gpt-4o-mini',
    'VISION_LLM_CHOICE': 'gpt-4o-mini',
    'EMBEDDING_PROVIDER': 'openai',
    'EMBEDDING_BASE_URL': 'https://api.openai.com/v1',
    'EMBEDDING_API_KEY': 'test-api-key',
    'EMBEDDING_MODEL_CHOICE': 'text-embedding-3-small',
    'SUPABASE_URL': 'https://test-supabase-url.com',
    'SUPABASE_SERVICE_KEY': 'test-supabase-key',
    'BRAVE_API_KEY': 'test-brave-key',
    'SEARXNG_BASE_URL': 'http://test-searxng-url.com'
}):
    # Mock the AsyncOpenAI client before it's used in tools
    with patch('openai.AsyncOpenAI') as mock_openai_client:
        # Configure the mock to return a MagicMock
        mock_client = MagicMock()
        mock_openai_client.return_value = mock_client
        
        # Mock the Supabase client
        with patch('supabase.create_client') as mock_create_client:
            mock_supabase = MagicMock()
            mock_create_client.return_value = mock_supabase
            
            # Add parent directory to path to import the tools module
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Import tools from their new locations
            from tools.web.search import brave_web_search, searxng_web_search, web_search_tool
            from tools.common.embedding import get_embedding
            from tools.document.retrieval import retrieve_relevant_documents_tool, list_documents_tool, get_document_content_tool
            from tools.image.analysis import image_analysis_tool
            from tools.code.execution import execute_safe_code_tool


class TestWebSearchTools:
    @pytest.mark.asyncio
    async def test_brave_web_search_success(self):
        # Mock HTTP client and response
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "title": "Test Title 1",
                        "description": "Test Description 1",
                        "url": "https://example.com/1"
                    },
                    {
                        "title": "Test Title 2",
                        "description": "Test Description 2",
                        "url": "https://example.com/2"
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        # Test the function
        result = await brave_web_search("test query", mock_client, "test-api-key")
        
        # Verify the HTTP request was made correctly
        mock_client.get.assert_called_once_with(
            'https://api.search.brave.com/res/v1/web/search',
            params={
                'q': "test query",
                'count': 5,
                'text_decorations': True,
                'search_lang': 'en'
            },
            headers={
                'X-Subscription-Token': 'test-api-key',
                'Accept': 'application/json',
            }
        )
        
        # Verify the response was processed correctly
        assert "Test Title 1" in result
        assert "Test Description 1" in result
        assert "https://example.com/1" in result
        assert "Test Title 2" in result
        assert "Test Description 2" in result
        assert "https://example.com/2" in result

    @pytest.mark.asyncio
    async def test_brave_web_search_no_results(self):
        # Mock HTTP client and response with no results
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"web": {"results": []}}
        mock_client.get.return_value = mock_response
        
        # Test the function
        result = await brave_web_search("test query", mock_client, "test-api-key")
        
        # Verify the response for no results
        assert result == "No results found for the query."

    @pytest.mark.asyncio
    async def test_searxng_web_search_success(self):
        # Mock HTTP client and response
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "SearXNG Result 1",
                    "url": "https://example.com/searxng1",
                    "content": "SearXNG Content 1"
                },
                {
                    "title": "SearXNG Result 2",
                    "url": "https://example.com/searxng2",
                    "content": "SearXNG Content 2"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        # Test the function
        result = await searxng_web_search("test query", mock_client, "https://searxng.example.com")
        
        # Verify the HTTP request was made correctly
        mock_client.get.assert_called_once_with(
            "https://searxng.example.com/search",
            params={'q': "test query", 'format': 'json'}
        )
        
        # Verify the response was processed correctly
        assert "SearXNG Result 1" in result
        assert "https://example.com/searxng1" in result
        assert "SearXNG Content 1" in result
        assert "SearXNG Result 2" in result
        assert "https://example.com/searxng2" in result
        assert "SearXNG Content 2" in result

    @pytest.mark.asyncio
    async def test_searxng_web_search_no_results(self):
        # Mock HTTP client and response with no results
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_client.get.return_value = mock_response
        
        # Test the function
        result = await searxng_web_search("test query", mock_client, "https://searxng.example.com")
        
        # Verify the response for no results
        assert result == "No results found for the query."

    @pytest.mark.asyncio
    @patch('tools.web.search.brave_web_search')
    async def test_web_search_tool_with_brave(self, mock_brave_search):
        # Setup mock for brave search
        mock_brave_search.return_value = "Brave search results"
        
        # Create a specific mock client to pass to the function
        mock_client = AsyncMock()
        
        # Test with Brave API key provided
        result = await web_search_tool(
            "test query", 
            mock_client, 
            "brave-api-key", 
            "https://searxng.example.com"
        )
        
        # Verify Brave search was called with the right parameters
        # Use ANY for the client parameter since we can't directly compare AsyncMock instances
        from unittest.mock import ANY
        mock_brave_search.assert_called_once_with("test query", ANY, "brave-api-key")
        assert result == "Brave search results"

    @pytest.mark.asyncio
    @patch('tools.web.search.searxng_web_search')
    async def test_web_search_tool_with_searxng(self, mock_searxng_search):
        # Setup mock for SearXNG search
        mock_searxng_search.return_value = "SearXNG search results"
        
        # Create a specific mock client to pass to the function
        mock_client = AsyncMock()
        
        # Test with no Brave API key (should use SearXNG)
        result = await web_search_tool(
            "test query", 
            mock_client, 
            "", 
            "https://searxng.example.com"
        )
        
        # Verify SearXNG search was called with the right parameters
        # Use ANY for the client parameter since we can't directly compare AsyncMock instances
        from unittest.mock import ANY
        mock_searxng_search.assert_called_once_with("test query", ANY, "https://searxng.example.com")
        assert result == "SearXNG search results"

    @pytest.mark.asyncio
    async def test_web_search_tool_exception(self):
        # Mock HTTP client that raises an exception
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Test exception")
        
        # Test with both API keys to ensure exception handling
        result = await web_search_tool(
            "test query", 
            mock_client, 
            "brave-api-key", 
            "https://searxng.example.com"
        )
        
        # Verify exception was handled
        assert "Test exception" in result


# Global reference to the mocked OpenAI client
openai_client_mock = mock_client

class TestEmbeddingTools:
    @pytest.mark.asyncio
    async def test_get_embedding_success(self):
        # Mock OpenAI client embeddings create method
        mock_client = AsyncMock()
        mock_embeddings = AsyncMock()
        mock_client.embeddings = mock_embeddings
        mock_response = MagicMock()
        
        # Configure a successful response with embedding data
        mock_data = MagicMock()
        mock_data.embedding = [0.1, 0.2, 0.3]
        mock_response.data = [mock_data]
        mock_embeddings.create.return_value = mock_response
        
        # Test the function
        with patch('tools.common.embedding.embedding_model', 'text-embedding-3-small'):
            result = await get_embedding("test text", mock_client)
        
        # Verify the embedding request was made correctly
        mock_embeddings.create.assert_called_once_with(
            input=["test text"],
            model="text-embedding-3-small"
        )
        
        # Verify the result
        assert result == [0.1, 0.2, 0.3]
        
    @pytest.mark.asyncio
    async def test_get_embedding_exception(self):
        # Mock OpenAI client that raises an exception
        mock_client = AsyncMock()
        mock_embeddings = AsyncMock()
        mock_client.embeddings = mock_embeddings
        mock_embeddings.create.side_effect = Exception("Test exception")
        
        # Test the function
        with patch('tools.common.embedding.embedding_model', 'text-embedding-3-small'):
            with pytest.raises(Exception) as excinfo:
                await get_embedding("test text", mock_client)
            
        # Verify the exception was raised
        assert "Test exception" in str(excinfo.value)


class TestDocumentTools:
    @pytest.mark.asyncio
    @patch('tools.document.retrieval.get_embedding')
    async def test_retrieve_relevant_documents_tool_success(self, mock_get_embedding):
        # Mock embedding function
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Mock Supabase client with document chunks
        mock_supabase = MagicMock()
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        
        # Configure the mock response for rpc
        mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = mock_execute
        
        # The data structure that matches our expected format with valid JSON strings for metadata
        mock_execute.data = [
            {
                'content': 'Document content 1',
                'metadata': '{"source": "source1.txt", "chunk_index": 1}'
            },
            {
                'content': 'Document content 2',
                'metadata': '{"source": "source2.txt", "chunk_index": 1}'
            }
        ]
        
        # Test the function
        result = await retrieve_relevant_documents_tool(mock_supabase, mock_client, "test query")
        
        # Verify get_embedding was called correctly
        mock_get_embedding.assert_called_once_with("test query", mock_client)
        
        # Verify the RPC call was made correctly
        mock_supabase.rpc.assert_called_once_with(
            'match_documents',
            {'query_embedding': [0.1, 0.2, 0.3], 'match_count': 4}
        )
        
        # Verify the result contains both document contents and source info
        assert "Document 1: Document content 1" in result
        assert "Source: source1.txt" in result
        assert "Document 2: Document content 2" in result
        assert "Source: source2.txt" in result

    @pytest.mark.asyncio
    @patch('tools.document.retrieval.get_embedding')
    async def test_retrieve_relevant_documents_tool_no_results(self, mock_get_embedding):
        # Mock embedding function
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        
        # Mock Supabase client with empty response
        mock_supabase = MagicMock()
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        mock_supabase.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = mock_execute
        mock_execute.data = []
        
        # Test the function
        result = await retrieve_relevant_documents_tool(mock_supabase, mock_client, "test query")
        
        # Verify the result for no documents
        assert result == "No relevant documents found for the query."

    @pytest.mark.asyncio
    @patch('tools.document.retrieval.get_embedding')
    async def test_retrieve_relevant_documents_tool_exception(self, mock_get_embedding):
        # Mock embedding function that raises an exception
        mock_get_embedding.side_effect = Exception("Test exception")
        
        # Test the function
        with patch('builtins.print') as mock_print:
            result = await retrieve_relevant_documents_tool(mock_supabase, mock_client, "test query")
        
        # Verify the exception was handled
        mock_print.assert_called_once_with("Error retrieving documents: Test exception")
        assert "Error retrieving documents: Test exception" in result

    @pytest.mark.asyncio
    async def test_list_documents_tool_success(self):
        # Mock Supabase client with document list
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_execute = MagicMock()
        
        # Configure the mock response
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.execute.return_value = mock_execute
        
        # Mock data with document metadata
        mock_execute.data = [
            {
                'id': 'doc1',
                'title': 'Document 1',
                'source': 'Source 1',
                'file_type': 'pdf',
                'schema': None
            },
            {
                'id': 'doc2',
                'title': 'Document 2',
                'source': 'Source 2',
                'file_type': 'csv',
                'schema': '{"column1": "string", "column2": "number"}'
            }
        ]
        
        # Test the function
        result = await list_documents_tool(mock_supabase)
        
        # Verify Supabase was queried correctly
        mock_supabase.table.assert_called_once_with('document_metadata')
        mock_table.select.assert_called_once_with('*')
        
        # Verify the result contains both documents
        assert isinstance(result, list)
        assert len(result) == 2
        assert "ID: doc1 - Document 1 from Source 1 (pdf)" in result[0]
        assert "ID: doc2 - Document 2 from Source 2 (csv) (Schema: {\"column1\": \"string\", \"column2\": \"number\"})" in result[1]

    @pytest.mark.asyncio
    async def test_list_documents_tool_exception(self):
        # Mock Supabase client that raises an exception
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("Test exception")
        
        # Test the function
        with patch('builtins.print') as mock_print:
            result = await list_documents_tool(mock_supabase)
        
        # Verify the exception was handled
        mock_print.assert_called_once_with("Error listing documents: Test exception")
        assert result == ["Error listing documents: Test exception"]

    @pytest.mark.asyncio
    async def test_get_document_content_tool_success(self):
        # Mock Supabase client with document content
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_eq = MagicMock()
        mock_order = MagicMock()
        mock_execute = MagicMock()
        
        # Configure the first call to check if document exists
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{'id': 'doc1'}])
        
        # Need to reset the mock for the second call to get chunks
        mock_table.reset_mock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_execute
        
        # Mock chunks data
        mock_execute.data = [
            {
                'content': 'Document content part 1',
            },
            {
                'content': 'Document content part 2',
            }
        ]
        
        # Test the function
        result = await get_document_content_tool(mock_supabase, 'doc1')
        
        # Verify the result contains both parts of the document
        assert "Document content part 1" in result
        assert "Document content part 2" in result

    @pytest.mark.asyncio
    async def test_get_document_content_tool_no_content(self):
        # Mock Supabase client with no results
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_eq = MagicMock()
        mock_order = MagicMock()
        mock_execute = MagicMock()
        
        # Configure the first call to check if document exists
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{'id': 'doc1'}])
        
        # Need to reset the mock for the second call to get chunks
        mock_table.reset_mock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_execute
        mock_execute.data = []
        
        # Test the function
        result = await get_document_content_tool(mock_supabase, 'doc1')
        
        # Verify the result for no content
        assert result == "No content chunks found for document with ID doc1."

    @pytest.mark.asyncio
    async def test_get_document_content_tool_exception(self):
        # Mock Supabase client that raises an exception
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("Test exception")
        
        # Test the function
        with patch('builtins.print') as mock_print:
            result = await get_document_content_tool(mock_supabase, 'doc1')
        
        # Verify the exception was handled
        mock_print.assert_called_once_with("Error retrieving document content: Test exception")
        assert "Error retrieving document content: Test exception" in result


class TestImageAnalysisTool:
    @pytest.mark.asyncio
    async def test_image_analysis_tool_success(self):
        # Directly patch the agent run method
        with patch('tools.image.analysis.Agent') as mock_agent_class, \
             patch('tools.image.analysis.OpenAIModel') as mock_model_class, \
             patch('tools.image.analysis.OpenAIProvider') as mock_provider_class, \
             patch('tools.image.analysis.os.getenv') as mock_getenv, \
             patch('tools.image.analysis.base64.b64decode') as mock_b64decode:
            
            # Mock environment variables
            mock_getenv.side_effect = lambda key, default=None: {
                'LLM_API_KEY': 'test-api-key',
                'LLM_BASE_URL': 'https://api.openai.com/v1'
            }.get(key, default)
            
            # Mock base64 decoding to avoid padding issues
            mock_b64decode.return_value = b'fake_image_data'
            
            # Mock the Agent class and its run method
            mock_agent_instance = MagicMock()
            mock_agent_class.return_value = mock_agent_instance
            mock_result = MagicMock()
            mock_result.data = "Image analysis result"
            
            # Create a custom async mock for run method
            async def mock_run(*args, **kwargs):
                return mock_result
                
            mock_agent_instance.run = mock_run
            
            # Mock Supabase client with proper response structure
            mock_supabase = MagicMock()
            
            # Setup metadata response
            metadata_response = MagicMock()
            metadata_response.data = [{'file_type': 'jpg'}]
            metadata_table = MagicMock()
            metadata_table.select.return_value.eq.return_value.execute.return_value = metadata_response
            
            # Setup binary response
            binary_response = MagicMock()
            binary_response.data = [{'binary_data': 'dGVzdCBiYXNlNjQgZGF0YQ==', 'mime_type': 'image/jpeg'}]
            binary_table = MagicMock()
            binary_table.select.return_value.eq.return_value.execute.return_value = binary_response
            
            # Configure table method to return different mocks based on the table name
            def mock_table(table_name):
                if table_name == 'document_metadata':
                    return metadata_table
                elif table_name == 'document_binary':
                    return binary_table
                return MagicMock()
                
            mock_supabase.table = mock_table
            
            # Test the function
            result = await image_analysis_tool(mock_supabase, 'img1', 'Describe this image')
            
            # Verify the result
            assert result == "Image analysis result"
            
            # Verify the mocks were called correctly
            mock_agent_class.assert_called_once()
            mock_model_class.assert_called_once()
            mock_provider_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_image_analysis_tool_no_document(self):
        # Mock Supabase client with empty response
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_execute = MagicMock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_execute
        
        # Configure the mock to return empty data
        mock_execute.data = []
        
        # Test the function
        result = await image_analysis_tool(mock_supabase, 'img1', 'Describe this image')
        
        # Verify the result contains the expected error message
        assert "not found" in result
        
    @pytest.mark.asyncio
    async def test_image_analysis_tool_no_binary(self):
        # Mock Supabase client
        mock_supabase = MagicMock()
        
        # Setup metadata response
        metadata_response = MagicMock()
        metadata_response.data = [{'file_type': 'jpg'}]
        metadata_table = MagicMock()
        metadata_table.select.return_value.eq.return_value.execute.return_value = metadata_response
        
        # Setup empty binary response
        binary_response = MagicMock()
        binary_response.data = []
        binary_table = MagicMock()
        binary_table.select.return_value.eq.return_value.execute.return_value = binary_response
        
        # Configure table method
        def mock_table(table_name):
            if table_name == 'document_metadata':
                return metadata_table
            elif table_name == 'document_binary':
                return binary_table
            return MagicMock()
            
        mock_supabase.table = mock_table
        
        # Test the function
        result = await image_analysis_tool(mock_supabase, 'img1', 'Describe this image')
        
        # Verify the result
        assert "Binary data" in result
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_image_analysis_tool_exception(self):
        # Mock Supabase client to raise an exception
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")
        mock_supabase.table.return_value = mock_table
        
        # Test the function
        result = await image_analysis_tool(mock_supabase, 'img1', 'Describe this image')
        
        # Verify the result contains the error message
        assert "Error analyzing image" in result
        assert "Database error" in result


class TestExecuteSafeCodeTool:
    def test_execute_safe_code_success(self):
        # Test code that should execute safely
        code = """
print("Hello, World!")
result = 2 + 2
print(f"2 + 2 = {result}")
"""
        result = execute_safe_code_tool(code)
        
        # Verify the output
        assert "Hello, World!" in result
        assert "2 + 2 = 4" in result

    def test_execute_safe_code_with_allowed_modules(self):
        # Test code that uses allowed modules
        code = """
import math
import json
import datetime

print(f"Pi is approximately {math.pi}")
print(json.dumps({"key": "value"}))
print(f"Current year: {datetime.datetime.now().year}")
"""
        result = execute_safe_code_tool(code)
        
        # Verify the output contains results from allowed modules
        assert "Pi is approximately 3.14" in result
        assert '{"key": "value"}' in result
        assert "Current year:" in result

    def test_execute_safe_code_with_disallowed_modules(self):
        # Test code that tries to import disallowed modules
        code = """
# Try to import os module (should fail)
import os
print("Imported os successfully")  # This line should not execute
"""
        result = execute_safe_code_tool(code)
        
        # Verify that an error was reported and os import failed
        assert "Error executing code:" in result
        assert "Module os is not allowed" in result

    def test_execute_safe_code_with_exception(self):
        # Test code that raises an exception
        code = """
print("Starting")
x = 1 / 0  # Division by zero
print("This won't be reached")
"""
        result = execute_safe_code_tool(code)
        
        # Verify the output shows the exception
        assert "Error executing code: division by zero" in result

    def test_execute_safe_code_with_complex_operations(self):
        # Test code with more complex operations
        code = """
# Define a function
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

# Use list comprehension
squares = [x**2 for x in range(5)]
print(f"Squares: {squares}")

# Use higher-order functions
doubled = list(map(lambda x: x*2, squares))
print(f"Doubled: {doubled}")

# Test recursion
print(f"Factorial of 5: {factorial(5)}")
"""
        result = execute_safe_code_tool(code)
        
        # Verify the output shows complex operations worked
        assert "Squares: [0, 1, 4, 9, 16]" in result
        assert "Doubled: [0, 2, 8, 18, 32]" in result
        assert "Factorial of 5: 120" in result
