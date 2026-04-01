import { useEffect, useState } from "react";
import { Globe } from "@phosphor-icons/react";
import { api } from "../../services/api";
import { formatBytes } from "../../utils/formatters";

interface Profile {
  name: string;
  path: string;
  has_passwords?: boolean;
  has_cookies?: boolean;
  has_history?: boolean;
}

interface BrowserRow {
  id: string;
  name: string;
  path: string;
  type: string;
  profiles: Profile[];
  total_size: number;
}

export function BrowserManager() {
  const [list, setList] = useState<BrowserRow[]>([]);
  const [dest, setDest] = useState("D:\\SuggyExport");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api
      .detectBrowsers()
      .then((r: { browsers: BrowserRow[] }) => setList(r.browsers ?? []))
      .catch(() => setList([]))
      .finally(() => setLoading(false));
  }, []);

  const exportProfile = async (browserId: string, profileName: string) => {
    setMessage("Экспорт…");
    try {
      const res = await api.exportBrowser(browserId, profileName, dest, {
        bookmarks: true,
        cookies: true,
        history: true,
        passwords: true,
        extensions: true,
        settings: true,
      });
      const path = (res as { export_path?: string; error?: string }).export_path;
      const err = (res as { error?: string }).error;
      setMessage(err ? String(err) : path ? `Готово: ${path}` : JSON.stringify(res));
    } catch (e) {
      setMessage(String(e));
    }
  };

  if (loading) {
    return (
      <section className="glass-panel" style={{ padding: 16 }}>
        Поиск браузеров…
      </section>
    );
  }

  return (
    <section className="glass-panel fade-in" style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <Globe size={24} weight="duotone" />
        <h2 style={{ margin: 0 }}>Браузеры</h2>
      </div>
      <label style={{ display: "block", marginBottom: 12, opacity: 0.85 }}>
        Папка назначения
        <input
          className="glass-input"
          style={{ width: "100%", marginTop: 6 }}
          value={dest}
          onChange={(e) => setDest(e.target.value)}
        />
      </label>
      {list.length === 0 && <p>Браузеры не найдены или нет доступа к профилям.</p>}
      {list.map((b) => (
        <div
          key={b.id}
          className="glass-panel"
          style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}
        >
          <strong>{b.name}</strong>
          <div style={{ fontSize: 13, opacity: 0.7 }}>{b.path}</div>
          <div style={{ fontSize: 13 }}>Размер: {formatBytes(b.total_size)}</div>
          <div style={{ marginTop: 8 }}>
            {b.profiles.map((p) => (
              <div
                key={p.name}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 8,
                  padding: "6px 0",
                  borderTop: "1px solid rgba(255,255,255,0.08)",
                }}
              >
                <span>Профиль: {p.name}</span>
                <button
                  type="button"
                  className="glass-button"
                  onClick={() => exportProfile(b.id, p.name)}
                >
                  Сохранить профиль
                </button>
              </div>
            ))}
          </div>
        </div>
      ))}
      {message && (
        <p style={{ marginTop: 12, fontSize: 14, opacity: 0.9 }}>{message}</p>
      )}
    </section>
  );
}
