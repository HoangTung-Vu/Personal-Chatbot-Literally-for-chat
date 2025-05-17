from app.services.llm.base_llm import BaseLLM
from app.services.llm.web_agent_llm import WebAgentLLM
from app.services.memory_service import MemoryService

import datetime
from typing import List, Dict, Any, Optional

class MainLLM(BaseLLM):
    """Main LLM service for handling primary chat interactions"""
    
    def __init__(self, history: Optional[List[Dict]] = None):
        """Initialize the Main LLM with the memory service"""
        super().__init__(model_name="gemini-2.0-flash", is_main=True, history=history)  # Using faster model for main interactions
        self.memory_service = MemoryService()
        self.memory_service.initialize()  # Initialize the ChromaDB connection
        self.web_agent = WebAgentLLM()
        
    def process_chat(self, message: str, with_search: bool = True) -> str:
        """Process a chat message with memory context"""
        # Get current timestamp for context
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build context
        context_parts = [f"Current time: {current_time} \n"]
        
        if with_search:
            web_response = self.web_agent.process_web_query(message)
            context_parts.append(f"Web search results:\n{web_response}")

        # Add memory context if enabled
        memory_context = self.memory_service.get_relevant_context(message)
        if memory_context:
            context_parts.append(f"Memory context:\n{memory_context}")
        
        # Combine all context
        full_context = "\n\n".join(context_parts)
        print("Full context for LLM:", full_context)
        # Generate prompt with context
        prompt = f"Context information (use this to inform your response, but don't explicitly mention it):\n{full_context}\n\nUser message: {message}"
        
        # Generate response
        response = self.generate_response(prompt)
        
        # Store interaction in memory
        self.memory_service.store_interaction(message, "user")
        self.memory_service.store_interaction(response, "model")    
                
        return response