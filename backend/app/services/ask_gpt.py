from openai import OpenAI
from app.config import GPT_API_KEY
from app.create_embeddings import get_chroma_collection
import random

# Inizializza il client OpenAI
client = OpenAI(api_key=GPT_API_KEY)
chat_history = []

# Ottieni la collezione Chroma
chroma_collection = get_chroma_collection()

def ask_gpt(message: str) -> str:
    print(f"messaggio: {message}")

    # Embedding
    embedding_response = client.embeddings.create(
        input=[message],
        model="text-embedding-3-small",
        dimensions=768
    )
    embedding = embedding_response.data[0].embedding
    print(f"📏 Embedding dimensione: {len(embedding)}")

    # Query su Chroma
    result = chroma_collection.query(
        query_embeddings=[embedding],
        n_results=5
    )

    # Prepara il contesto
    top_docs = random.sample(result["documents"][0], k=min(3, len(result["documents"][0])))
    contesto = "\n".join(top_docs)

    # Costruisci il prompt
    prompt = f"""
    Sei l’assistente virtuale dello studio dentistico Marinetti Dental di Viterbo.
    Rispondi a domande su trattamenti, tecnologie, prevenzione, prodotti e prezzi indicativi.
    Offri spiegazioni professionali ma accessibili anche a chi non è del settore.

    Ecco alcune informazioni da usare per rispondere:
    {contesto}

    DOMANDA: {message}
    """

    SYSTEM_PROMPT = """
    Sei l’assistente virtuale di Marinetti Dental, uno studio dentistico moderno con sede a Viterbo.

    📍 Indirizzo: Via Roncone 18A, 01100 Viterbo  
    📞 Tel: 0761 000000  
    📧 Email: info@marinettidental.it  
    🌐 Sito: www.marinettidental.it  
    🕐 Orari: Lun–Ven 08:30–19:00, Sabato solo su appuntamento, Domenica chiuso  

    ✅ Fornisci informazioni dettagliate su trattamenti, tecnologie usate, prevenzione e prodotti per l’igiene orale.  
    ✅ Puoi dare prezzi indicativi (se disponibili nei dati), specificando che sono da listino.  
    ✅ Se ti chiedono prenotazioni, invitali a chiamare lo studio.  
    ✅ Se possibile, dai spiegazioni tecniche ma chiare, come fosse una scheda informativa.  
    ❌ Non fare diagnosi personalizzate.  
    ⚠️ Se non sei sicuro, consiglia sempre di rivolgersi allo studio.  

    Rispondi in modo cordiale, professionale e sintetico. Non ripetere i dati dell’azienda se non serve.
    """

    chat_history.append({"role": "user", "content": prompt})

    if len(chat_history) > 6:
        chat_history[:] = chat_history[-6:]

    chat = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *chat_history
        ],
        temperature=0.7
    )

    reply = chat.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    return reply
