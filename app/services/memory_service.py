import chromadb
import os
import logging
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from pathlib import Path
import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MemoryService:
    def __init__(self):
        self.persist_dir = os.getenv("CHROMADB_PERSIST_DIR", "./chroma_db")
        self.collection_name = os.getenv("CHROMADB_COLLECTION", "memory")
        self.client = None
        self.collection = None
        self.embedding_function = None
        
        # Ensure persist directory exists
        Path(self.persist_dir).mkdir(exist_ok=True)
        
        # Configure Gemini API key for embeddings
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    def initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            logger.info(f"Initializing ChromaDB with persist directory: {self.persist_dir}")
            
            # Create persistent client with telemetry disabled
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Set up embedding function for Gemini
            self._setup_embedding_function()
            
            # Check if collection exists first
            collections = self.client.list_collections()
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            # Get or create collection without throwing exception
            if collection_exists:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Connected to existing ChromaDB collection '{self.collection_name}'")
            else:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Created new ChromaDB collection '{self.collection_name}'")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
    
    def _setup_embedding_function(self):
        """Set up the embedding function for Gemini"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not found, embedding function may not work properly")
            
            # Use ChromaDB's built-in Google embedding function
            self.embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=api_key,
                task_type="retrieval_query"
            )
            logger.info("Successfully set up Gemini embedding function")
        except Exception as e:
            logger.error(f"Error setting up embedding function: {str(e)}")
            self.embedding_function = None
    
    def store_interaction(self, message: str, role: str):
        """Store a single message (user or AI) in ChromaDB with timestamp metadata"""
        try:
            if not self.collection:
                self.initialize()
            
            # Get current timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Create unique ID for this message
            message_id = f"{role}_{timestamp}_{str(uuid.uuid4())[:8]}"
            
            # Store in ChromaDB with role and timestamp metadata
            self.collection.add(
                documents=[message],
                metadatas=[{
                    "role": role,  # "user" or "model"
                    "timestamp": timestamp
                }],
                ids=[message_id]
            )
            
            logger.info(f"Stored {role} message in ChromaDB with ID {message_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing message in ChromaDB: {str(e)}")
            return False
    
    def get_relevant_context(self, query: str, n_results: int = 8, where: Optional[Dict[str, Any]] = None):
        """Retrieve relevant context based on query"""
        try:
            if not self.collection:
                self.initialize()
                
            # Check if collection is empty
            collection_data = self.collection.get()
            if len(collection_data['ids']) == 0:
                logger.info("ChromaDB collection is empty, no context to retrieve")
                return ""
            
            # Format the where parameter if provided
            formatted_where = None
            if where:
                formatted_where = {}
                for key, value in where.items():
                    if value is not None:
                        formatted_where[key] = {"$eq": value}
            
            # Make sure query isn't empty (ChromaDB requires non-empty query)
            if not query:
                query = " "  # Use a space as minimal content if empty
            
            # Query ChromaDB for similar contexts
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=formatted_where
            )
            
            # Format results
            if results and results['documents'] and len(results['documents'][0]) > 0:
                # Include metadata like role and timestamp in the context
                formatted_results = []
                for i, doc in enumerate(results['documents'][0]):
                    if results['distances'][0][i] > 0.4:
                        continue
                    role = results['metadatas'][0][i].get('role', 'unknown')
                    timestamp = results['metadatas'][0][i].get('timestamp', 'unknown time')
                    formatted_results.append(f"[{role} at {timestamp}]: {doc}")
                
                context = "\n\n".join(formatted_results)
                logger.info(f"Retrieved {len(formatted_results)} relevant context items")
                return context
            
            logger.info("No relevant context found")
            return ""
        except Exception as e:
            logger.error(f"Error retrieving context from ChromaDB: {str(e)}")
            return ""
    