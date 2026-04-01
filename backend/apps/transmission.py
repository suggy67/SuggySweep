import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size, expand


class TransmissionExporter:
    _PATHS = (
        ("{LOCALAPPDATA}\\transmission", "Transmission"),
        ("{LOCALAPPDATA}\\Transmission", "Transmission"),
        ("{APPDATA}\\Transmission", "Transmission"),
    )

    def detect(self) -> List[Dict[str, Any]]:
        seen: set[str] = set()
        out: List[Dict[str, Any]] = []
        for tmpl, label in self._PATHS:
            path = os.path.normpath(expand(tmpl))
            key = os.path.normcase(path)
            if not os.path.isdir(path) or key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "id": f"transmission_{len(out)}",
                    "name": label,
                    "path": path,
                    "total_size": dir_size(path),
                    "kind": "transmission",
                }
            )
        if len(out) == 1:
            out[0]["id"] = "transmission"
        return out

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        for item in self.detect():
            if item["id"] != app_id:
                continue
            export_dir = os.path.join(dest_path, "apps", app_id)
            shutil.copytree(item["path"], export_dir, dirs_exist_ok=True)
            if not full_backup:
                pass
            return {
                "success": True,
                "export_path": export_dir,
                "size": dir_size(export_dir),
            }
        return {"error": "Transmission не найдена"}
