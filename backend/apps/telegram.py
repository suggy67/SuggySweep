import ctypes
import os
import shutil
import string
from typing import Any, Dict, List


class TelegramExporter:
    TELEGRAM_APPS = {
        "telegram": {
            "name": "Telegram Desktop",
            "dirs": [
                "{APPDATA}\\Telegram Desktop",
                "{USERPROFILE}\\AppData\\Local\\Telegram Desktop",
            ],
            "data_dir": "tdata",
        },
        "ayugram": {
            "name": "AyuGram Desktop",
            "dirs": ["{APPDATA}\\AyuGram Desktop", "{APPDATA}\\AyuGramDesktop"],
            "data_dir": "tdata",
        },
        "64gram": {
            "name": "64Gram Desktop",
            "dirs": ["{APPDATA}\\64Gram Desktop"],
            "data_dir": "tdata",
        },
        "kotatogram": {
            "name": "Kotatogram Desktop",
            "dirs": ["{APPDATA}\\Kotatogram Desktop"],
            "data_dir": "tdata",
        },
    }

    def detect(self) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        seen_paths: set[str] = set()
        for app_id, info in self.TELEGRAM_APPS.items():
            for dir_template in info["dirs"]:
                path = self._expand(dir_template)
                if not os.path.exists(path) or path in seen_paths:
                    continue
                seen_paths.add(path)
                tdata_path = os.path.join(path, info["data_dir"])
                has_tdata = os.path.exists(tdata_path)
                found.append(
                    {
                        "id": app_id,
                        "name": info["name"],
                        "path": path,
                        "has_tdata": has_tdata,
                        "tdata_size": self._dir_size(tdata_path) if has_tdata else 0,
                        "total_size": self._dir_size(path),
                        "is_portable": False,
                    }
                )
                break
        found.extend(self._find_portable())
        return found

    def export(
        self, app_id: str, dest_path: str, full_backup: bool = True
    ) -> Dict[str, Any]:
        for detected in self.detect():
            if detected["id"] == app_id:
                export_dir = os.path.join(dest_path, "apps", app_id)
                if full_backup:
                    shutil.copytree(detected["path"], export_dir, dirs_exist_ok=True)
                else:
                    os.makedirs(export_dir, exist_ok=True)
                    tdata_src = os.path.join(detected["path"], "tdata")
                    if os.path.exists(tdata_src):
                        shutil.copytree(
                            tdata_src,
                            os.path.join(export_dir, "tdata"),
                            dirs_exist_ok=True,
                        )
                return {
                    "success": True,
                    "export_path": export_dir,
                    "size": self._dir_size(export_dir),
                }
        return {"error": f"Приложение {app_id} не найдено"}

    def _find_portable(self) -> List[Dict[str, Any]]:
        portable: List[Dict[str, Any]] = []
        try:
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for i, letter in enumerate(string.ascii_uppercase):
                if not (bitmask >> i) & 1:
                    continue
                drive = f"{letter}:\\"
                for name in ["Telegram", "Telegram Desktop", "AyuGram"]:
                    check_path = os.path.join(drive, name)
                    tdata = os.path.join(check_path, "tdata")
                    if os.path.isdir(tdata):
                        portable.append(
                            {
                                "id": f"portable_{letter}_{name.lower().replace(' ', '_')}",
                                "name": f"{name} (Portable, {letter}:)",
                                "path": check_path,
                                "has_tdata": True,
                                "tdata_size": self._dir_size(tdata),
                                "total_size": self._dir_size(check_path),
                                "is_portable": True,
                            }
                        )
        except Exception:
            pass
        return portable

    @staticmethod
    def _expand(template: str) -> str:
        return template.format(
            APPDATA=os.environ.get("APPDATA", ""),
            USERPROFILE=os.environ.get("USERPROFILE", ""),
        )

    @staticmethod
    def _dir_size(path: str) -> int:
        total = 0
        for dp, _, fns in os.walk(path):
            for f in fns:
                try:
                    total += os.path.getsize(os.path.join(dp, f))
                except OSError:
                    pass
        return total
