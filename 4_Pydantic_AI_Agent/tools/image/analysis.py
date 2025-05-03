"""
Image analysis tools for the agent.

This module provides image analysis functionality using vision AI models.
"""

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, BinaryContent
from supabase import Client
import base64
import os

async def image_analysis_tool(supabase: Client, document_id: str, query: str) -> str:
    """
    Analyzes an image based on the document ID of the image provided.
    This function pulls the binary of the image from the knowledge base
    and passes that into a subagent with a vision LLM.
    
    Args:
        supabase: The Supabase client
        document_id: The ID (or file path) of the image to analyze
        query: What to extract from the image analysis
        
    Returns:
        str: An analysis of the image based on the query
    """
    try:
        # First, get the document metadata to ensure it's an image
        metadata_response = supabase.table('document_metadata').select('*').eq('id', document_id).execute()
        
        if len(metadata_response.data) == 0:
            return f"Image with ID {document_id} not found."
            
        file_type = metadata_response.data[0].get('file_type', '').lower()
        
        # Check if it's an image file
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        is_image = any(file_type.endswith(ext) for ext in image_extensions)
        
        if not is_image:
            return f"Document with ID {document_id} is not an image (type: {file_type})."
            
        # Get the image binary data
        binary_response = supabase.table('document_binary').select('*').eq('document_id', document_id).execute()
        
        if len(binary_response.data) == 0:
            return f"Binary data for image with ID {document_id} not found."
            
        # Get binary data and mime type
        binary_str = binary_response.data[0].get('binary_data', '')
        mime_type = binary_response.data[0].get('mime_type', 'image/jpeg')
        
        # Create a vision agent for analyzing the image
        vision_model = "gpt-4o"
        vision_api_key = os.getenv('LLM_API_KEY') or 'your-api-key'
        vision_base_url = os.getenv('LLM_BASE_URL') or 'https://api.openai.com/v1'
        
        vision_agent = Agent(
            OpenAIModel(
                vision_model,
                provider=OpenAIProvider(
                    base_url=vision_base_url, 
                    api_key=vision_api_key
                )
            ),
            system_prompt=f"You are an AI that analyzes images. Answer the following question about the image: {query}"
        )
        
        # Turn the binary string into binary and send it into the vision LLM
        binary = base64.b64decode(binary_str.encode('utf-8'))
        result = await vision_agent.run([query, BinaryContent(data=binary, media_type=mime_type)])

        return result.data

    except Exception as e:
        print(f"Error analyzing image: {e}")
        return f"Error analyzing image: {str(e)}"
