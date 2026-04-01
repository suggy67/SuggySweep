import { ChildProcess, spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

let backendProc: ChildProcess | null = null;

export function resolveBackendPaths(resourcesRoot: string): {
  script: string;
  cwd: string;
} {
  const script = path.join(resourcesRoot, "backend", "main.py");
  return { script, cwd: path.dirname(script) };
}

export function startBackend(resourcesRoot: string): void {
  if (backendProc) return;
  const { script, cwd } = resolveBackendPaths(resourcesRoot);
  if (!fs.existsSync(script)) {
    console.error("[Suggy Sweep] Не найден backend:", script);
    return;
  }
  const explicit = process.env.SUGGY_PYTHON?.trim();
  const win = process.platform === "win32";
  const cmd = explicit || (win ? "py" : "python3");
  const absScript = path.resolve(script);
  const args = !explicit && win ? ["-3", absScript] : [absScript];
  backendProc = spawn(cmd, args, {
    stdio: "inherit",
    shell: win,
    cwd,
    env: { ...process.env, PYTHONUTF8: "1" },
  });
}

export function stopBackend(): void {
  if (!backendProc) return;
  backendProc.kill();
  backendProc = null;
}
