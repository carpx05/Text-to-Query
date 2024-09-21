import os
import sys
import json
import logging
from typing import List, Any
import faiss
from sentence_transformers import SentenceTransformer
from decimal import Decimal
import datetime

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_dir)
from config import Config


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super(CustomEncoder, self).default(obj)

class FAISSConnector:
    def __init__(self):
        self.model_name = Config.FAISS_MODEL_NAME
        self.index_file = Config.FAISS_INDEX_FILE
        self.data_file = Config.FAISS_DATA_FILE
        self.model = None
        self.index = None

    def _load_model(self):
        """Load the SentenceTransformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded SentenceTransformer model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            raise

    def _encode_data(self, data: List[Any]) -> faiss.IndexFlatIP:
        """Encode the data and create a FAISS index."""
        try:
            texts = [json.dumps(item, cls=CustomEncoder) for item in data]
            vectors = self.model.encode(texts)
            faiss.normalize_L2(vectors)

            dimension = vectors.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(vectors)

            logger.info(f"Encoded {len(data)} items and created FAISS index")
            return index
        except Exception as e:
            logger.error(f"Failed to encode data and create FAISS index: {e}")
            raise

    def store_in_faiss(self, data: List[Any]):
        """Store data in FAISS index and save to disk."""
        try:
            self._load_model()
            self.index = self._encode_data(data)

            faiss.write_index(self.index, self.index_file)
            logger.info(f"Saved FAISS index to {self.index_file}")

            with open(self.data_file, "w") as f:
                json.dump(data, f, cls=CustomEncoder)
            logger.info(f"Saved original data to {self.data_file}")

            logger.info(f"Successfully stored {len(data)} items in FAISS index")
        except Exception as e:
            logger.error(f"Failed to store data in FAISS: {e}")
            raise

    def delete_faiss_index(self):
        """Delete FAISS index and associated data file."""
        try:
            if os.path.exists(self.index_file):
                os.remove(self.index_file)
                logger.info(f"Deleted FAISS index file: {self.index_file}")
            else:
                logger.warning(f"FAISS index file not found: {self.index_file}")

            if os.path.exists(self.data_file):
                os.remove(self.data_file)
                logger.info(f"Deleted associated data file: {self.data_file}")
            else:
                logger.warning(f"Associated data file not found: {self.data_file}")

            self.index = None
            logger.info("FAISS index and associated data have been deleted.")
        except Exception as e:
            logger.error(f"Failed to delete FAISS index and associated data: {e}")
            raise

    def load_faiss_index(self):
        """Load FAISS index from disk."""
        try:
            if os.path.exists(self.index_file):
                self.index = faiss.read_index(self.index_file)
                logger.info(f"Loaded FAISS index from {self.index_file}")
            else:
                logger.warning(f"FAISS index file not found: {self.index_file}")
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            raise

    def search_faiss(self, query: str, k: int = 5) -> List[Any]:
        """Search the FAISS index for similar items."""
        try:
            if self.index is None:
                self.load_faiss_index()

            if self.model is None:
                self._load_model()

            query_vector = self.model.encode([query])
            faiss.normalize_L2(query_vector)

            distances, indices = self.index.search(query_vector, k)

            with open(self.data_file, "r") as f:
                data = json.load(f)

            results = [data[i] for i in indices[0]]
            logger.info(f"Performed FAISS search with query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to perform FAISS search: {e}")
            raise

# Usage example
if __name__ == "__main__":
    faiss_manager = FAISSManager()
    
    # Store data
    data_to_store = [{"id": 1, "text": "Example 1"}, {"id": 2, "text": "Example 2"}]
    faiss_manager.store_in_faiss(data_to_store)
    
    # Search
    results = faiss_manager.search_faiss("Example", k=1)
    print(f"Search results: {results}")
    
    # Delete index
    faiss_manager.delete_faiss_index()