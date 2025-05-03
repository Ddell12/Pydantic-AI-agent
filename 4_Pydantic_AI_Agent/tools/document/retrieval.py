"""
Document retrieval tools for the agent.

This module provides functions for retrieving documents from the knowledge base.
"""

from openai import AsyncOpenAI
from supabase import Client
from typing import List
import json

from ..common.embedding import get_embedding

async def retrieve_relevant_documents_tool(
    supabase: Client, 
    embedding_client: AsyncOpenAI, 
    user_query: str
) -> str:
    """
    Function to retrieve relevant document chunks with RAG.
    This is called by the retrieve_relevant_documents tool for the agent.
    
    Args:
        supabase: The Supabase client
        embedding_client: The OpenAI client for generating embeddings
        user_query: The user's question or query
        
    Returns:
        str: Formatted string containing relevant document chunks with metadata
    """
    try:
        # Generate embedding for the query
        embedding = await get_embedding(user_query, embedding_client)
        
        # Query Supabase for similar documents
        response = supabase.rpc(
            'match_documents',
            {'query_embedding': embedding, 'match_count': 4}
        ).execute()
        
        if len(response.data) == 0:
            return "No relevant documents found for the query."
            
        chunks = []
        for i, item in enumerate(response.data, 1):
            # Extract metadata
            metadata = json.loads(item['metadata']) if item.get('metadata') else {}
            source_info = f" (Source: {metadata.get('source', 'Unknown')})" if metadata.get('source') else ""
            
            # Format each chunk with metadata
            chunk_text = f"Document {i}: {item['content']}{source_info}\n"
            chunks.append(chunk_text)
            
        return "\n".join(chunks)
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return f"Error retrieving documents: {str(e)}"

async def list_documents_tool(supabase: Client) -> List[str]:
    """
    Function to retrieve a list of all available documents.
    This is called by the list_documents tool for the agent.
    
    Args:
        supabase: The Supabase client
        
    Returns:
        List[str]: List of documents including their metadata (URL/path, schema if applicable, etc.)
    """
    try:
        # Query all documents from document_metadata table
        response = supabase.table('document_metadata').select('*').execute()
        
        if len(response.data) == 0:
            return ["No documents available in the knowledge base."]
            
        documents = []
        for doc in response.data:
            # Format document info
            doc_id = doc.get('id', 'Unknown ID')
            title = doc.get('title', 'Untitled')
            source = doc.get('source', 'Unknown source')
            file_type = doc.get('file_type', 'Unknown type')
            
            # Include schema info for tabular data if available
            schema_info = ""
            if doc.get('schema'):
                schema_info = f" (Schema: {doc['schema']})"
                
            documents.append(f"ID: {doc_id} - {title} from {source} ({file_type}){schema_info}")
            
        return documents
    except Exception as e:
        print(f"Error listing documents: {e}")
        return [f"Error listing documents: {str(e)}"]

async def get_document_content_tool(supabase: Client, document_id: str) -> str:
    """
    Retrieve the full content of a specific document by combining all its chunks.
    This is called by the get_document_content tool for the agent.
    
    Args:
        supabase: The Supabase client
        document_id: The ID (or file path) of the document to retrieve
        
    Returns:
        str: The complete content of the document with all chunks combined in order
    """
    try:
        # First check if the document exists
        metadata_response = supabase.table('document_metadata').select('*').eq('id', document_id).execute()
        
        if len(metadata_response.data) == 0:
            return f"Document with ID {document_id} not found."
            
        # Get document chunks ordered by chunk_index
        chunks_response = supabase.table('documents').select('*').eq('metadata->>document_id', document_id).order('metadata->>chunk_index').execute()
        
        if len(chunks_response.data) == 0:
            return f"No content chunks found for document with ID {document_id}."
            
        # Combine all chunks
        content_chunks = []
        for chunk in chunks_response.data:
            content_chunks.append(chunk.get('content', ''))
            
        return "\n".join(content_chunks)
    except Exception as e:
        print(f"Error retrieving document content: {e}")
        return f"Error retrieving document content: {str(e)}"
