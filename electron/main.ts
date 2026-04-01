import { app, BrowserWindow } from "electron";
import http from "node:http";
import path from "node:path";
import { startBackend, stopBackend } from "./python-bridge";

const BACKEND_HEALTH_URL =
  process.env.SUGGY_BACKEND_URL?.trim() ||
  "http://127.0.0.1:8765/api/system/info";
const DEV_SERVER_URL =
  process.env.SUGGY_DEV_SERVER_URL?.trim() || "http://127.0.0.1:5173";

function getResourcesRoot(): string {
  if (app.isPackaged) {
    return process.resourcesPath;
  }
  return path.resolve(__dirname, "..", "..");
}

function waitForBackend(url: string, timeoutMs: number): Promise<void> {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;

    const retry = () => {
      if (Date.now() > deadline) {
        reject(new Error("Backend не ответил (проверьте Python и порт 8765)"));
        return;
      }
      setTimeout(attempt, 450);
    };

    const attempt = () => {
      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode && res.statusCode >= 200 && res.statusCode < 500) {
          resolve();
        } else {
          retry();
        }
      });
      req.on("error", () => retry());
      req.setTimeout(2800, () => {
        req.destroy();
        retry();
      });
    };

    attempt();
  });
}

function createWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    title: "Suggy Sweep",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
    },
  });

  return win;
}

app.whenReady().then(async () => {
  const root = getResourcesRoot();
  startBackend(root);
  try {
    await waitForBackend(BACKEND_HEALTH_URL, 50_000);
  } catch (e) {
    console.error(e);
  }

  const win = createWindow();

  if (app.isPackaged) {
    const indexHtml = path.join(process.resourcesPath, "app", "index.html");
    await win.loadFile(indexHtml);
  } else {
    await win.loadURL(DEV_SERVER_URL);
  }
});

app.on("window-all-closed", () => {
  stopBackend();
  app.quit();
});
