import os
from dotenv import load_dotenv

load_dotenv()
GPT_API_KEY = os.getenv("OPENAI_API_KEY")

# Configurazione del DB vettoriale
CHROMA_DB_DIRECTORY = os.getenv("CHROMA_DB_DIRECTORY", "db_marinetti")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "prodotti_marinetti")