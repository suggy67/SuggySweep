import { useState } from "react";
import { useScanStore } from "../../stores/scanStore";
import { useScanner } from "../../hooks/useScanner";
import { formatBytes, formatNumber } from "../../utils/formatters";
import { api } from "../../services/api";

export function ScanDashboard() {
  const { runQuickScan, startLiveScan, clearLive } = useScanner();
  const quickResult = useScanStore((s) => s.quickResult);
  const liveFiles = useScanStore((s) => s.liveFiles);
  const progress = useScanStore((s) => s.progress);
  const setQuickResult = useScanStore((s) => s.setQuickResult);
  const [busy, setBusy] = useState(false);
  const [explain, setExplain] = useState<string>("");
  const [explainingPath, setExplainingPath] = useState<string | null>(null);

  const onQuick = async () => {
    setBusy(true);
    clearLive();
    try {
      await runQuickScan();
    } finally {
      setBusy(false);
    }
  };

  const onLive = () => {
    clearLive();
    setQuickResult(null);
    startLiveScan();
  };

  const explainFile = async (path: string, name: string, category: string, size: number) => {
    setExplainingPath(path);
    setExplain("");
    const fileInfo = {
      path,
      name,
      extension: name.includes(".") ? `.${name.split(".").pop()}` : "",
      size,
      modified: "",
      category,
    };
    await api.analyzeFileStream(fileInfo, (c) => setExplain((e) => e + c));
    setExplainingPath(null);
  };

  const categories = quickResult ? Object.entries(quickResult.categories) : [];

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <section className="glass-panel fade-in" style={{ padding: 16 }}>
        <h2 style={{ marginTop: 0 }}>Сканирование</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          <button type="button" className="glass-button glass-button-primary" disabled={busy} onClick={onQuick}>
            Быстрое сканирование
          </button>
          <button type="button" className="glass-button" onClick={onLive}>
            Потоковое (WebSocket)
          </button>
        </div>
        {quickResult && (
          <p style={{ marginTop: 12, opacity: 0.85 }}>
            Всего: {formatNumber(quickResult.total_files)} файлов · {formatBytes(quickResult.total_size)}
          </p>
        )}
        {liveFiles.length > 0 && (
          <p style={{ marginTop: 8, opacity: 0.85 }}>
            Поток: {progress.count} файлов · {formatBytes(progress.totalSize)}
            <br />
            <small style={{ opacity: 0.7 }}>{progress.currentPath}</small>
          </p>
        )}
      </section>

      {categories.length > 0 && (
        <section className="glass-panel fade-in" style={{ padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Категории</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 10 }}>
            {categories.map(([name, data]) => (
              <div key={name} className="glass-panel" style={{ padding: 12, borderRadius: 14 }}>
                <strong>{name}</strong>
                <div style={{ fontSize: 13, opacity: 0.75 }}>
                  {formatNumber(data.count)} · {formatBytes(data.size)}
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 16 }}>
            <h4 style={{ marginBottom: 8 }}>Примеры файлов</h4>
            {categories.flatMap(([cat, data]) =>
              data.files.slice(0, 3).map((f) => (
                <div
                  key={f.path}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 8,
                    padding: "8px 0",
                    borderBottom: "1px solid rgba(255,255,255,0.08)",
                  }}
                >
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 500 }}>{f.name}</div>
                    <small style={{ opacity: 0.65, wordBreak: "break-all" }}>{f.path}</small>
                  </div>
                  <button
                    type="button"
                    className="glass-button"
                    disabled={explainingPath === f.path}
                    onClick={() => explainFile(f.path, f.name, cat, f.size)}
                  >
                    Что это?
                  </button>
                </div>
              ))
            )}
          </div>
          {explain && (
            <div className="glass-panel" style={{ marginTop: 12, padding: 12, borderRadius: 14, whiteSpace: "pre-wrap" }}>
              {explain}
            </div>
          )}
        </section>
      )}
    </div>
  );
}
