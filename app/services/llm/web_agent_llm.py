from app.services.llm.base_llm import BaseLLM
from app.services.search_service import SearchService
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebAgentLLM(BaseLLM):
    """Web agent LLM service for handling web searches and providing up-to-date information"""
    
    def __init__(self):
        """Initialize the web agent LLM with search service"""
        super().__init__(model_name="gemini-1.5-flash", is_main=False)  # WebAgent doesn't need history, it's not a multiturn chat
        self.search_service = SearchService()
        
    def process_web_query(self, query: str, max_extractions: int = 3, max_content_length: int = 2000) -> str:
        """
        Process a web query and return information from the web with detailed content extraction
        
        Args:
            query: User's query to search for
            max_extractions: Maximum number of web pages to extract detailed content from
            max_content_length: Maximum length of content to extract from each page
            
        Returns:
            Comprehensive response based on extracted web content
        """
        try:
            # Detect if query is not in English and keep it as is, rather than generating a search query
            is_likely_english = all(ord(char) < 128 for char in query if char.isalpha())
            
            if is_likely_english:
                # For English queries, generate an optimized search query
                logger.info(f"Original query: {query}")
                search_query = self.generate_response(
                    f"Convert this user query into an effective web search query. Only respond with the search query, nothing else: {query}"
                )
                logger.info(f"Generated search query: {search_query}")
            else:
                # For non-English queries, use the original query
                search_query = query
                logger.info(f"Using original non-English query for search: {search_query}")
                
            # Perform web search with enhanced content extraction
            detailed_results = self.search_service.search_and_extract(
                search_query, 
                max_extractions=max_extractions, 
                max_content_length=max_content_length
            )
            
            # Try with original query if generated query didn't get results
            if not detailed_results and is_likely_english and search_query != query:
                logger.info("No results with generated query, trying original query")
                detailed_results = self.search_service.search_and_extract(
                    query, 
                    max_extractions=max_extractions, 
                    max_content_length=max_content_length
                )
            
            # If still no results, return a helpful message
            if not detailed_results:
                return f"""I couldn't find specific information for your query: "{query}".

Here are some suggestions:
- Try rewording your search terms
- Try using more general keywords
- If searching in a language other than English, you might try an English equivalent
- Use specific names, titles, or concepts rather than broad descriptions

Since I couldn't retrieve web results, I'll answer based on my training:
{self.generate_response(f"Answer this query without using web search: {query}")}"""
            
            # Format extracted content as context with prominently displayed URLs
            web_context = "Web search results:\n\n"
            
            for i, result in enumerate(detailed_results, 1):
                if isinstance(result, dict):
                    # Add title with source number
                    web_context += f"[Source {i}] {result.get('title', 'No title')}\n"
                    
                    # Highlight the URL
                    url = result.get('url', '#')
                    web_context += f"URL: {url}\n"
                    
                    # Add extracted content if available, otherwise use snippet
                    if result.get("extraction_status") == "success" and result.get("extracted_content"):
                        # Use extracted content (truncated if very long)
                        content = result["extracted_content"]
                        if len(content) > 1500:  # Limit context size per source
                            content = content[:1500] + "... (content truncated)"
                        web_context += f"Content:\n{content}\n\n"
                    else:
                        # Fallback to snippet
                        web_context += f"Summary: {result.get('snippet', 'No description available')}\n\n"
                else:
                    # For string format, ensure we extract and display the URL
                    text_parts = str(result).split("URL: ")
                    source_text = text_parts[0]
                    url = text_parts[1] if len(text_parts) > 1 else "#"
                    
                    web_context += f"[Source {i}]\n{source_text}\n"
                    web_context += f"URL: {url}\n\n"
            
            # Create prompt for the LLM to synthesize information
            language_instruction = "" if is_likely_english else f"Respond in the same language as the query: '{query}'"
            
            prompt = f"""
            Based on these detailed web search results, provide a comprehensive and accurate answer to the query: "{query}"
            
            {web_context}
            Please synthesize the information from these sources into a helpful response that directly addresses the query.
            Include only factual information from the sources. If the sources contradict each other, acknowledge this.
            If the web content contains relevant quotations or statistics, include them.
            Cite source numbers [Source X] when referencing specific information.
            Make sure to include the URL when citing information from a specific source, using this format: [Source X: URL]
            {language_instruction}
            """
            
            # Generate response without using chat history
            response = self.generate_response(prompt)
            
            return response
            
        except Exception as e:
            logger.exception(f"Error in process_web_query: {str(e)}")
            return f"""I encountered an error while trying to search for information about your query: "{query}".

Here's my best response based on my training knowledge without web search:
{self.generate_response(f"Answer this query without using web search: {query}")}"""

# Ensure the class is exported
__all__ = ['WebAgentLLM']