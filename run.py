import uvicorn
import os
from pathlib import Path

# Create necessary directories
data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

chroma_dir = Path(os.getenv("CHROMADB_PERSIST_DIR", "./chroma_db"))
chroma_dir.mkdir(exist_ok=True)

if __name__ == "__main__":
    print("Starting Personal AI Assistant...")
    print("Access the web interface at http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)