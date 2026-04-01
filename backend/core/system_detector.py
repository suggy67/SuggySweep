import os
import platform


class SystemDetector:
    @staticmethod
    def detect() -> dict:
        build = int(platform.version().split(".")[-1]) if platform.version() else 0
        os_name = "Windows 11" if build >= 22000 else "Windows 10"
        edition = "Unknown"
        display_version = ""

        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            )
            edition = winreg.QueryValueEx(key, "EditionID")[0]
            display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
            winreg.CloseKey(key)
        except Exception:
            pass

        return {
            "os": os_name,
            "edition": edition,
            "version": display_version,
            "build": build,
            "full": f"{os_name} {edition} {display_version}".strip(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "username": os.getenv("USERNAME"),
        }
