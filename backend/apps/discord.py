import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size, expand


class DiscordExporter:
    VARIANTS = {
        "discord": {"name": "Discord", "dir": "{APPDATA}\\discord"},
        "discordcanary": {"name": "Discord Canary", "dir": "{APPDATA}\\discordcanary"},
        "discordptb": {"name": "Discord PTB", "dir": "{APPDATA}\\discordptb"},
    }

    def detect(self) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        for app_id, info in self.VARIANTS.items():
            path = expand(info["dir"])
            if not os.path.isdir(path):
                continue
            bd = expand("{APPDATA}\\BetterDiscord")
            has_bd = os.path.isdir(bd) and app_id == "discord"
            extra = dir_size(bd) if has_bd else 0
            found.append(
                {
                    "id": app_id,
                    "name": info["name"] + (" + BetterDiscord" if has_bd else ""),
                    "path": path,
                    "has_betterdiscord": has_bd,
                    "total_size": dir_size(path) + extra,
                    "kind": "discord",
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
                os.path.join(export_dir, "discord_data"),
                dirs_exist_ok=True,
            )
            bd = expand("{APPDATA}\\BetterDiscord")
            if item.get("has_betterdiscord") and os.path.isdir(bd):
                shutil.copytree(
                    bd,
                    os.path.join(export_dir, "BetterDiscord"),
                    dirs_exist_ok=True,
                )
            if not full_backup:
                pass
            return {
                "success": True,
                "export_path": export_dir,
                "size": dir_size(export_dir),
            }
        return {"error": f"{app_id} не найден"}
