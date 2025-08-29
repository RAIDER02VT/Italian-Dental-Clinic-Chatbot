import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import "./App.css";
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

/** Normalizza il testo del bot:
 * - rimuove ``` triple backtick
 * - rimuove indentazioni da code-block
 * - compatta righe vuote multiple
 */
function normalizeBotText(input: string): string {
  if (!input) return "";
  let out = input.replace(/```[\s\S]*?```/g, (m) => m.replace(/```/g, ""));
  out = out.replace(/\r/g, "");
  out = out.replace(/^\s{4,}/gm, "");   // niente indentazione che crea <pre>
  out = out.replace(/\n[ \t]+/g, "\n"); // spazi dopo newline
  out = out.replace(/[ \t]+\n/g, "\n"); // spazi prima di newline
  out = out.replace(/\n{3,}/g, "\n\n"); // max 2 newline consecutivi
  return out.trim();
}

const App: React.FC = () => {
  const [domanda, setDomanda] = useState("");
  const [risposte, setRisposte] = useState<Risposta[]>([]);
  const [loading, setLoading] = useState(false);

  const endOfChatRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    endOfChatRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [risposte, loading]);

  const inviaDomanda = async () => {
    const domandaTrim = domanda.trim();
    if (!domandaTrim || loading) return;

    // Mostra subito la frase di attesa (unico loader)
    const frase = frasiAttesa[Math.floor(Math.random() * frasiAttesa.length)];
    setRisposte((prev) => [...prev, { domanda: domandaTrim, risposta: frase }]);
    setDomanda("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: domandaTrim }),
      });

      if (!res.ok) {
        const errorText = await res.text().catch(() => "");
        console.error("Errore backend:", res.status, errorText);
        setRisposte((prev) => {
          const ultime = [...prev];
          const idx = ultime.length - 1;
          ultime[idx] = {
            domanda: ultime[idx].domanda,
            risposta: `❌ Errore ${res.status}. Riprova tra poco.`,
          };
          return ultime;
        });
        return;
      }

      const data = await res.json();
      const rispostaPulita = normalizeBotText(String(data.risposta ?? ""));

      setRisposte((prev) => {
        const ultime = [...prev];
        const idx = ultime.length - 1;
        ultime[idx] = {
          domanda: ultime[idx].domanda,
          risposta: rispostaPulita || "⚠️ Nessuna risposta ricevuta.",
        };
        return ultime;
      });
    } catch (err) {
      console.error(err);
      setRisposte((prev) => {
        const ultime = [...prev];
        const idx = ultime.length - 1;
        ultime[idx] = {
          domanda: ultime[idx].domanda,
          risposta: "❌ Errore di rete. Controlla la connessione e riprova.",
        };
        return ultime;
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setRisposte([
      {
        risposta:
          "Ciao! Sono l'assistente di **Sileoni Dental**. Se hai dubbi su trattamenti, costi o prevenzione, scrivimi pure: sono qui per aiutarti!",
      },
    ]);
  }, []);

  return (
    <div className="chat-container">
      <div className="header">
        <img src={logo} alt="Sileoni Dental Logo" className="logo" />
        <h1>Sileoni Dental – Assistente Virtuale</h1>
      </div>

      <div className="chat-box" role="log" aria-live="polite">
        {risposte.map((r, i) => (
          <div key={i} className="msg-block">
            {r.domanda && <div className="msg-user">🧑‍⚕️ {r.domanda}</div>}
            <div className="msg-bot">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkBreaks]}
                components={{
                  code({ inline, children, ...props }) {
                    if (inline) return <code {...props}>{children}</code>;
                    // niente <pre>, niente box grigi
                    return <span {...props}>{children}</span>;
                  },
                  pre({ children }) {
                    return <>{children}</>;
                  },
                }}
              >
                {r.risposta}
              </ReactMarkdown>
            </div>
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
          aria-label="Inserisci domanda"
        />
        <button onClick={inviaDomanda} disabled={loading}>
          {loading ? "..." : "Invia"}
        </button>
      </div>
    </div>
  );
};

export default App;
