import { useEffect, useMemo, useState } from "react";
import { Package } from "@phosphor-icons/react";
import { api, reinstallScriptUrl } from "../../services/api";
import type { InstalledProgram } from "../../types";
import { formatBytes } from "../../utils/formatters";

export function InstalledProgramsPage() {
  const [programs, setPrograms] = useState<InstalledProgram[]>([]);
  const [total, setTotal] = useState(0);
  const [truncated, setTruncated] = useState(false);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    api
      .getProgramsList(6000)
      .then((r) => {
        setPrograms(r.programs ?? []);
        setTotal(r.total ?? 0);
        setTruncated(!!r.truncated);
        setError("");
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return programs;
    return programs.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        (p.publisher && p.publisher.toLowerCase().includes(q))
    );
  }, [programs, filter]);

  return (
    <section className="glass-panel fade-in" style={{ padding: 16, display: "flex", flexDirection: "column", minHeight: 480 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <Package size={24} weight="duotone" />
        <h2 style={{ margin: 0 }}>Установленные программы</h2>
      </div>
      <p style={{ opacity: 0.8, marginTop: 0 }}>
        Список из реестра Windows (для плана переустановки). Всего записей: {total}
        {truncated ? " (показана только часть — увеличьте limit в API при необходимости)" : ""}.
      </p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
        <a
          className="glass-button glass-button-primary"
          href={reinstallScriptUrl("powershell", 8000)}
          style={{ textDecoration: "none", display: "inline-block" }}
        >
          Скачать PowerShell (.ps1)
        </a>
        <a
          className="glass-button"
          href={reinstallScriptUrl("txt", 8000)}
          style={{ textDecoration: "none", display: "inline-block" }}
        >
          Список .txt
        </a>
      </div>
      <input
        className="glass-input"
        style={{ marginBottom: 12 }}
        placeholder="Поиск по названию или издателю…"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      {loading && <p>Загрузка…</p>}
      {error && <p style={{ color: "rgba(255,120,120,0.95)" }}>{error}</p>}
      {!loading && !error && (
        <div
          className="glass-panel"
          style={{
            flex: 1,
            overflow: "auto",
            padding: 8,
            borderRadius: 14,
            maxHeight: "min(60vh, 560px)",
          }}
        >
          <div style={{ fontSize: 12, opacity: 0.55, marginBottom: 8 }}>
            Отображается: {filtered.length} из {programs.length}
          </div>
          {filtered.map((p) => (
            <div
              key={`${p.name}-${p.version ?? ""}`}
              style={{
                padding: "8px 6px",
                borderBottom: "1px solid rgba(255,255,255,0.06)",
                fontSize: 13,
              }}
            >
              <div style={{ fontWeight: 600 }}>{p.name}</div>
              <div style={{ opacity: 0.75 }}>
                {p.publisher || "—"}
                {p.version ? ` · ${p.version}` : ""}
                {p.estimated_size_bytes ? ` · ${formatBytes(p.estimated_size_bytes)}` : ""}
              </div>
              {p.install_location ? (
                <div style={{ fontSize: 11, opacity: 0.5, wordBreak: "break-all" }}>{p.install_location}</div>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
