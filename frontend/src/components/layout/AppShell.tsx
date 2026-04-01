import { useEffect, useState } from "react";
import { Play } from "@phosphor-icons/react";
import type { SystemInfo, ViewKey } from "../../types";
import { api } from "../../services/api";
import { useScanStore } from "../../stores/scanStore";
import { Sidebar } from "./Sidebar";
import { TitleBar } from "./TitleBar";
import { ScanDashboard } from "../scanner/ScanDashboard";
import { MyFilesPanel } from "../scanner/MyFilesPanel";
import { AIChatPanel } from "../ai/AIChatPanel";
import { BackupWizard } from "../backup/BackupWizard";
import { RestoreWizard } from "../backup/RestoreWizard";
import { BrowserManager } from "../browsers/BrowserManager";
import { AppManager } from "../apps/AppManager";
import { InstalledProgramsPage } from "../programs/InstalledProgramsPage";
import { SettingsPage } from "../settings/SettingsPage";
import { SystemInfoPanel } from "../settings/SystemInfoPanel";

function Dashboard({
  system,
  onStartScan,
}: {
  system: SystemInfo | null;
  onStartScan: () => void;
}) {
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <section
        className="glass-panel fade-in"
        style={{
          padding: 20,
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "radial-gradient(circle at 70% 20%, rgba(0,122,255,0.2), transparent 55%)",
            pointerEvents: "none",
          }}
        />
        <div style={{ position: "relative" }}>
          {system && (
            <span
              className="glass-panel"
              style={{ display: "inline-block", padding: "6px 12px", fontSize: 13, marginBottom: 12 }}
            >
              {system.full || `${system.os} ${system.edition} ${system.version}`}
            </span>
          )}
          <h1 style={{ margin: "0 0 8px" }}>Подготовь свой ПК к переустановке</h1>
          <p style={{ opacity: 0.88, maxWidth: 560 }}>
            Suggy Sweep найдёт пользовательские файлы, подскажет через AI, что сохранить, и поможет собрать бэкап на
            внешний носитель.
          </p>
          <button
            type="button"
            className="glass-button glass-button-primary"
            style={{ marginTop: 16, display: "inline-flex", alignItems: "center", gap: 8 }}
            onClick={onStartScan}
          >
            <Play size={20} weight="fill" />
            Начать сканирование
          </button>
        </div>
      </section>
      <section className="glass-panel fade-in" style={{ padding: 16 }}>
        <h3 style={{ marginTop: 0 }}>Быстрые действия</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 10 }}>
          {[
            "Полное сканирование",
            "Браузеры",
            "Приложения",
            "AI-анализ",
            "Бэкап",
            "Восстановление",
          ].map((t) => (
            <div key={t} className="glass-panel" style={{ padding: 12, borderRadius: 14, fontSize: 14 }}>
              {t}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export function AppShell() {
  const [view, setView] = useState<ViewKey>("dashboard");
  const [system, setSystem] = useState<SystemInfo | null>(null);
  const quickResult = useScanStore((s) => s.quickResult);

  useEffect(() => {
    api.getSystemInfo().then(setSystem).catch(() => setSystem(null));
  }, []);

  const sidebarStats = quickResult
    ? {
        files: quickResult.total_files,
        size: quickResult.total_size,
        drive: undefined,
      }
    : undefined;

  const content = () => {
    switch (view) {
      case "dashboard":
        return <Dashboard system={system} onStartScan={() => setView("scanner")} />;
      case "scanner":
        return <ScanDashboard />;
      case "myfiles":
        return <MyFilesPanel />;
      case "browsers":
        return <BrowserManager />;
      case "apps":
        return <AppManager />;
      case "programs":
        return <InstalledProgramsPage />;
      case "backup":
        return <BackupWizard />;
      case "restore":
        return <RestoreWizard />;
      case "ai":
        return <AIChatPanel />;
      case "system":
        return <SystemInfoPanel />;
      case "settings":
        return <SettingsPage />;
      default:
        return null;
    }
  };

  return (
    <div style={{ minHeight: "100vh", padding: 12, display: "grid", gridTemplateRows: "auto 1fr", gap: 12 }}>
      <TitleBar onOpenSettings={() => setView("settings")} />
      <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: 12, alignItems: "start" }}>
        <Sidebar current={view} onChange={setView} stats={sidebarStats} />
        <div style={{ minWidth: 0 }}>{content()}</div>
      </div>
    </div>
  );
}
