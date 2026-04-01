import { useEffect, useState } from "react";
import { AppWindow } from "@phosphor-icons/react";
import { api } from "../../services/api";
import { formatBytes } from "../../utils/formatters";

interface BaseApp {
  id: string;
  name: string;
  path: string;
  total_size: number;
  kind?: string;
}

interface TelegramClient extends BaseApp {
  has_tdata?: boolean;
  tdata_size?: number;
  is_portable?: boolean;
}

interface DiscordApp extends BaseApp {
  has_betterdiscord?: boolean;
}

interface VSCodeApp extends BaseApp {
  user_size?: number;
  extensions_size?: number;
}

interface SteamApp extends BaseApp {
  userdata_size?: number;
}

interface FilezillaRow extends BaseApp {
  has_sitemanager?: boolean;
}

interface GitSSHApp extends BaseApp {
  has_gitconfig?: boolean;
  has_ssh?: boolean;
  has_npmrc?: boolean;
  has_yarnrc?: boolean;
}

interface WinScpRow extends BaseApp {
  paths_found?: string[];
}

interface DetectResponse {
  telegram_clients?: TelegramClient[];
  discord?: DiscordApp[];
  vscode?: VSCodeApp[];
  steam?: SteamApp[];
  git_ssh?: GitSSHApp[];
  obs?: BaseApp[];
  qbittorrent?: BaseApp[];
  filezilla?: FilezillaRow[];
  transmission?: BaseApp[];
  putty?: BaseApp[];
  winscp?: WinScpRow[];
}

export function AppManager() {
  const [data, setData] = useState<DetectResponse | null>(null);
  const [dest, setDest] = useState("D:\\SuggyExport");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api
      .detectApps()
      .then((r: DetectResponse) => setData(r))
      .catch(() => setData(null));
  }, []);

  const save = async (id: string, full: boolean) => {
    setMsg("Экспорт…");
    try {
      const res = (await api.exportApp(id, dest, full)) as {
        error?: string;
        export_path?: string;
        note?: string;
      };
      setMsg(
        res.error
          ? String(res.error)
          : `Сохранено: ${res.export_path ?? ""}${res.note ? ` — ${res.note}` : ""}`
      );
    } catch (e) {
      setMsg(String(e));
    }
  };

  const tg = data?.telegram_clients ?? [];
  const dc = data?.discord ?? [];
  const vs = data?.vscode ?? [];
  const st = data?.steam ?? [];
  const gs = data?.git_ssh ?? [];
  const obs = data?.obs ?? [];
  const qbit = data?.qbittorrent ?? [];
  const fz = data?.filezilla ?? [];
  const tr = data?.transmission ?? [];
  const pt = data?.putty ?? [];
  const ws = data?.winscp ?? [];
  const totalCount =
    tg.length +
    dc.length +
    vs.length +
    st.length +
    gs.length +
    obs.length +
    qbit.length +
    fz.length +
    tr.length +
    pt.length +
    ws.length;

  return (
    <section className="glass-panel fade-in" style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <AppWindow size={24} weight="duotone" />
        <h2 style={{ margin: 0 }}>Приложения</h2>
      </div>
      <p style={{ opacity: 0.8 }}>
        Мессенджеры, Discord, VS Code / VSCodium, Steam, Git/SSH/npm, OBS, qBittorrent, FileZilla, Transmission,
        PuTTY, WinSCP.
      </p>
      <label style={{ display: "block", marginBottom: 16 }}>
        Папка назначения
        <input
          className="glass-input"
          style={{ width: "100%", marginTop: 6 }}
          value={dest}
          onChange={(e) => setDest(e.target.value)}
        />
      </label>

      {tg.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, marginBottom: 8 }}>Мессенджеры</h3>
          {tg.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              {c.is_portable && (
                <span style={{ marginLeft: 8, fontSize: 12, opacity: 0.7 }}>portable</span>
              )}
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>
                Размер: {formatBytes(c.total_size)} · tdata:{" "}
                {c.has_tdata ? formatBytes(c.tdata_size ?? 0) : "—"}
              </div>
              <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                <button type="button" className="glass-button" onClick={() => save(c.id, true)}>
                  Полный бэкап
                </button>
                <button type="button" className="glass-button" onClick={() => save(c.id, false)}>
                  Только tdata
                </button>
              </div>
            </div>
          ))}
        </>
      )}

      {dc.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>Discord</h3>
          {dc.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>{formatBytes(c.total_size)}</div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Сохранить данные
              </button>
            </div>
          ))}
        </>
      )}

      {vs.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>Редакторы</h3>
          {vs.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>
                User: {formatBytes(c.user_size ?? c.total_size)}
                {c.extensions_size ? ` · Расширения: ${formatBytes(c.extensions_size)}` : ""}
              </div>
              <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                <button type="button" className="glass-button" onClick={() => save(c.id, false)}>
                  Только настройки (User)
                </button>
                <button type="button" className="glass-button" onClick={() => save(c.id, true)}>
                  + расширения (.vscode/extensions)
                </button>
              </div>
            </div>
          ))}
        </>
      )}

      {st.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>Steam</h3>
          {st.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>
                userdata: {formatBytes(c.userdata_size ?? 0)} · всего папка Steam: {formatBytes(c.total_size)}
              </div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Сохранить userdata + config
              </button>
            </div>
          ))}
        </>
      )}

      {gs.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>Разработка</h3>
          {gs.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>
                {formatBytes(c.total_size)} · .gitconfig: {c.has_gitconfig ? "да" : "нет"} · .ssh:{" "}
                {c.has_ssh ? "да" : "нет"} · .npmrc: {c.has_npmrc ? "да" : "нет"}
              </div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Экспортировать
              </button>
            </div>
          ))}
        </>
      )}

      {obs.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>Стриминг</h3>
          {obs.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>{formatBytes(c.total_size)}</div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Сохранить профиль OBS
              </button>
            </div>
          ))}
        </>
      )}

      {qbit.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>Торренты</h3>
          {qbit.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>{formatBytes(c.total_size)}</div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Сохранить настройки qBittorrent
              </button>
            </div>
          ))}
        </>
      )}

      {fz.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>FTP</h3>
          {fz.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>
                {formatBytes(c.total_size)}
                {c.has_sitemanager ? " · sitemanager.xml найден" : ""}
              </div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Сохранить настройки FileZilla
              </button>
            </div>
          ))}
        </>
      )}

      {tr.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>Transmission</h3>
          {tr.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <div style={{ fontSize: 13 }}>{formatBytes(c.total_size)}</div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Сохранить данные Transmission
              </button>
            </div>
          ))}
        </>
      )}

      {pt.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>PuTTY</h3>
          {pt.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>{c.path}</div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Экспорт .reg (настройки и сессии)
              </button>
            </div>
          ))}
        </>
      )}

      {ws.length > 0 && (
        <>
          <h3 style={{ fontSize: 15, opacity: 0.75, margin: "16px 0 8px" }}>WinSCP</h3>
          {ws.map((c) => (
            <div key={c.id} className="glass-panel" style={{ padding: 12, marginBottom: 12, borderRadius: 14 }}>
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, opacity: 0.7 }}>
                {c.paths_found?.length
                  ? c.paths_found.join(" · ")
                  : c.path}
              </div>
              <div style={{ fontSize: 13 }}>{formatBytes(c.total_size)}</div>
              <button type="button" className="glass-button" style={{ marginTop: 10 }} onClick={() => save(c.id, true)}>
                Сохранить настройки WinSCP
              </button>
            </div>
          ))}
        </>
      )}

      {totalCount === 0 && <p>Поддерживаемые приложения не найдены.</p>}
      {msg && <p style={{ marginTop: 12 }}>{msg}</p>}
    </section>
  );
}
