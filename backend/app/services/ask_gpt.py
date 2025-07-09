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

    # Crea embedding da 1536 dimensioni (ada-002)
    embedding_response = client.embeddings.create(
        input=[message],
        model="text-embedding-3-small",
        dimensions=768
    )
    embedding = embedding_response.data[0].embedding
    print(f"📏 Embedding dimensione: {len(embedding)}")

    # Query su Chroma con l'embedding
    result = chroma_collection.query(
        query_embeddings=[embedding],
        n_results=5
    )

    # Prepara il contesto
    top_docs = random.sample(result["documents"][0], k=min(3, len(result["documents"][0])))
    contesto = "\n".join(top_docs)

    # Costruisci il prompt
    prompt = f"""
    Sei un assistente virtuale per una rivendita di materiale edile
    di Viterbo che si chiama Marinetti edilizia.
    Offri risposte su schede_tecniche, materiali, lavorazioni e contatti aziendali.
    Rispondi SEMPRE in italiano.
    Ecco alcune informazioni tecniche da tenere in considerazione:
    {contesto}
    DOMANDA: {message}
    """
    SYSTEM_PROMPT = """
                Sei l’assistente virtuale di Marinetti Edilizia, rivendita di materiali edili a Viterbo.

                📍 Indirizzo: St:Bagni 12b, 01100 Viterbo (VT)  
                📞 Tel: 0761 251285  
                📧 Email: vendite@marinetti.it  
                🕐 Orari: Lun–Ven 07:00–12:30 / 14:30–18:00, Sab 07:30–12:30, Dom chiuso  
                🌐 Sito: www.marinetti.it
                

                Se chiedono informazioni su trasporti:comunica che noi non facciamo trasporti ma ci apppoggiamo a dei trasportatori esterni e i principali sono:
                📞 Tel Quirino: 330737923
                📞 Tel Emanuele Boni: 3281316907
                📞 Tel Rosadini:3281630482

                Se chiedono informazioni sulle colle: Colle principali: Bioflex, Top progres, H40
                Sei un tecnico che deve dar consigli su lavorazioni ,come se fossi una scheda tecnica se ti chiedono come usare un prodotto
                
                ✅ Rispondi sempre in italiano, in modo tecnico ma chiaro.  
                ❌ Mai fornire prezzi (neanche approssimativi).  
                ❌ Mai dare garanzie.  
                    Includere solo link a schede tecniche.  
                ❌ Non diciamo mai “abbiamo tutto”: invita a chiedere un preventivo.  
                📄 Fornisci schede tecniche, consigli d’uso, spiegazioni sui materiali.  
                📦 Non facciamo noleggio.  
                ⚠️ Se non sai qualcosa, dillo chiaramente.  
                ⚠️ Le risposte sono solo a scopo informativo, nessuna responsabilità.
                    rispondi si con le informazioni dell'azienda ma non essere ripetitivo
                """
    chat_history.append({"role": "user", "content": prompt})

    if len(chat_history) > 6:
        chat_history[:] = chat_history[-6:]

    # Chiamata a GPT-4
    chat = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }, *chat_history
        ],
        temperature=0.7
    )

    reply = chat.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    return reply