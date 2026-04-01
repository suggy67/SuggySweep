import { useScanStore } from "../../stores/scanStore";
import { formatBytes, formatNumber } from "../../utils/formatters";

export function MyFilesPanel() {
  const quick = useScanStore((s) => s.quickResult);

  if (!quick) {
    return (
      <section className="glass-panel fade-in" style={{ padding: 16 }}>
        <h2 style={{ marginTop: 0 }}>Мои файлы</h2>
        <p style={{ opacity: 0.85 }}>Сначала выполните быстрое сканирование на экране «Scanner».</p>
      </section>
    );
  }

  return (
    <section className="glass-panel fade-in" style={{ padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Мои файлы</h2>
      <p style={{ opacity: 0.85 }}>
        Всего: {formatNumber(quick.total_files)} · {formatBytes(quick.total_size)}
      </p>
      <ul style={{ paddingLeft: 18, lineHeight: 1.8 }}>
        {Object.entries(quick.categories).map(([name, c]) => (
          <li key={name}>
            <strong>{name}</strong> — {formatNumber(c.count)} файлов, {formatBytes(c.size)}
          </li>
        ))}
      </ul>
    </section>
  );
}
