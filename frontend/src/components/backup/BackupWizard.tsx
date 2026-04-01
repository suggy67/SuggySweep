import { useEffect, useMemo, useState } from "react";
import { api } from "../../services/api";
import { useScanStore } from "../../stores/scanStore";
import type { DriveInfo, FileInfo } from "../../types";
import { formatBytes } from "../../utils/formatters";

function flattenFilesFromQuick(): FileInfo[] {
  const quick = useScanStore.getState().quickResult;
  if (!quick) return [];
  const out: FileInfo[] = [];
  for (const bucket of Object.values(quick.categories)) {
    out.push(...bucket.files);
  }
  return out;
}

export function BackupWizard() {
  const [drives, setDrives] = useState<DriveInfo[]>([]);
  const [selectedLetter, setSelectedLetter] = useState<string>("");
  const [compression, setCompression] = useState<"folder" | "zip">("folder");
  const [status, setStatus] = useState("");
  const quickResult = useScanStore((s) => s.quickResult);

  const filesToBackup = useMemo(() => flattenFilesFromQuick(), [quickResult]);

  useEffect(() => {
    const load = () =>
      api.getDrives().then((d) => {
        setDrives(d);
        const first = d.find((x) => x.is_suitable_for_backup);
        if (first && !selectedLetter) setSelectedLetter(first.letter);
      });
    load();
    const id = window.setInterval(load, 5000);
    return () => window.clearInterval(id);
  }, [selectedLetter]);

  const run = async () => {
    if (!selectedLetter) {
      setStatus("Выберите диск");
      return;
    }
    if (filesToBackup.length === 0) {
      setStatus("Нет файлов из быстрого скана. Сначала откройте Scanner → Быстрое сканирование.");
      return;
    }
    setStatus("Создание бэкапа…");
    try {
      const res = await api.createBackup({
        files: filesToBackup,
        dest_drive: `${selectedLetter}:`,
        compression,
      });
      setStatus(res.error ? JSON.stringify(res) : `Готово: ${res.path}`);
    } catch (e) {
      setStatus(String(e));
    }
  };

  return (
    <section className="glass-panel fade-in" style={{ padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Мастер бэкапа</h2>
      <p style={{ opacity: 0.85 }}>
        Шаг 1: диск назначения (список обновляется каждые 5 с). Шаг 2: данные берутся из последнего быстрого скана.
      </p>
      <div style={{ display: "grid", gap: 10, marginBottom: 16 }}>
        {drives.map((d) => (
          <button
            key={d.letter}
            type="button"
            className="glass-button"
            style={{
              textAlign: "left",
              borderColor: selectedLetter === d.letter ? "rgba(0,122,255,0.6)" : undefined,
            }}
            onClick={() => setSelectedLetter(d.letter)}
          >
            <strong>
              {d.letter}: — {d.label}
            </strong>
            <div style={{ fontSize: 13, opacity: 0.75 }}>
              {d.type} · свободно {formatBytes(d.free_bytes)}
              {d.is_system ? " · системный" : ""}
            </div>
          </button>
        ))}
      </div>
      <label style={{ display: "block", marginBottom: 12 }}>
        Формат
        <select
          className="glass-input"
          style={{ width: "100%", marginTop: 6 }}
          value={compression}
          onChange={(e) => setCompression(e.target.value as "folder" | "zip")}
        >
          <option value="folder">Папка + манифест</option>
          <option value="zip">ZIP архив</option>
        </select>
      </label>
      <p style={{ fontSize: 14, opacity: 0.85 }}>
        Файлов к копированию: {filesToBackup.length} (из быстрого скана, до 100 на категорию)
      </p>
      <button type="button" className="glass-button glass-button-primary" onClick={run}>
        Создать бэкап
      </button>
      {status && <p style={{ marginTop: 12 }}>{status}</p>}
    </section>
  );
}
