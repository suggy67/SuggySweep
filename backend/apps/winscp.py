import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size, expand


class WinSCPExporter:
    def _candidates(self) -> List[str]:
        paths = [
            expand("{APPDATA}\\WinSCP.ini"),
            expand("{USERPROFILE}\\Documents\\WinSCP.ini"),
            os.path.join(expand("{APPDATA}"), "WinSCP"),
        ]
        out: List[str] = []
        seen: set[str] = set()
        for p in paths:
            if not p:
                continue
            n = os.path.normcase(os.path.normpath(p))
            if not os.path.exists(p) or n in seen:
                continue
            seen.add(n)
            out.append(p)
        return out

    def detect(self) -> List[Dict[str, Any]]:
        c = self._candidates()
        if not c:
            return []
        total = 0
        for p in c:
            if os.path.isfile(p):
                total += os.path.getsize(p)
            elif os.path.isdir(p):
                total += dir_size(p)
        return [
            {
                "id": "winscp",
                "name": "WinSCP",
                "path": c[0] if len(c) == 1 else expand("{APPDATA}"),
                "paths_found": c,
                "total_size": total,
                "kind": "winscp",
            }
        ]

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        if app_id != "winscp":
            return {"error": "Неизвестный id"}
        c = self._candidates()
        if not c:
            return {"error": "WinSCP не найден"}
        export_dir = os.path.join(dest_path, "apps", "winscp")
        os.makedirs(export_dir, exist_ok=True)
        for src in c:
            name = os.path.basename(src)
            dest = os.path.join(export_dir, name)
            if os.path.isfile(src):
                shutil.copy2(src, dest)
            elif os.path.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
        if not full_backup:
            pass
        return {
            "success": True,
            "export_path": export_dir,
            "size": dir_size(export_dir),
        }
