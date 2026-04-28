import lancedb
import os
import pyarrow as pa
from loguru import logger
import threading

class CodeIndexer:
    """Indexes codebase files into a local LanceDB for semantic search."""

    def __init__(self, db_path: str = ".lancedb"):
        self.db_path = db_path
        self.db = lancedb.connect(self.db_path)
        self.table_name = "codebase"
        
        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("file_path", pa.string()),
            pa.field("content", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 1536)) # Example OpenAI embedding size
        ])
        
        if self.table_name not in self.db.table_names():
            self.table = self.db.create_table(self.table_name, schema=schema)
            logger.info("Created new LanceDB table for codebase.")
        else:
            self.table = self.db.open_table(self.table_name)
            logger.info("Opened existing LanceDB table.")

    def _mock_embed(self, text: str) -> list[float]:
        """In a real implementation, call OpenAI/Ollama embeddings API."""
        return [0.0] * 1536

    def index_directory_background(self, directory: str):
        """Starts a background thread to index the directory."""
        thread = threading.Thread(target=self._index_directory, args=(directory,))
        thread.daemon = True
        thread.start()
        logger.info(f"Started background indexing for {directory}")

    def _index_directory(self, directory: str):
        data = []
        try:
            for root, _, files in os.walk(directory):
                if ".git" in root or "__pycache__" in root or ".venv" in root:
                    continue
                for file in files:
                    if not file.endswith((".py", ".js", ".ts", ".md", ".json")):
                        continue
                        
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if len(content) > 10000: # Skip huge files for now
                                continue
                            
                            vector = self._mock_embed(content)
                            data.append({
                                "id": file_path,
                                "file_path": file_path,
                                "content": content,
                                "vector": vector
                            })
                    except Exception:
                        pass
            
            if data:
                self.table.add(data)
                logger.info(f"Indexed {len(data)} files successfully.")
        except Exception as e:
            logger.error(f"Error during indexing: {e}")

    def search(self, query: str, limit: int = 3) -> list[dict]:
        """Searches the codebase."""
        query_vector = self._mock_embed(query)
        try:
            results = self.table.search(query_vector).limit(limit).to_list()
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
