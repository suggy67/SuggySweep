import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size, expand


class VSCodeExporter:
    EDITORS = {
        "vscode": {
            "name": "Visual Studio Code",
            "user_dir": "{APPDATA}\\Code\\User",
        },
        "vscodium": {
            "name": "VSCodium",
            "user_dir": "{APPDATA}\\VSCodium\\User",
        },
    }

    def detect(self) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        for app_id, info in self.EDITORS.items():
            path = expand(info["user_dir"])
            if not os.path.isdir(path):
                continue
            ext_root = os.path.join(
                os.environ.get("USERPROFILE", ""),
                ".vscode",
                "extensions",
            )
            ext_size = dir_size(ext_root) if os.path.isdir(ext_root) and app_id == "vscode" else 0
            found.append(
                {
                    "id": app_id,
                    "name": info["name"],
                    "path": path,
                    "extensions_path": ext_root if app_id == "vscode" else None,
                    "user_size": dir_size(path),
                    "extensions_size": ext_size,
                    "total_size": dir_size(path) + ext_size,
                    "kind": "vscode",
                }
            )
        return found

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        for item in self.detect():
            if item["id"] != app_id:
                continue
            export_dir = os.path.join(dest_path, "apps", app_id)
            os.makedirs(export_dir, exist_ok=True)
            shutil.copytree(
                item["path"],
                os.path.join(export_dir, "User"),
                dirs_exist_ok=True,
            )
            if full_backup and item.get("extensions_path") and os.path.isdir(item["extensions_path"]):
                shutil.copytree(
                    item["extensions_path"],
                    os.path.join(export_dir, "extensions"),
                    dirs_exist_ok=True,
                )
            return {
                "success": True,
                "export_path": export_dir,
                "size": dir_size(export_dir),
            }
        return {"error": f"{app_id} не найден"}
