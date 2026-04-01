import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size, expand


class OBSExporter:
    def detect(self) -> List[Dict[str, Any]]:
        path = expand("{APPDATA}\\obs-studio")
        if not os.path.isdir(path):
            return []
        return [
            {
                "id": "obs_studio",
                "name": "OBS Studio",
                "path": path,
                "total_size": dir_size(path),
                "kind": "obs",
            }
        ]

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        if app_id != "obs_studio":
            return {"error": "Неизвестный id"}
        items = self.detect()
        if not items:
            return {"error": "OBS не найден"}
        export_dir = os.path.join(dest_path, "apps", "obs_studio")
        shutil.copytree(items[0]["path"], export_dir, dirs_exist_ok=True)
        if not full_backup:
            pass
        return {
            "success": True,
            "export_path": export_dir,
            "size": dir_size(export_dir),
        }
