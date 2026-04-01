import { GearSix } from "@phosphor-icons/react";

export function SettingsPage() {
  return (
    <section className="glass-panel fade-in" style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <GearSix size={24} weight="duotone" />
        <h2 style={{ margin: 0 }}>Настройки</h2>
      </div>
      <ul style={{ lineHeight: 1.7, opacity: 0.9 }}>
        <li>Тёмная тема по умолчанию (liquid glass)</li>
        <li>
          AI: переменная окружения <code>LOVABLE_API_KEY</code> для процесса Python (backend)
        </li>
        <li>
          Frontend / Electron: при нестандартном хосте API скопируйте{" "}
          <code>frontend/.env.example</code> в <code>frontend/.env</code> и задайте{" "}
          <code>VITE_API_BASE</code> (например <code>http://127.0.0.1:8765/api</code>)
        </li>
        <li>
          Electron: <code>SUGGY_PYTHON</code> — путь к Python; <code>SUGGY_DEV_SERVER_URL</code> — URL Vite при
          разработке; <code>SUGGY_BACKEND_URL</code> — URL проверки готовности API
        </li>
        <li>Язык интерфейса: русский</li>
      </ul>
    </section>
  );
}
