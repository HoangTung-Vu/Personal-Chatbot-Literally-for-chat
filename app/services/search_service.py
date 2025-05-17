import os
import requests
import json
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SearchService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.max_results = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        
        # Log configuration status
        if not self.api_key:
            logger.warning("GOOGLE_SEARCH_API_KEY not found in environment variables")
        if not self.search_engine_id:
            logger.warning("GOOGLE_SEARCH_ENGINE_ID not found in environment variables")
        
    def search_web(self, query: str) -> List[Dict[str, str]]:
        """Search the web using Google Search API and return a list of search result dictionaries"""
        try:
            if not self.api_key or not self.search_engine_id:
                logger.error("Google Search API credentials not configured")
                return []
            
            logger.info(f"Performing web search for query: {query}")
                
            # Build search URL
            search_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": self.max_results
            }
            
            # Make request to Google Search API
            logger.debug(f"Sending request to Google Search API...")
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Error in Google Search API: {response.status_code}: {response.text}")
                return []
            
            # Parse results
            search_results = response.json()
            if "items" not in search_results:
                logger.warning("No search results found")
                return []
            
            logger.info(f"Found {len(search_results['items'])} search results")
                
            # Format results as dictionaries
            formatted_results = []
            for item in search_results["items"]:
                result = {
                    "title": item.get("title", "No title available"),
                    "snippet": item.get("snippet", "No description available"),
                    "url": item.get("link", "#"),
                    "source": item.get("displayLink", "Unknown source")
                }
                formatted_results.append(result)
                
            return formatted_results
        
        except requests.exceptions.Timeout:
            logger.error("Request to Google Search API timed out")
            return []
        except requests.exceptions.ConnectionError:
            logger.error("Connection error while contacting Google Search API")
            return []
        except json.JSONDecodeError:
            logger.error("Failed to parse response from Google Search API")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error in web search: {str(e)}")
            return []
            
    def extract_content_from_url(self, url: str, max_content_length: int = 5000) -> Dict[str, Any]:
        """
        Extract content from a URL
        
        Args:
            url: The URL to extract content from
            max_content_length: Maximum length of content to extract
            
        Returns:
            Dictionary containing title, content, and status
        """
        result = {
            "title": "",
            "content": "",
            "status": "error",
            "url": url
        }
        
        try:
            logger.info(f"Extracting content from URL: {url}")
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Check if content is HTML
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type.lower():
                result["content"] = f"Content type is not HTML: {content_type}"
                return result
            
            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            result["title"] = title_tag.text if title_tag else "No title found"
            
            # Extract main content
            # Try some common content containers
            main_content = None
            for selector in ['article', 'main', '.content', '#content', '.post', '.article', '.entry-content']:
                content = soup.select_one(selector)
                if content:
                    main_content = content
                    break
                    
            if not main_content:
                # Fallback to body if no specific content container found
                main_content = soup.body
                
            if main_content:
                # Remove script, style, and nav elements
                for element in main_content.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    element.decompose()
                
                # Get text
                content = main_content.get_text(separator='\n', strip=True)
                
                # Truncate if too long
                if len(content) > max_content_length:
                    content = content[:max_content_length] + "... [content truncated]"
                
                result["content"] = content
                result["status"] = "success"
            else:
                result["content"] = "Failed to extract main content"
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out")
            result["content"] = "Request timed out"
            return result
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error while contacting {url}")
            result["content"] = "Connection error"
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while contacting {url}: {str(e)}")
            result["content"] = f"Request error: {str(e)}"
            return result
        except Exception as e:
            logger.exception(f"Unexpected error extracting content from {url}: {str(e)}")
            result["content"] = f"Error extracting content: {str(e)}"
            return result
            
    def search_and_extract(self, query: str, max_extractions: int = 3, max_content_length: int = 5000) -> List[Dict[str, Any]]:
        """
        Search the web and extract content from the top results
        
        Args:
            query: The search query
            max_extractions: Maximum number of URLs to extract content from
            max_content_length: Maximum length of content to extract from each URL
            
        Returns:
            List of dictionaries containing search results with extracted content
        """
        # Search the web
        search_results = self.search_web(query)
        
        # Limit the number of extractions
        results_to_process = search_results[:max_extractions]
        
        # Extract content from each result
        for result in results_to_process:
            url = result["url"]
            extracted = self.extract_content_from_url(url, max_content_length)
            
            # Update the search result with extracted content
            result["extracted_title"] = extracted["title"]
            result["extracted_content"] = extracted["content"]
            result["extraction_status"] = extracted["status"]
            
        return search_results

# # Test function
# def main():
#     logger.info("Testing search service...")
    
#     # Create an instance of SearchService
#     search_service = SearchService()
    
#     # Check if API credentials are available
#     if not search_service.api_key or not search_service.search_engine_id:
#         logger.error("API credentials not available. Please set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables.")
#         print("\nEnvironment variables needed:")
#         print("GOOGLE_SEARCH_API_KEY - Your Google API key")
#         print("GOOGLE_SEARCH_ENGINE_ID - Your custom search engine ID")
#         print("MAX_SEARCH_RESULTS - (Optional) Number of results to return (default: 5)")
#         return
    
#     print("\n1. Simple search test")
#     # Test query
#     test_query = "latest advancements in artificial intelligence"
#     print(f"\nPerforming simple search for: '{test_query}'")
    
#     # Execute search
#     results = search_service.search_web(test_query)
    
#     # Display results
#     if results:
#         print(f"\nSearch returned {len(results)} results:")
#         for i, result in enumerate(results, 1):
#             print(f"\nResult {i}:")
#             print(f"- Title: {result['title']}")
#             print(f"- Snippet: {result['snippet']}")
#             print(f"- URL: {result['url']}")
#     else:
#         print("\nNo results found or an error occurred.")
        
#     print("\n2. Search and extract content test")
#     print(f"\nPerforming search with content extraction for: '{test_query}'")
    
#     # Execute search with content extraction
#     detailed_results = search_service.search_and_extract(test_query, max_extractions=2)
    
#     # Display results with extracted content
#     if detailed_results:
#         print(f"\nSearch and extract returned {len(detailed_results)} results:")
#         for i, result in enumerate(detailed_results, 1):
#             print(f"\nResult {i}:")
#             print(f"- Title: {result['title']}")
#             print(f"- Snippet: {result['snippet']}")
#             print(f"- URL: {result['url']}")
            
#             if "extracted_content" in result and result["extraction_status"] == "success":
#                 print(f"\nExtracted Content:")
#                 print(f"- Extracted Title: {result['extracted_title']}")
#                 print(f"- Content Preview: {result['extracted_content'][:300]}...")
#             else:
#                 print("\nContent extraction failed or was not performed")
#     else:
#         print("\nNo results found or an error occurred.")

# if __name__ == "__main__":
#     main()