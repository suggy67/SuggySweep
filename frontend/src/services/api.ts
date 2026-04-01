import type {
  DriveInfo,
  FileInfo,
  InstalledProgram,
  QuickScanResult,
  SystemInfo,
} from "../types";

const rawBase =
  (import.meta.env.VITE_API_BASE as string | undefined)?.trim() ||
  "http://127.0.0.1:8765/api";
export const API_BASE = rawBase.replace(/\/$/, "");

function scanWebSocketUrl(): string {
  try {
    const httpRoot = API_BASE.replace(/\/api\/?$/i, "");
    const u = new URL(httpRoot || "http://127.0.0.1:8765");
    const wsProto = u.protocol === "https:" ? "wss:" : "ws:";
    return `${wsProto}//${u.host}/api/scan/ws/scan`;
  } catch {
    return "ws://127.0.0.1:8765/api/scan/ws/scan";
  }
}

export function reinstallScriptUrl(
  format: "powershell" | "txt" = "powershell",
  limit = 8000
): string {
  const q = new URLSearchParams({ format, limit: String(limit) });
  return `${API_BASE}/programs/reinstall-script?${q}`;
}

async function readEventStream(
  response: Response,
  onChunk: (text: string) => void
): Promise<void> {
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buffer.indexOf("\n")) !== -1) {
      const line = buffer.slice(0, idx).trimEnd();
      buffer = buffer.slice(idx + 1);
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6).trim();
      if (data === "[DONE]") return;
      try {
        const parsed = JSON.parse(data) as { content?: string };
        if (parsed.content) onChunk(parsed.content);
      } catch {
        /* ignore */
      }
    }
  }
}

export const api = {
  getSystemInfo: (): Promise<SystemInfo> =>
    fetch(`${API_BASE}/system/info`).then((r) => r.json()),

  getDrives: (): Promise<DriveInfo[]> =>
    fetch(`${API_BASE}/drives/list`).then((r) => r.json()),

  checkSpace: (drive: string, required_bytes: number) =>
    fetch(`${API_BASE}/drives/check-space`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ drive, required_bytes }),
    }).then((r) => r.json()),

  quickScan: (body?: {
    include_appdata?: boolean;
    max_files_per_category?: number;
  }): Promise<QuickScanResult> =>
    fetch(`${API_BASE}/scan/quick-scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body ?? { include_appdata: true }),
    }).then((r) => r.json()),

  detectBrowsers: () =>
    fetch(`${API_BASE}/browsers/detect`).then((r) => r.json()),

  exportBrowser: (
    browser_id: string,
    profile: string,
    dest_path: string,
    options: Record<string, boolean>
  ) =>
    fetch(`${API_BASE}/browsers/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        browser_id,
        profile,
        dest_path,
        options,
      }),
    }).then((r) => r.json()),

  detectApps: () => fetch(`${API_BASE}/apps/detect`).then((r) => r.json()),

  getProgramsList: (limit = 4000): Promise<{
    programs: InstalledProgram[];
    total: number;
    truncated: boolean;
  }> =>
    fetch(`${API_BASE}/programs/list?limit=${limit}`).then((r) => r.json()),

  exportApp: (app_id: string, dest_path: string, full_backup: boolean) =>
    fetch(`${API_BASE}/apps/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ app_id, dest_path, full_backup }),
    }).then((r) => r.json()),

  createBackup: (payload: {
    files: FileInfo[];
    dest_drive: string;
    backup_name?: string;
    compression?: "folder" | "zip";
  }) =>
    fetch(`${API_BASE}/backup/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => r.json()),

  previewBackup: (backup_path: string, preview_limit?: number) =>
    fetch(`${API_BASE}/backup/preview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ backup_path, preview_limit: preview_limit ?? 500 }),
    }).then((r) => r.json()),

  restoreBackup: (payload: {
    backup_path: string;
    restore_items?: string[];
    dest_base?: string;
  }) =>
    fetch(`${API_BASE}/backup/restore`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => r.json()),

  startScan: (
    onFile: (file: FileInfo) => void,
    onProgress: (p: {
      count: number;
      total_size: number;
      current_file: string;
    }) => void,
    onComplete: (r: { total_files: number; total_size: number }) => void,
    config?: { include_appdata?: boolean }
  ) => {
    const ws = new WebSocket(scanWebSocketUrl());
    ws.onopen = () =>
      ws.send(JSON.stringify({ include_appdata: config?.include_appdata ?? true }));
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data as string) as {
        type: string;
        data?: FileInfo;
        count?: number;
        total_size?: number;
        current_file?: string;
        total_files?: number;
      };
      if (data.type === "file" && data.data) onFile(data.data);
      if (data.type === "progress")
        onProgress({
          count: data.count ?? 0,
          total_size: data.total_size ?? 0,
          current_file: data.current_file ?? "",
        });
      if (data.type === "complete")
        onComplete({
          total_files: data.total_files ?? 0,
          total_size: data.total_size ?? 0,
        });
    };
    return ws;
  },

  analyzeFileStream: async (
    fileInfo: FileInfo,
    onChunk: (text: string) => void
  ) => {
    const response = await fetch(`${API_BASE}/ai/analyze-file`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_info: fileInfo }),
    });
    await readEventStream(response, onChunk);
  },

  chatStream: async (
    messages: { role: string; content: string }[],
    onChunk: (text: string) => void
  ) => {
    const response = await fetch(`${API_BASE}/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
    await readEventStream(response, onChunk);
  },

  recommendationsStream: async (
    scanResults: unknown,
    onChunk: (text: string) => void
  ) => {
    const response = await fetch(`${API_BASE}/ai/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scanResults),
    });
    await readEventStream(response, onChunk);
  },
};
