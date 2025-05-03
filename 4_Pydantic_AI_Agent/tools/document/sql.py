"""
SQL query tools for tabular document data.

This module provides SQL query functionality for tabular data stored in the database.
"""

from supabase import Client
import re
import json

async def execute_sql_query_tool(supabase: Client, sql_query: str) -> str:
    """
    Run a SQL query - use this to query from the document_rows table once you know the file ID you are querying. 
    dataset_id is the file_id and you are always using the row_data for filtering, which is a jsonb field that has 
    all the keys from the file schema given in the document_metadata table.

    Never use a placeholder file ID. Always use the list_documents tool first to get the file ID.

    Example query:

    SELECT AVG((row_data->>'revenue')::numeric)
    FROM document_rows
    WHERE dataset_id = '123';

    Example query 2:

    SELECT 
        row_data->>'category' as category,
        SUM((row_data->>'sales')::numeric) as total_sales
    FROM document_rows
    WHERE dataset_id = '123'
    GROUP BY row_data->>'category';
    
    Args:
        supabase: The Supabase client
        sql_query: The SQL query to execute (must be read-only)
        
    Returns:
        str: The results of the SQL query in JSON format
    """
    try:
        # Check if the query is read-only (only allowing SELECT statements)
        if not is_read_only_query(sql_query):
            return "Only SELECT queries are allowed for security reasons."
        
        # Execute the query on Supabase
        response = supabase.rpc('execute_sql', {'query_text': sql_query}).execute()
        
        if 'error' in response:
            return f"SQL Error: {response['error']['message']}"
            
        # Format the response data
        if len(response.data) == 0:
            return "Query executed successfully but returned no results."
            
        return json.dumps(response.data, indent=2)
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return f"Error executing SQL query: {str(e)}"

def is_read_only_query(sql_query: str) -> bool:
    """
    Check if a SQL query is read-only (SELECT only).
    
    Args:
        sql_query: The SQL query to check
        
    Returns:
        bool: True if the query is read-only, False otherwise
    """
    # Remove comments and normalize whitespace
    normalized_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    normalized_query = re.sub(r'/\*.*?\*/', '', normalized_query, flags=re.DOTALL)
    normalized_query = normalized_query.strip().lower()
    
    # Check if the query starts with SELECT
    if not normalized_query.startswith('select'):
        return False
    
    # Check for non-SELECT statements
    dangerous_keywords = [
        'insert', 'update', 'delete', 'drop', 'alter', 'create', 
        'truncate', 'replace', 'upsert', 'copy', 'grant', 'revoke'
    ]
    
    for keyword in dangerous_keywords:
        # Match whole words only
        if re.search(r'\b' + keyword + r'\b', normalized_query):
            return False
            
    return True
