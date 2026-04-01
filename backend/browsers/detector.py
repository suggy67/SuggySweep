import os
import shutil
from typing import Any, Dict, List


class BrowserDetector:
    BROWSERS: Dict[str, Dict[str, Any]] = {
        "chrome": {
            "name": "Google Chrome",
            "paths": ["{LOCALAPPDATA}\\Google\\Chrome\\User Data"],
            "type": "chromium",
        },
        "edge": {
            "name": "Microsoft Edge",
            "paths": ["{LOCALAPPDATA}\\Microsoft\\Edge\\User Data"],
            "type": "chromium",
        },
        "firefox": {
            "name": "Mozilla Firefox",
            "paths": ["{APPDATA}\\Mozilla\\Firefox\\Profiles"],
            "type": "firefox",
        },
        "opera": {
            "name": "Opera",
            "paths": ["{APPDATA}\\Opera Software\\Opera Stable"],
            "type": "chromium",
        },
        "opera_gx": {
            "name": "Opera GX",
            "paths": ["{APPDATA}\\Opera Software\\Opera GX Stable"],
            "type": "chromium",
        },
        "brave": {
            "name": "Brave",
            "paths": ["{LOCALAPPDATA}\\BraveSoftware\\Brave-Browser\\User Data"],
            "type": "chromium",
        },
        "vivaldi": {
            "name": "Vivaldi",
            "paths": ["{LOCALAPPDATA}\\Vivaldi\\User Data"],
            "type": "chromium",
        },
        "yandex": {
            "name": "Yandex Browser",
            "paths": ["{LOCALAPPDATA}\\Yandex\\YandexBrowser\\User Data"],
            "type": "chromium",
        },
    }

    def detect_installed(self) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        for browser_id, info in self.BROWSERS.items():
            for path_template in info["paths"]:
                path = self._expand_path(path_template)
                if os.path.exists(path):
                    found.append(
                        {
                            "id": browser_id,
                            "name": info["name"],
                            "path": path,
                            "type": info["type"],
                            "profiles": self._get_profiles(path, info["type"]),
                            "total_size": self._get_dir_size(path),
                        }
                    )
                    break
        return found

    def _get_profiles(self, base_path: str, browser_type: str) -> List[Dict[str, Any]]:
        profiles: List[Dict[str, Any]] = []
        if browser_type == "chromium":
            try:
                for item in os.listdir(base_path):
                    profile_path = os.path.join(base_path, item)
                    if not os.path.isdir(profile_path):
                        continue
                    if item == "Default" or item.startswith("Profile "):
                        profiles.append(
                            {
                                "name": item,
                                "path": profile_path,
                                "has_passwords": os.path.exists(
                                    os.path.join(profile_path, "Login Data")
                                ),
                                "has_cookies": os.path.exists(
                                    os.path.join(profile_path, "Cookies")
                                ),
                                "has_history": os.path.exists(
                                    os.path.join(profile_path, "History")
                                ),
                            }
                        )
            except OSError:
                pass
        elif browser_type == "firefox":
            import configparser

            profiles_ini = os.path.join(os.path.dirname(base_path), "profiles.ini")
            if os.path.exists(profiles_ini):
                config = configparser.ConfigParser()
                config.read(profiles_ini)
                for section in config.sections():
                    if not section.startswith("Profile"):
                        continue
                    name = config.get(section, "Name", fallback="Unknown")
                    is_rel = config.getint(section, "IsRelative", fallback=1)
                    p = config.get(section, "Path", fallback="")
                    profile_path = (
                        os.path.join(base_path, p) if is_rel else p
                    )
                    if os.path.isdir(profile_path):
                        profiles.append(
                            {
                                "name": name,
                                "path": profile_path,
                                "has_passwords": os.path.exists(
                                    os.path.join(profile_path, "logins.json")
                                ),
                                "has_cookies": os.path.exists(
                                    os.path.join(profile_path, "cookies.sqlite")
                                ),
                            }
                        )
        return profiles

    def export_profile(
        self, browser_id: str, profile_name: str, dest_path: str, options: Dict[str, bool]
    ) -> Dict[str, Any]:
        if browser_id not in self.BROWSERS:
            return {"error": "Неизвестный браузер"}
        browser = self.BROWSERS[browser_id]
        base = self._expand_path(browser["paths"][0])
        profile_path = os.path.join(base, profile_name)
        if not os.path.isdir(profile_path):
            return {"error": "Профиль не найден"}

        export_dir = os.path.join(dest_path, "browsers", browser_id, profile_name)
        os.makedirs(export_dir, exist_ok=True)
        files_to_copy: List[str] = []

        if options.get("bookmarks"):
            if browser["type"] == "chromium":
                files_to_copy.extend(["Bookmarks", "Bookmarks.bak"])
            else:
                files_to_copy.append("places.sqlite")
        if options.get("passwords"):
            if browser["type"] == "chromium":
                files_to_copy.extend(["Login Data", "Login Data-journal"])
            else:
                files_to_copy.extend(["logins.json", "key4.db", "key3.db"])
        if options.get("cookies"):
            if browser["type"] == "chromium":
                files_to_copy.extend(["Cookies", "Cookies-journal"])
            else:
                files_to_copy.append("cookies.sqlite")
        if options.get("history") and browser["type"] == "chromium":
            files_to_copy.extend(["History", "History-journal"])
        if options.get("settings") and browser["type"] == "chromium":
            files_to_copy.extend(["Preferences", "Secure Preferences"])

        copied = 0
        for f in files_to_copy:
            src = os.path.join(profile_path, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(export_dir, f))
                copied += 1

        if options.get("extensions") and browser["type"] == "chromium":
            ext_dir = os.path.join(profile_path, "Extensions")
            if os.path.isdir(ext_dir):
                shutil.copytree(
                    ext_dir,
                    os.path.join(export_dir, "Extensions"),
                    dirs_exist_ok=True,
                )

        return {"copied_files": copied, "export_path": export_dir}

    @staticmethod
    def _expand_path(template: str) -> str:
        return template.format(
            LOCALAPPDATA=os.environ.get("LOCALAPPDATA", ""),
            APPDATA=os.environ.get("APPDATA", ""),
        )

    @staticmethod
    def _get_dir_size(path: str) -> int:
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except OSError:
                    pass
        return total
