# backend/app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# root repo = due livelli sopra (backend/app -> root)
ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"

# carica .env dalla root
load_dotenv(ROOT_DIR / ".env")

# --- OpenAI ---
GPT_API_KEY = os.getenv("OPENAI_API_KEY", "")

# --- Chroma (path risolto rispetto a backend) ---
_cfg_dir = os.getenv("CHROMA_DB_DIRECTORY", "chroma_db_marinetti")
CHROMA_DB_DIRECTORY = (
    Path(_cfg_dir) if os.path.isabs(_cfg_dir) else (BACKEND_DIR / _cfg_dir)
)
CHROMA_DB_DIRECTORY = CHROMA_DB_DIRECTORY.resolve()

CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "prodotti_info_dentista")

# debug opzionale:
# print("📂 CHROMA_DB_DIRECTORY =", CHROMA_DB_DIRECTORY)
