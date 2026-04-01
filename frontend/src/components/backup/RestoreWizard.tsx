import { useCallback, useMemo, useState } from "react";
import { ArrowCounterClockwise } from "@phosphor-icons/react";
import { api } from "../../services/api";
import { formatBytes } from "../../utils/formatters";

interface ManifestFileEntry {
  original_path: string;
  backup_path?: string;
  size?: number;
  category?: string;
}

interface PreviewOk {
  version?: string;
  created?: string;
  backup_name?: string;
  source_system?: Record<string, string>;
  total_files?: number;
  total_size_manifest?: number;
  files_preview?: ManifestFileEntry[];
  truncated?: boolean;
  error?: string;
}

export function RestoreWizard() {
  const [path, setPath] = useState("");
  const [preview, setPreview] = useState<PreviewOk | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [mode, setMode] = useState<"all" | "picked">("all");
  const [destBase, setDestBase] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<string>("");

  const files = preview?.files_preview ?? [];

  const loadPreview = async () => {
    setBusy(true);
    setResult("");
    setPreview(null);
    setSelected(new Set());
    try {
      const data = (await api.previewBackup(path.trim(), 800)) as PreviewOk;
      setPreview(data);
      if (data.error) {
        setResult(data.error);
      } else if (data.files_preview?.length) {
        setSelected(new Set(data.files_preview.map((f) => f.original_path)));
      }
    } catch (e) {
      setResult(String(e));
    } finally {
      setBusy(false);
    }
  };

  const togglePath = useCallback((p: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(p)) next.delete(p);
      else next.add(p);
      return next;
    });
  }, []);

  const selectAllInPreview = () => {
    setSelected(new Set(files.map((f) => f.original_path)));
  };

  const clearSelection = () => setSelected(new Set());

  const runRestore = async () => {
    setBusy(true);
    setResult("Восстановление…");
    try {
      const payload: {
        backup_path: string;
        restore_items?: string[];
        dest_base?: string;
      } = { backup_path: path.trim() };
      if (mode === "picked") {
        payload.restore_items = Array.from(selected);
      }
      const db = destBase.trim();
      if (db) payload.dest_base = db;
      const res = await api.restoreBackup(payload);
      setResult(JSON.stringify(res, null, 2));
    } catch (e) {
      setResult(String(e));
    } finally {
      setBusy(false);
    }
  };

  const summaryLine = useMemo(() => {
    if (!preview || preview.error) return null;
    const sys = preview.source_system;
    const node = sys?.node ?? "";
    return `${preview.backup_name ?? "бэкап"} · файлов: ${preview.total_files ?? 0}${
      node ? ` · с ПК: ${node}` : ""
    }`;
  }, [preview]);

  return (
    <section className="glass-panel fade-in" style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <ArrowCounterClockwise size={24} weight="duotone" />
        <h2 style={{ margin: 0 }}>Восстановление</h2>
      </div>
      <p style={{ opacity: 0.85 }}>
        Укажите путь к папке бэкапа (рядом с <code>suggy_manifest.json</code>) или к <code>.zip</code> архиву.
      </p>
      <input
        className="glass-input"
        style={{ width: "100%", marginBottom: 8 }}
        placeholder="D:\SuggySweep_Backups\имя_бэкапа"
        value={path}
        onChange={(e) => setPath(e.target.value)}
      />
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
        <button type="button" className="glass-button" disabled={busy || !path.trim()} onClick={loadPreview}>
          Загрузить манифест
        </button>
      </div>

      <label style={{ display: "block", marginBottom: 12, fontSize: 14 }}>
        Другая корневая папка (необязательно)
        <input
          className="glass-input"
          style={{ width: "100%", marginTop: 6 }}
          placeholder="Пусто = оригинальные пути из манифеста"
          value={destBase}
          onChange={(e) => setDestBase(e.target.value)}
        />
      </label>

      {summaryLine && (
        <p style={{ fontSize: 14, opacity: 0.9, marginBottom: 8 }}>{summaryLine}</p>
      )}
      {preview?.created && (
        <p style={{ fontSize: 13, opacity: 0.65, marginTop: 0 }}>Создан: {preview.created}</p>
      )}

      {files.length > 0 && (
        <>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", marginBottom: 10 }}>
            <span style={{ fontSize: 14 }}>Объём:</span>
            <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 14 }}>
              <input
                type="radio"
                name="restore-mode"
                checked={mode === "all"}
                onChange={() => setMode("all")}
              />
              Все файлы манифеста
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 14 }}>
              <input
                type="radio"
                name="restore-mode"
                checked={mode === "picked"}
                onChange={() => setMode("picked")}
              />
              Только отмеченные (из предпросмотра)
            </label>
          </div>
          {preview?.truncated && (
            <p style={{ fontSize: 13, color: "rgba(255,200,120,0.95)", marginBottom: 8 }}>
              Показана только часть списка. Режим «Все файлы манифеста» восстановит полный набор из архива/папки.
            </p>
          )}
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <button type="button" className="glass-button" onClick={selectAllInPreview}>
              Отметить все в списке
            </button>
            <button type="button" className="glass-button" onClick={clearSelection}>
              Снять все
            </button>
          </div>
          <div
            className="glass-panel"
            style={{
              maxHeight: 280,
              overflow: "auto",
              padding: 8,
              borderRadius: 12,
              marginBottom: 12,
            }}
          >
            {files.map((f) => (
              <label
                key={f.original_path}
                style={{
                  display: "flex",
                  gap: 8,
                  alignItems: "flex-start",
                  padding: "6px 4px",
                  borderBottom: "1px solid rgba(255,255,255,0.06)",
                  fontSize: 12,
                  cursor: "pointer",
                }}
              >
                <input
                  type="checkbox"
                  checked={selected.has(f.original_path)}
                  onChange={() => togglePath(f.original_path)}
                />
                <span style={{ wordBreak: "break-all", flex: 1 }}>
                  {f.original_path}
                  {f.size != null ? (
                    <span style={{ opacity: 0.6, marginLeft: 6 }}>({formatBytes(f.size)})</span>
                  ) : null}
                </span>
              </label>
            ))}
          </div>
        </>
      )}

      <button
        type="button"
        className="glass-button glass-button-primary"
        disabled={busy || !path.trim()}
        onClick={runRestore}
      >
        Восстановить
      </button>
      {result && (
        <pre
          style={{
            marginTop: 16,
            padding: 12,
            background: "rgba(0,0,0,0.25)",
            borderRadius: 12,
            overflow: "auto",
            fontSize: 12,
            maxHeight: 360,
          }}
        >
          {result}
        </pre>
      )}
    </section>
  );
}
