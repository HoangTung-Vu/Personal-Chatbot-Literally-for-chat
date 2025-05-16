from app.services.llm.base_llm import BaseLLM
from app.services.search_service import SearchService
from typing import List, Dict, Any, Optional

class WebAgentLLM(BaseLLM):
    """Web agent LLM service for handling web searches and providing up-to-date information"""
    
    def __init__(self):
        """Initialize the web agent LLM with search service"""
        super().__init__(model_name="gemini-2.0-pro", is_main=False)  # WebAgent doesn't need history, it's not a multiturn chat
        self.search_service = SearchService()
        
    def process_web_query(self, query: str) -> str:
        """Process a web query and return information from the web"""
        # Perform web search
        search_query = self.generate_response(query)
        search_results = self.search_service.search_web(search_query)
        
        if not search_results:
            return "I couldn't find any relevant information from web search. Please try a different query."
            
        # Format search results as context
        web_context = "Web search results:\n" + "\n".join(search_results)
        
        # Create prompt for the LLM to synthesize information
        prompt = f"""
        Based on these web search results, provide a comprehensive and accurate answer to the query: "{query}"
        
        {web_context}
        
        Please synthesize the information from these sources into a helpful response that directly addresses the query.
        Include only factual information from the sources. If the sources contradict each other, acknowledge this.
        Do not reference "the search results" or "the web search" in your answer.
        """
        
        # Generate response without using chat history
        response = self.generate_response(prompt)
        
        return response

# Ensure the class is exported
__all__ = ['WebAgentLLM']