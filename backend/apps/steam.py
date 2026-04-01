import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size, steam_install_path


class SteamExporter:
    def detect(self) -> List[Dict[str, Any]]:
        root = steam_install_path()
        if not root:
            return []
        userdata = os.path.join(root, "userdata")
        config = os.path.join(root, "config")
        userdata_size = dir_size(userdata) if os.path.isdir(userdata) else 0
        return [
            {
                "id": "steam",
                "name": "Steam",
                "path": root,
                "userdata_size": userdata_size,
                "total_size": dir_size(root),
                "kind": "steam",
            }
        ]

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        if app_id != "steam":
            return {"error": "Неизвестный id Steam"}
        items = self.detect()
        if not items:
            return {"error": "Steam не найден"}
        root = items[0]["path"]
        export_dir = os.path.join(dest_path, "apps", "steam")
        os.makedirs(export_dir, exist_ok=True)

        for sub in ("userdata", "config"):
            src = os.path.join(root, sub)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(export_dir, sub), dirs_exist_ok=True)

        lib = os.path.join(root, "steamapps", "libraryfolders.vdf")
        if os.path.isfile(lib):
            sa = os.path.join(export_dir, "steamapps")
            os.makedirs(sa, exist_ok=True)
            shutil.copy2(lib, os.path.join(sa, "libraryfolders.vdf"))

        if full_backup:
            ss = os.path.join(root, "steamapps", "shadercache")
            if os.path.isdir(ss):
                pass

        return {
            "success": True,
            "export_path": export_dir,
            "size": dir_size(export_dir),
            "note": "Скопированы userdata, config и libraryfolders.vdf (без steamapps/common).",
        }
