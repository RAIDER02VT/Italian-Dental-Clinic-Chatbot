import os
from dotenv import load_dotenv

load_dotenv()

GPT_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "prodotti_info_dentista")

# Base directory = cartella backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔥 Qui la vera soluzione:
cartella_db = os.getenv("CHROMA_DB_DIRECTORY", "chroma_db")
CHROMA_DB_DIRECTORY = (
    cartella_db if os.path.isabs(cartella_db) else os.path.join(BASE_DIR, cartella_db)
)

# ✅ Stampalo per debug se vuoi
print("📂 CHROMA_DB_DIRECTORY =", CHROMA_DB_DIRECTORY)
