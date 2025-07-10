import pandas as pd
import sys
import os
import platform
from openai import OpenAI
from app.config import GPT_API_KEY, CHROMA_DB_DIRECTORY, CHROMA_COLLECTION_NAME

# Fix per Codespaces: forza sqlite aggiornato solo se serve
if "CODESPACES" in os.environ or platform.system() != "Windows":
    try:
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    except ImportError:
        print("Modulo pysqlite3 non trovato, proseguo con sqlite3 standard")
# Ora puoi importare chromadb
import chromadb
import chromadb
from chromadb.config import Settings
from tqdm import tqdm
from pathlib import Path

# Inizializza OpenAI client
client = OpenAI(api_key=GPT_API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "..", "frasi.csv")

def create_chroma_collection():
    print("🔁 Creazione embedding da zero...")

    # Carica CSV
    df = pd.read_csv(csv_path, sep=";", header=None, names=["frase"])
    df = df.dropna(subset=["frase"]) 
    df = df[df["frase"].str.strip() != ""]
    frasi = df["frase"].tolist()

    # Inizializza ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIRECTORY)
    collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

    # Parametro batch
    batch_size = 300

    for batch_start in tqdm(range(0, len(frasi), batch_size), desc="🔁 Creazione embedding"):
        batch_end = min(batch_start + batch_size, len(frasi))
        batch = frasi[batch_start:batch_end]
        ids = [f"frase_{i}" for i in range(batch_start, batch_end)]

        try:
            response = client.embeddings.create(
                input=batch,
                model="text-embedding-3-small",
                dimensions=768
            )
            embeddings = [r.embedding for r in response.data]

            collection.add(
                documents=batch,
                ids=ids,
                embeddings=embeddings
            )

        except Exception as e:
            print(f"❌ Errore nel batch {batch_start}-{batch_end}: {e}")

    print("✅ Embedding completati e salvati nel database Chroma.")
    return collection

def get_chroma_collection():
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIRECTORY)
    return chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

# Questo codice viene eseguito **solo se lanci direttamente questo file**
if __name__ == "__main__":
    if not Path(CHROMA_DB_DIRECTORY).exists():
        create_chroma_collection()
    else:
        print("✅ ChromaDB già esistente. Nessuna creazione necessaria.")
