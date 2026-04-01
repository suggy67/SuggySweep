import { useEffect, useState } from "react";
import { Desktop } from "@phosphor-icons/react";
import { api } from "../../services/api";
import type { SystemInfo } from "../../types";

export function SystemInfoPanel() {
  const [info, setInfo] = useState<SystemInfo | null>(null);

  useEffect(() => {
    api.getSystemInfo().then(setInfo).catch(() => setInfo(null));
  }, []);

  return (
    <section className="glass-panel fade-in" style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <Desktop size={24} weight="duotone" />
        <h2 style={{ margin: 0 }}>Система</h2>
      </div>
      {!info && <p>Загрузка…</p>}
      {info && (
        <dl style={{ display: "grid", gap: 8 }}>
          <div>
            <dt style={{ opacity: 0.6, fontSize: 13 }}>ОС</dt>
            <dd style={{ margin: 0 }}>{info.full || `${info.os} ${info.edition}`}</dd>
          </div>
          <div>
            <dt style={{ opacity: 0.6, fontSize: 13 }}>Сборка</dt>
            <dd style={{ margin: 0 }}>{info.build}</dd>
          </div>
          <div>
            <dt style={{ opacity: 0.6, fontSize: 13 }}>Архитектура</dt>
            <dd style={{ margin: 0 }}>{info.architecture}</dd>
          </div>
          <div>
            <dt style={{ opacity: 0.6, fontSize: 13 }}>ПК / пользователь</dt>
            <dd style={{ margin: 0 }}>
              {info.hostname} · {info.username}
            </dd>
          </div>
        </dl>
      )}
    </section>
  );
}
