from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
import asyncio

server = MCPServerHTTP(url='http://localhost:3001/sse')  
agent = Agent('openai:gpt-4o-mini', mcp_servers=[server])  


async def main():
    async with agent.run_mcp_servers():  
        result = await agent.run('What is 453945 * 349573?')
    print(result.data)

import requests
import json
from typing import Dict, List, Any, Optional

def search_searxng(query: str, 
                   endpoint: str = "http://localhost:8080/search", 
                   search_format: str = "json",
                   categories: Optional[List[str]] = None,
                   limit: int = 10) -> Dict[str, Any]:
    """
    Search using a local SearXNG instance.
    
    Args:
        query: The search query string
        endpoint: The SearXNG endpoint URL (default: http://localhost:8080/search)
        format: Response format (default: json)
        categories: List of categories to search in (default: None, which searches all)
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        Dict containing the search results
    """
    # Prepare the parameters for the request
    params = {'q': query, 'format': search_format}
    
    # Add categories if specified
    if categories:
        params['categories'] = ','.join(categories)
    
    try:
        # Make the request to SearXNG
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse and return the results
        results = response.json()
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request to SearXNG: {e}")
        return {"error": str(e)}
    
    except json.JSONDecodeError:
        print("Error decoding JSON response")
        return {"error": "Invalid JSON response"}


def display_results(results: Dict[str, Any]) -> None:
    """
    Display search results in a readable format.
    
    Args:
        results: The search results dictionary returned by search_searxng
    """
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    print(f"Found {len(results.get('results', []))} results\n")
    
    for i, result in enumerate(results.get('results', []), 1):
        print(f"{i}. {result.get('title', 'No title')}")
        print(f"   URL: {result.get('url', 'No URL')}")
        print(f"   Content: {result.get('content', 'No content')[:150]}...")
        print()


# Example usage
if __name__ == "__main__":
    user_query = input("Enter your search query: ")
    search_results = search_searxng(user_query)
    display_results(search_results)
    
    # Optional: save results to a file
    save_option = input("Save results to file? (y/n): ").lower()
    if save_option == 'y':
        filename = input("Enter filename to save results: ")
        with open(filename, 'w') as f:
            json.dump(search_results, f, indent=2)
        print(f"Results saved to {filename}")    

# if __name__ == "__main__":
#     asyncio.run(main())