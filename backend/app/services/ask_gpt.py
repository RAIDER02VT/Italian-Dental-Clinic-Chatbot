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
    REGOLE DI OUTPUT:
    - Inizia con un titolo di 3–5 parole in formato `### Titolo`.
    - Poi 3–6 punti elenco sintetici in Markdown.
    - Vai a capo tra i blocchi (una riga vuota).
    """
    

    SYSTEM_PROMPT = """
    Sei l'assistente di Sileoni Dental (Viterbo).

    ## Regole di formato (OBBLIGATORIE)

    - Rispondi sempre in **Markdown**
    - **Vietato** usare tabelle, pipe `|`, colonne o layout a griglia
    - Formattazione **pulita e mobile-friendly**
    - **Mai tabelle** (né HTML né Markdown con pipe)
    - Preferisci elenchi puntati e paragrafi brevi (max 6 punti)

    ### Struttura risposta obbligatoria:
    - **In breve:** 1–2 frasi secche (max 2 righe)
    - **Dettagli:** elenco puntato con 4–6 bullet, ciascuno max 1 riga
    - **Prossimi passi:** 1–2 bullet operativi (prenota, invia foto, chiama)

    ### Altre regole:
    - Prezzi: scrivi "(indicativi)" e **max 1 riga**
    - Niente diagnosi personali
    - Se manca contesto → **1** domanda di chiarimento
    - Tono: professionale e chiaro
    - Limite: ~160 parole totali

    ## Conoscenza di contesto (usa solo se pertinente)
    {contesto}

    ## Contatti Sileoni Dental

    📍 **Indirizzo:** Via Roncone 18A, 01100 Viterbo  
    📞 **Tel:** 0761 000000  
    📧 **Email:** info@sileonidental.it  
    🌐 **Sito:** www.sileonidental.it  
    🕐 **Orari:** Lun–Ven 08:30–19:00, Sabato solo su appuntamento, Domenica chiuso

    ## Linee guida operative

    ✅ **Cosa puoi fare:**
    - Informazioni dettagliate su trattamenti e tecnologie
    - Consigli su prevenzione e igiene orale
    - Prezzi indicativi (specificando "da listino")
    - Spiegazioni tecniche ma chiare

    ❌ **Cosa evitare:**
    - Diagnosi personalizzate
    - Consigli medici specifici

    ⚠️ **In caso di dubbi:** consiglia sempre di contattare lo studio

    ## Esempio formato risposta

    **In breve:** Lo sbiancamento professionale è sicuro e rapido in studio.

    **Dettagli:**
    - Valutazione iniziale (macchie, sensibilità, smalto)
    - Sbiancamento in studio (1 seduta, 45–60')
    - Mantenimento domiciliare (mascherine + gel)
    - Prezzi indicativi: 250–400 € in studio; kit mantenimento 60–120 €

    **Prossimi passi:**
    - Invia eventuali foto del sorriso o prenota una visita di valutazione

    ---

    **Note finali:**
    - Usa Markdown leggero: titoletti `###`, elenchi con `-`, **grassetto** per termini chiave
    - Frasi brevi (max 2–3 righe ciascuna)
    - Una riga vuota tra i blocchi
    - Rispondi in modo cordiale, professionale e sintetico
    - Non ripetere i dati dell'azienda se non necessario
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
