import pandas as pd
import re

df = pd.read_csv("../dati_marinetti.csv", sep=";", dtype= str)
df = df.fillna('')

def descrizione_prodotto(row):
    descrizione = row["Descrizione"].strip()
    descrizione_estesa = row["Descrizione estesa"].strip()
    marca = row["Marca"].strip()
    stato = row["Stato articolo"].strip()

    if stato == "In uso":
        frase = f"Il prodotto {descrizione} con descrizione {descrizione_estesa}"
        if marca is not None and marca.strip() != "":
            frase += f", della marca {marca}"
        else:
            frase += "."
    else:
        frase = ""


    frase = re.sub(r"\s+", " ", frase)
    frase = frase.replace(" .", ".")
    return frase

#applica la funzione su ogni riga
df["frasi_ai"] = df.apply(descrizione_prodotto, axis=1)

df["frasi_ai"].to_csv("../frasi.csv", sep=";", index = False, header=False)

# Messaggio finale (corretto)
print("✅ Frasi salvate nel file 'frasi.csv' con i dati del file 'dati_marinetti.csv'")
