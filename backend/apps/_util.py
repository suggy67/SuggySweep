import os


def dir_size(path: str) -> int:
    total = 0
    for dp, _, fns in os.walk(path):
        for f in fns:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    return total


def expand(template: str) -> str:
    return template.format(
        APPDATA=os.environ.get("APPDATA", ""),
        LOCALAPPDATA=os.environ.get("LOCALAPPDATA", ""),
        USERPROFILE=os.environ.get("USERPROFILE", ""),
        USER=os.environ.get("USERPROFILE", ""),
    )


def steam_install_path() -> str | None:
    try:
        import winreg

        for key_path in (
            r"SOFTWARE\WOW6432Node\Valve\Steam",
            r"SOFTWARE\Valve\Steam",
        ):
            try:
                k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                path, _ = winreg.QueryValueEx(k, "InstallPath")
                winreg.CloseKey(k)
                if path and os.path.isdir(path):
                    return os.path.normpath(path)
            except OSError:
                continue
    except Exception:
        pass
    for candidate in (
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Steam"),
    ):
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "steam.exe")):
            return os.path.normpath(candidate)
    return None
