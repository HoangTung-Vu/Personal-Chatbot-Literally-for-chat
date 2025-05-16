import os
import requests
import json
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SearchService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.max_results = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
        
    def search_web(self, query: str) -> List[str]:
        """Search the web using Google Search API and return a list of results"""
        try:
            if not self.api_key or not self.search_engine_id:
                print("Google Search API credentials not configured")
                return []
                
            # Build search URL
            search_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": self.max_results
            }
            
            # Make request to Google Search API
            response = requests.get(search_url, params=params)
            if response.status_code != 200:
                print(f"Error in Google Search API: {response.status_code}: {response.text}")
                return []
                
            # Parse results
            search_results = response.json()
            if "items" not in search_results:
                return []
                
            # Format results
            formatted_results = []
            for item in search_results["items"]:
                snippet = item.get("snippet", "No description available")
                title = item.get("title", "No title available")
                link = item.get("link", "#")
                formatted_results.append(f"- {title}\n  {snippet}\n  URL: {link}")
                
            return formatted_results
        
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return []