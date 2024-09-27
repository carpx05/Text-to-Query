import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # FAISS index
    FAISS_MODEL_NAME = os.environ.get("FAISS_MODEL_NAME")
    FAISS_INDEX_FILE = os.environ.get("FAISS_INDEX_FILE")
    FAISS_DATA_FILE = os.environ.get("FAISS_DATA_FILE")

    # SQLite cache
    SQLITE_CACHE_FILE = os.getenv("SQLITE_CACHE_FILE")

    # MySQL connection
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

    # CSV directory
    CSV_DIRECTORY = os.environ.get("CSV_DIRECTORY")
    MAX_SAMPLE_ROWS: int = 10
    ENCODING = os.environ.get("CSV_ENCODING")
    CSV_DATA_DIRECTORY = os.environ.get("CSV_DATA_DIRECTORY")

    # Flask app
    FLASK_HOST = os.getenv("FLASK_HOST")

    # Google API key
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME")
