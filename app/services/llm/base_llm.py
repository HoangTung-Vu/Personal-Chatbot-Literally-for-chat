import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BaseLLM:
    """Base class for LLM services"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash", is_main: bool = True, history: Optional[List[Dict]] = None):
        """Initialize the LLM with a specific model"""
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
            
        # Initialize model
        if is_main:
            sysprompt_path = os.path.join(os.path.dirname(__file__), "private_system_prompt.txt")
            with open(sysprompt_path, "r", encoding="utf-8") as f:
                system_instruction = f.read()
            
            config = {
                "max_output_tokens": 512,
                "temperature": 0.8,
                "top_p": 0.95,
                "top_k": 40
            }
            self.model = genai.GenerativeModel(model_name, generation_config=config, system_instruction=system_instruction)
        else:
            system_instruction = """
            Bạn là một AI hỗ trợ tìm kiếm thông tin trên web. 
            Dựa vào thông tin từ user prompt hãy tạo một câu hỏi tìm kiếm trên web để tìm kiếm thông tin chính xác nhất phù hợp với yêu cầu của người dùng.
            (Yêu cầu tìm thông tin mới nhất)
            
            Bạn cũng phải tạo thông tin tổng hợp từ các kết quả tìm kiếm trên web để trả lời câu hỏi của người dùng, gửi về dưới dạng context cho mô hình chính.
            """
            config = { 
                "max_output_tokens": 512,
                "temperature": 0.1
            }
            self.model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
        self.is_main = is_main
        
        if is_main: 
            if history is None:
                history = []
            self.chat = self.model.start_chat(history=history)

        
    def generate_response(self, prompt: str) -> str:
        if self.is_main:
            # Generate response using the chat model
            try:
                response = self.chat.send_message(prompt)
                return response.text
            except Exception as e:
                print(f"Error generating response: {str(e)}")
                return f"I'm having trouble generating a response at the moment. Error: {str(e)}"
        else:
            # Generate response using the non-chat model
            try:
                # Using generate_content instead of generate
                response = self.model.generate_content(prompt)
                # Access text property correctly based on the API
                if hasattr(response, 'text'):
                    return response.text
                elif hasattr(response, 'parts'):
                    return ''.join(part.text for part in response.parts)
                else:
                    # Handle case where response structure is different
                    print("Response structure is unexpected:", type(response))
                    return str(response)
            except Exception as e:
                print(f"Error generating response: {str(e)}")
                return f"I'm having trouble generating a response at the moment. Error: {str(e)}"
