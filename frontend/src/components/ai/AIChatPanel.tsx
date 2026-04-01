import { useState } from "react";
import { motion } from "framer-motion";
import { api } from "../../services/api";
import { useScanStore } from "../../stores/scanStore";

export function AIChatPanel() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; text: string }[]>([]);
  const [streaming, setStreaming] = useState(false);
  const quickResult = useScanStore((s) => s.quickResult);

  const send = async () => {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");
    const history = [...messages, { role: "user" as const, text }];
    setMessages([...history, { role: "assistant", text: "" }]);
    setStreaming(true);
    let acc = "";
    await api.chatStream(
      history.map((x) => ({ role: x.role, content: x.text })),
      (chunk) => {
        acc += chunk;
        setMessages((m) => {
          const copy = [...m];
          copy[copy.length - 1] = { role: "assistant", text: acc };
          return copy;
        });
      }
    );
    setStreaming(false);
  };

  const recommendations = async () => {
    if (!quickResult) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Сначала выполните быстрое сканирование." },
      ]);
      return;
    }
    setStreaming(true);
    let acc = "";
    setMessages((m) => [...m, { role: "assistant", text: "" }]);
    await api.recommendationsStream(quickResult, (chunk) => {
      acc += chunk;
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = { role: "assistant", text: acc };
        return copy;
      });
    });
    setStreaming(false);
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "minmax(200px, 260px) 1fr", gap: 12 }}>
      <aside className="glass-panel fade-in" style={{ padding: 14 }}>
        <h3 style={{ marginTop: 0 }}>Контекст</h3>
        {quickResult ? (
          <p style={{ fontSize: 14, opacity: 0.85 }}>
            Есть результаты быстрого скана: {quickResult.total_files} файлов.
          </p>
        ) : (
          <p style={{ fontSize: 14, opacity: 0.75 }}>Нет данных сканирования.</p>
        )}
        <button type="button" className="glass-button" style={{ width: "100%" }} onClick={recommendations} disabled={streaming}>
          Рекомендации по бэкапу
        </button>
      </aside>
      <section className="glass-panel fade-in" style={{ padding: 16, display: "flex", flexDirection: "column", minHeight: 420 }}>
        <h2 style={{ marginTop: 0 }}>AI Assistant</h2>
        <div style={{ flex: 1, overflow: "auto", marginBottom: 12 }}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                marginBottom: 10,
                padding: 10,
                borderRadius: 12,
                background:
                  msg.role === "user" ? "rgba(0,122,255,0.2)" : "rgba(255,255,255,0.06)",
              }}
            >
              <div style={{ fontSize: 12, opacity: 0.6, marginBottom: 4 }}>
                {msg.role === "user" ? "Вы" : "AI"}
              </div>
              <div style={{ whiteSpace: "pre-wrap" }}>{msg.text}</div>
            </motion.div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            className="glass-input"
            style={{ flex: 1 }}
            placeholder="Спросите про файлы или бэкап…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <button type="button" className="glass-button glass-button-primary" onClick={send} disabled={streaming}>
            Отправить
          </button>
        </div>
      </section>
    </div>
  );
}
