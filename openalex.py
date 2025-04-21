from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("test-mcp-openalex", "0.1.0")

# Constants
OA_API_BASE = "https://api.openalex.org"


USER_AGENT = "openalex-search-app/1.0"
MAILTO_ADDRESS = "openalextest@gmail.com"

# Define the OpenAlex API endpoints
ENDPOINTS = {
    "works": "/works",
    "authors": "/authors",
    "venues": "/venues",
    "institutions": "/institutions",
    "concepts": "/concepts",
    "ids": "/ids",
}
# Define the OpenAlex API parameters
PARAMS = {
    "works": {
        "filter": ["doi", "title", "abstract"],
        "sort": ["relevance", "date"],
        "page": 1,
        "per_page": 10,
    },
    "authors": {
        "filter": ["orcid", "name"],
        "sort": ["relevance", "date"],
        "page": 1,
        "per_page": 10,
    },
    # Add other endpoints and their parameters as needed
}
# Define the OpenAlex API response structure
RESPONSE_STRUCTURE = {
    "works": {
        "id": str,
        "doi": str,
        "title": str,
        "abstract": str,
        "authors": list,
        "publication_date": str,
    },
    "authors": {
        "id": str,
        "orcid": str,
        "name": str,
        "works_count": int,
    },
    # Add other endpoints and their response structures as needed
}

async def fetch_openalex_data(endpoint: str, params: dict = None) -> Any:
    """
    Fetch data from OpenAlex API.

    Args:
        endpoint (str): The API endpoint to fetch data from.
        params (dict, optional): Additional query parameters for the request.

    Returns:
        Any: The parsed JSON response from the API.
    """
    url = f"{OA_API_BASE}/{endpoint}"
    headers = {
        "User-Agent": USER_AGENT,
        "Mailto": MAILTO_ADDRESS,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

@mcp.tool("openalex_search")
async def openalex_search(query: str, endpoint: str = "works", params: dict = None) -> Any:
    """
    Search OpenAlex API for a given query.

    Args:
        query (str): The search query.
        endpoint (str): The API endpoint to search.
        params (dict, optional): Additional query parameters for the request.

    Returns:
        Any: The parsed JSON response from the API.
    """
    if endpoint not in ENDPOINTS:
        raise ValueError(f"Invalid endpoint: {endpoint}")

    # Set default parameters if not provided
    if params is None:
        params = PARAMS[endpoint]

    # Add query to parameters
    params["search"] = query

    # Fetch data from OpenAlex API
    data = await fetch_openalex_data(ENDPOINTS[endpoint], params)
    
    if not data or "results" not in data:
        raise ValueError(f"No data found for query: {query}")
    


    
    return data    

def format_work(data: Any) -> str:
    """
    Format the response for a single work.

    Args:
        data (Any): The response data from OpenAlex API.

    Returns:
        str: Formatted string of the work.
    """
    if not data:
        return "No data found."
    return f"""
    Title: {data.get('title', 'N/A')}
    DOI: {data.get('doi', 'N/A')}
    Journal: {data.get('journal', 'N/A')}
    Authors: {', '.join([author['name'] for author in data.get('authors', [])])}
    Publication Date: {data.get('publication_date', 'N/A')}
    """
    
def format_works_response(data: Any) -> str:
    """
    Format the response for works.

    Args:
        data (Any): The response data from OpenAlex API.

    Returns:
        str: Formatted string of works.
    """
    works = data.get("results", [])
    formatted_works = []
    
    for work in works:
        formatted_works.append(format_work(work))

    found_works = "Number of works found: " + str(len(works))
    if not works:
        return "No works found."

    return "\n---\n".join(formatted_works) + "\n" + found_works


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')   
    

