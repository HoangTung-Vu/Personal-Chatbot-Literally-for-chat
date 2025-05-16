# My AI - Personal AI Assistant

A versatile AI assistant application built with FastAPI that provides intelligent chat capabilities, web search integration, and memory persistence.

## Features

- 💬 **AI Chat Interface**: Conversational AI chat powered by large language models
- 🌐 **Web Search Integration**: Capability to search the web for up-to-date information
- 💾 **Persistent Memory**: Chat history stored in SQLite database
- 🖥️ **Modern Web Interface**: Clean and responsive UI built with HTML, CSS, and JavaScript
- 🚀 **Fast API Backend**: Built on FastAPI for high-performance API endpoints

## Project Structure

```
my_ai/
├── app/                    # Main application package
│   ├── api/                # API endpoints
│   │   └── chat.py         # Chat endpoints
│   ├── models/             # Data models
│   │   └── chat_models.py  # Chat request/response models
│   └── services/           # Service layer
│       ├── llm/            # Language model services
│       │   ├── base_llm.py
│       │   ├── main_llm.py
│       │   └── web_agent_llm.py
│       ├── memory_service.py
│       └── search_service.py
├── static/                 # Static web files
│   ├── css/
│   └── js/
├── templates/              # HTML templates
├── data/                   # Data storage (created at runtime)
├── requirements.txt        # Project dependencies
└── run.py                  # Application entry point
```

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd my_ai
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv myai
   source myai/bin/activate  # On Windows: myai\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following environment variables:
   ```
   API_KEY=your_google_ai_api_key
   # Add any other required environment variables
   ```

## Usage

1. Start the application:
   ```bash
   uvicorn run:app --reload
   ```

2. Open your browser and navigate to `http://localhost:8000`

3. Start chatting with your AI assistant!

## API Endpoints

- `GET /`: Main web interface
- `POST /api/chat`: Send a message to the AI and receive a response

## Dependencies

- FastAPI: Web framework for building APIs
- Uvicorn: ASGI server for FastAPI
- Google Generative AI: Integration with Google's generative AI models
- ChromaDB: Vector database for semantic search
- SQLite: Lightweight database for persistent storage
- And more in `requirements.txt`

## Development

To contribute to the project:

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

[Include your license information here]