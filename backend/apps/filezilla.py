import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size, expand


class FileZillaExporter:
    def detect(self) -> List[Dict[str, Any]]:
        path = expand("{APPDATA}\\FileZilla")
        if not os.path.isdir(path):
            return []
        sm = os.path.join(path, "sitemanager.xml")
        return [
            {
                "id": "filezilla",
                "name": "FileZilla",
                "path": path,
                "has_sitemanager": os.path.isfile(sm),
                "total_size": dir_size(path),
                "kind": "filezilla",
            }
        ]

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        if app_id != "filezilla":
            return {"error": "Неизвестный id"}
        items = self.detect()
        if not items:
            return {"error": "FileZilla не найдена"}
        export_dir = os.path.join(dest_path, "apps", "filezilla")
        shutil.copytree(items[0]["path"], export_dir, dirs_exist_ok=True)
        if not full_backup:
            pass
        return {
            "success": True,
            "export_path": export_dir,
            "size": dir_size(export_dir),
        }
