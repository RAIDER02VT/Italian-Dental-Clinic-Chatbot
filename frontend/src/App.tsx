import React, { useState, useEffect, useRef } from "react";
import "./dentistChat.css";
import logo from "./assets/logo.png";

interface Risposta {
  domanda?: string;
  risposta: string;
}

const frasiAttesa = [
  "🦷 Sto controllando i dati dei trattamenti...",
  "😷 Un attimo che elaboro la risposta...",
  "📋 Recupero le informazioni sui servizi richiesti...",
  "🔍 Analizzo le tue esigenze dentali...",
  "💬 Sto preparando una risposta precisa...",
  "⏳ Un momento, ti rispondo subito...",
  "📄 Consulto i dettagli clinici aggiornati...",
  "🦷 Cerco i dettagli più adatti per te...",
];

const App: React.FC = () => {
  const [domanda, setDomanda] = useState("");
  const [risposte, setRisposte] = useState<Risposta[]>([]);
  const [loading, setLoading] = useState(false);
  const [fraseAttesa, setFraseAttesa] = useState("");

  const endOfChatRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    endOfChatRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [risposte]);

  const inviaDomanda = async () => {
    if (!domanda.trim()) return;

    const frase = frasiAttesa[Math.floor(Math.random() * frasiAttesa.length)];
    setRisposte((prev) => [...prev, { domanda, risposta: frase }]);
    setDomanda("");
    setFraseAttesa(frase);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: domanda }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error("Errore backend:", res.status, errorText);
        alert(`Errore ${res.status}: ${errorText}`);
        setLoading(false);
        return;
      }

      const data = await res.json();

      setRisposte((prev) => {
        const ultime = [...prev];
        ultime[ultime.length - 1] = {
          domanda: ultime[ultime.length - 1].domanda,
          risposta: data.risposta,
        };
        return ultime;
      });

      setDomanda("");
    } catch (err) {
      alert("Errore nella richiesta");
      console.error(err);
    }

    setLoading(false);
    setFraseAttesa("");
  };

  useEffect(() => {
    const messaggioIniziale = {
      risposta: "Ciao! Sono il tuo assistente dentale digitale SmileCare. Se hai dubbi su trattamenti, costi o prevenzione, scrivimi pure: sono qui per aiutarti!",
    };
    setRisposte([messaggioIniziale]);
  }, []);

  return (
    <div className="chat-container">
      <div className="header">
        <img src={logo} alt="SmileCare Logo" className="logo" />
        <h1>SmileCare – Assistente Dentistico Virtuale</h1>
      </div>

      <div className="chat-box">
        {risposte.map((r, i) => (
          <div key={i} className="msg-block">
            {r.domanda && <div className="msg-user">🧑‍⚕️ {r.domanda}</div>}
            <div className="msg-bot">{r.risposta}</div>
          </div>
        ))}
        <div ref={endOfChatRef} />
      </div>

      <div className="input-row">
        <input
          type="text"
          placeholder="Scrivi la tua domanda sui trattamenti dentali..."
          value={domanda}
          onChange={(e) => setDomanda(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && inviaDomanda()}
          disabled={loading}
        />
        <button onClick={inviaDomanda} disabled={loading}>
          {loading ? "..." : "Invia"}
        </button>
      </div>
    </div>
  );
};

export default App;

