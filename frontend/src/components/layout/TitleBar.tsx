import { Broom, GearSix } from "@phosphor-icons/react";

export function TitleBar({ onOpenSettings }: { onOpenSettings?: () => void }) {
  return (
    <header
      className="glass-panel"
      style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px" }}
    >
      <div style={{ display: "flex", gap: 8 }}>
        <span style={{ width: 12, height: 12, borderRadius: 999, background: "#ff5f57" }} />
        <span style={{ width: 12, height: 12, borderRadius: 999, background: "#ffbd2e" }} />
        <span style={{ width: 12, height: 12, borderRadius: 999, background: "#28c840" }} />
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <Broom size={20} weight="duotone" />
        <strong>Suggy Sweep</strong>
      </div>
      <button
        type="button"
        className="glass-button"
        style={{ padding: 8, display: "flex", alignItems: "center" }}
        onClick={onOpenSettings}
        aria-label="Настройки"
      >
        <GearSix size={20} weight="duotone" />
      </button>
    </header>
  );
}
