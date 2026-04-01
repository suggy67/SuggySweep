import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size, expand


class QBittorrentExporter:
    def detect(self) -> List[Dict[str, Any]]:
        path = expand("{APPDATA}\\qBittorrent")
        if not os.path.isdir(path):
            return []
        return [
            {
                "id": "qbittorrent",
                "name": "qBittorrent",
                "path": path,
                "total_size": dir_size(path),
                "kind": "qbittorrent",
            }
        ]

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        if app_id != "qbittorrent":
            return {"error": "Неизвестный id"}
        items = self.detect()
        if not items:
            return {"error": "qBittorrent не найден"}
        export_dir = os.path.join(dest_path, "apps", "qbittorrent")
        shutil.copytree(items[0]["path"], export_dir, dirs_exist_ok=True)
        if not full_backup:
            pass
        return {
            "success": True,
            "export_path": export_dir,
            "size": dir_size(export_dir),
        }
