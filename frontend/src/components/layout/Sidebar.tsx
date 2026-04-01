import {
  AppWindow,
  ArrowCounterClockwise,
  Desktop,
  FloppyDisk,
  FolderOpen,
  GearSix,
  Globe,
  House,
  MagnifyingGlass,
  Package,
  Robot,
} from "@phosphor-icons/react";
import type { ViewKey } from "../../types";
import { formatBytes } from "../../utils/formatters";

const items: { key: ViewKey; title: string; icon: JSX.Element }[] = [
  { key: "dashboard", title: "Dashboard", icon: <House size={20} weight="duotone" /> },
  { key: "scanner", title: "Scanner", icon: <MagnifyingGlass size={20} weight="duotone" /> },
  { key: "myfiles", title: "Мои файлы", icon: <FolderOpen size={20} weight="duotone" /> },
  { key: "browsers", title: "Браузеры", icon: <Globe size={20} weight="duotone" /> },
  { key: "apps", title: "Приложения", icon: <AppWindow size={20} weight="duotone" /> },
  { key: "programs", title: "Все программы", icon: <Package size={20} weight="duotone" /> },
  { key: "backup", title: "Бэкап", icon: <FloppyDisk size={20} weight="duotone" /> },
  { key: "restore", title: "Восстановление", icon: <ArrowCounterClockwise size={20} weight="duotone" /> },
  { key: "ai", title: "AI Assistant", icon: <Robot size={20} weight="duotone" /> },
  { key: "system", title: "Система", icon: <Desktop size={20} weight="duotone" /> },
  { key: "settings", title: "Настройки", icon: <GearSix size={20} weight="duotone" /> },
];

export function Sidebar({
  current,
  onChange,
  stats,
}: {
  current: ViewKey;
  onChange: (k: ViewKey) => void;
  stats?: { files: number; size: number; drive?: string };
}) {
  return (
    <aside className="glass-panel" style={{ width: 260, padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
      {items.map((item) => (
        <button
          key={item.key}
          type="button"
          onClick={() => onChange(item.key)}
          className="glass-button"
          style={{
            textAlign: "left",
            background: current === item.key ? "rgba(0,122,255,0.35)" : undefined,
            display: "flex",
            gap: 10,
            alignItems: "center",
          }}
        >
          {item.icon}
          {item.title}
        </button>
      ))}
      <div style={{ marginTop: "auto", paddingTop: 12, borderTop: "1px solid rgba(255,255,255,0.1)" }}>
        <div style={{ fontSize: 12, opacity: 0.55, marginBottom: 6 }}>Быстрая статистика</div>
        <div className="glass-panel" style={{ padding: 8, borderRadius: 12, fontSize: 13 }}>
          <div>Файлов: {stats?.files ?? "—"}</div>
          <div>Размер: {stats?.size != null ? formatBytes(stats.size) : "—"}</div>
          <div>Диск: {stats?.drive ?? "—"}</div>
        </div>
      </div>
    </aside>
  );
}
