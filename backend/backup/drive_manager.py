import ctypes
import os
import string
from typing import Any, Dict, List


class DriveManager:
    DRIVE_TYPES = {
        0: "Unknown",
        1: "No Root Dir",
        2: "Removable",
        3: "Fixed",
        4: "Network",
        5: "CD-ROM",
        6: "RAM Disk",
    }

    def get_available_drives(self) -> List[Dict[str, Any]]:
        drives: List[Dict[str, Any]] = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()

        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive_path = f"{letter}:\\"
                try:
                    drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
                    free_bytes = ctypes.c_ulonglong(0)
                    total_bytes = ctypes.c_ulonglong(0)
                    total_free = ctypes.c_ulonglong(0)
                    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                        drive_path,
                        ctypes.byref(free_bytes),
                        ctypes.byref(total_bytes),
                        ctypes.byref(total_free),
                    )
                    vol_name = ctypes.create_unicode_buffer(1024)
                    fs_name = ctypes.create_unicode_buffer(1024)
                    serial = ctypes.c_ulong(0)
                    ctypes.windll.kernel32.GetVolumeInformationW(
                        drive_path,
                        vol_name,
                        1024,
                        ctypes.byref(serial),
                        None,
                        None,
                        fs_name,
                        1024,
                    )
                    system_drive = os.environ.get("SystemDrive", "C:")
                    is_system = drive_path.rstrip("\\") == system_drive
                    drives.append(
                        {
                            "letter": letter,
                            "path": drive_path,
                            "label": vol_name.value or f"Диск ({letter}:)",
                            "type": self.DRIVE_TYPES.get(drive_type, "Unknown"),
                            "type_id": drive_type,
                            "filesystem": fs_name.value,
                            "total_bytes": total_bytes.value,
                            "free_bytes": free_bytes.value,
                            "used_bytes": total_bytes.value - free_bytes.value,
                            "is_system": is_system,
                            "is_removable": drive_type == 2,
                            "is_suitable_for_backup": (
                                drive_type in (2, 3)
                                and not is_system
                                and free_bytes.value > 100 * 1024 * 1024
                            ),
                        }
                    )
                except Exception:
                    pass
            bitmask >>= 1

        return drives

    def check_space(self, drive_letter: str, required_bytes: int) -> Dict[str, Any]:
        for drive in self.get_available_drives():
            if drive["letter"] == drive_letter.upper():
                has_space = drive["free_bytes"] >= required_bytes
                return {
                    "has_space": has_space,
                    "free_bytes": drive["free_bytes"],
                    "required_bytes": required_bytes,
                    "deficit_bytes": max(0, required_bytes - drive["free_bytes"]),
                }
        return {"error": f"Диск {drive_letter}: не найден"}
