import os
import subprocess
import sys
from typing import Any, Dict, List

from apps._util import dir_size


def _no_window() -> int:
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0)) if sys.platform == "win32" else 0


class PuttyExporter:
    REG_PATH = r"HKCU\Software\SimonTatham\PuTTY"

    def detect(self) -> List[Dict[str, Any]]:
        r = subprocess.run(
            ["reg", "query", self.REG_PATH],
            capture_output=True,
            text=True,
            creationflags=_no_window(),
        )
        if r.returncode != 0:
            return []
        return [
            {
                "id": "putty",
                "name": "PuTTY (сессии в реестре)",
                "path": self.REG_PATH,
                "total_size": 0,
                "kind": "putty",
            }
        ]

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        if app_id != "putty":
            return {"error": "Неизвестный id"}
        if not self.detect():
            return {"error": "PuTTY в реестре не найден"}
        export_dir = os.path.join(dest_path, "apps", "putty")
        os.makedirs(export_dir, exist_ok=True)
        out_reg = os.path.join(export_dir, "putty_settings.reg")
        r = subprocess.run(
            ["reg", "export", self.REG_PATH, out_reg, "/y"],
            capture_output=True,
            text=True,
            creationflags=_no_window(),
        )
        if r.returncode != 0:
            return {"error": r.stderr or "reg export не удался"}
        if not full_backup:
            pass
        size = os.path.getsize(out_reg) if os.path.isfile(out_reg) else 0
        return {"success": True, "export_path": export_dir, "size": size}
