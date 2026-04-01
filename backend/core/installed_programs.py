import winreg
from typing import Any, Dict, List, Set, Tuple


def _subkey_programs(hive: int, path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        parent = winreg.OpenKey(hive, path)
    except OSError:
        return out
    i = 0
    while True:
        try:
            sub_name = winreg.EnumKey(parent, i)
        except OSError:
            break
        i += 1
        try:
            key = winreg.OpenKey(parent, sub_name)
        except OSError:
            continue
        try:
            try:
                display = winreg.QueryValueEx(key, "DisplayName")[0]
            except OSError:
                winreg.CloseKey(key)
                continue
            if not display or not str(display).strip():
                winreg.CloseKey(key)
                continue
            try:
                if int(winreg.QueryValueEx(key, "SystemComponent")[0]) == 1:
                    winreg.CloseKey(key)
                    continue
            except (OSError, ValueError, TypeError):
                pass

            version = _query_str(key, "DisplayVersion")
            publisher = _query_str(key, "Publisher")
            install_loc = _query_str(key, "InstallLocation")
            uninstall = _query_str(key, "QuietUninstallString") or _query_str(
                key, "UninstallString"
            )
            est_size = None
            try:
                est_size = int(winreg.QueryValueEx(key, "EstimatedSize")[0]) * 1024
            except (OSError, ValueError, TypeError):
                pass

            out.append(
                {
                    "name": str(display).strip(),
                    "version": version,
                    "publisher": publisher,
                    "install_location": install_loc,
                    "uninstall_command": uninstall,
                    "estimated_size_bytes": est_size,
                }
            )
        finally:
            try:
                winreg.CloseKey(key)
            except OSError:
                pass
    try:
        winreg.CloseKey(parent)
    except OSError:
        pass
    return out


def _query_str(key: Any, name: str) -> str:
    try:
        v, _ = winreg.QueryValueEx(key, name)
        return str(v).strip() if v is not None else ""
    except OSError:
        return ""


def list_installed_programs(limit: int = 4000) -> Dict[str, Any]:
    paths = (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    )
    seen: Set[Tuple[str, str]] = set()
    merged: List[Dict[str, Any]] = []
    for hive, path in paths:
        for item in _subkey_programs(hive, path):
            key = (item["name"].lower(), (item.get("version") or "").lower())
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    merged.sort(key=lambda x: x["name"].lower())
    total = len(merged)
    truncated = total > limit
    return {
        "programs": merged[:limit],
        "total": total,
        "truncated": truncated,
    }
