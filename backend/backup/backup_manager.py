import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class BackupManager:
    MANIFEST_FILE = "suggy_manifest.json"

    def preview_manifest(
        self, backup_path: str, preview_limit: int = 500
    ) -> Dict[str, Any]:
        """Читает манифест из папки бэкапа или ZIP без полного извлечения."""
        if backup_path.endswith(".zip"):
            try:
                with zipfile.ZipFile(backup_path, "r") as zf:
                    manifest_member: Optional[str] = None
                    for name in zf.namelist():
                        norm = name.replace("\\", "/")
                        if norm.endswith(self.MANIFEST_FILE):
                            manifest_member = name
                            break
                    if not manifest_member:
                        return {"error": "Манифест в архиве не найден"}
                    with zf.open(manifest_member) as f:
                        manifest = json.load(f)
            except (OSError, zipfile.BadZipFile, json.JSONDecodeError) as e:
                return {"error": str(e)}
        else:
            manifest_path = os.path.join(backup_path, self.MANIFEST_FILE)
            if not os.path.isfile(manifest_path):
                return {"error": "Манифест не найден"}
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                return {"error": str(e)}

        files = manifest.get("files", [])
        preview = files[:preview_limit]
        return {
            "version": manifest.get("version"),
            "created": manifest.get("created"),
            "backup_name": manifest.get("backup_name"),
            "source_system": manifest.get("source_system"),
            "total_files": len(files),
            "total_size_manifest": manifest.get("total_size"),
            "files_preview": preview,
            "truncated": len(files) > preview_limit,
        }

    def create_backup(
        self,
        files: List[Dict[str, Any]],
        dest_drive: str,
        backup_name: Optional[str] = None,
        compression: str = "folder",
        compression_level: int = 6,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        if not backup_name:
            backup_name = f"suggy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        root = dest_drive.rstrip("\\") + "\\"
        backup_dir = os.path.join(root, "SuggySweep_Backups", backup_name)
        os.makedirs(backup_dir, exist_ok=True)

        system_drive = os.environ.get("SystemDrive", "C:") + "\\"
        manifest: Dict[str, Any] = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "backup_name": backup_name,
            "source_system": self._get_system_info(),
            "files": [],
            "total_files": len(files),
            "total_size": sum(f.get("size", 0) for f in files),
        }

        copied = 0
        errors: List[Dict[str, Any]] = []

        for i, file_info in enumerate(files):
            try:
                src = file_info["path"]
                if not os.path.isfile(src):
                    continue
                try:
                    rel_path = os.path.relpath(src, system_drive)
                except ValueError:
                    rel_path = file_info.get("name", os.path.basename(src))
                dest = os.path.join(backup_dir, "files", rel_path)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                file_hash = self._hash_file(dest)
                manifest["files"].append(
                    {
                        "original_path": src,
                        "backup_path": os.path.join("files", rel_path).replace("/", "\\"),
                        "size": file_info.get("size", os.path.getsize(dest)),
                        "hash": file_hash,
                        "category": file_info.get("category", ""),
                    }
                )
                copied += 1
                if progress_callback:
                    progress_callback(
                        {
                            "current": i + 1,
                            "total": len(files),
                            "percent": ((i + 1) / max(len(files), 1)) * 100,
                            "current_file": src,
                            "copied": copied,
                            "errors": len(errors),
                        }
                    )
            except Exception as e:
                errors.append({"file": file_info.get("path", ""), "error": str(e)})

        manifest["errors"] = errors
        manifest["completed"] = datetime.now().isoformat()

        with open(
            os.path.join(backup_dir, self.MANIFEST_FILE), "w", encoding="utf-8"
        ) as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        if compression == "zip":
            archive_path = f"{backup_dir}.zip"
            self._create_zip(backup_dir, archive_path, compression_level)
            shutil.rmtree(backup_dir)
            return {
                "success": True,
                "path": archive_path,
                "files_copied": copied,
                "errors": len(errors),
                "size": os.path.getsize(archive_path),
            }

        return {
            "success": True,
            "path": backup_dir,
            "files_copied": copied,
            "errors": len(errors),
            "size": self._dir_size(backup_dir),
        }

    def restore_backup(
        self,
        backup_path: str,
        restore_items: Optional[List[str]] = None,
        dest_base: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        if backup_path.endswith(".zip"):
            import tempfile

            temp_dir = tempfile.mkdtemp(prefix="suggy_restore_")
            with zipfile.ZipFile(backup_path) as zf:
                zf.extractall(temp_dir)
            backup_dir = temp_dir
        else:
            backup_dir = backup_path

        manifest_path = os.path.join(backup_dir, self.MANIFEST_FILE)
        if not os.path.exists(manifest_path):
            return {"error": "Манифест бэкапа не найден"}

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        restored = 0
        err_list: List[Dict[str, Any]] = []

        for i, file_entry in enumerate(manifest.get("files", [])):
            if restore_items and file_entry["original_path"] not in restore_items:
                continue
            src = os.path.join(backup_dir, file_entry["backup_path"])
            if dest_base:
                dest = os.path.join(dest_base, file_entry["backup_path"])
            else:
                dest = file_entry["original_path"]
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                expected = file_entry.get("hash", "")
                if expected and self._hash_file(dest) != expected:
                    err_list.append(
                        {"file": dest, "error": "Несовпадение хеша"}
                    )
                restored += 1
                if progress_callback:
                    total = len(manifest["files"])
                    progress_callback(
                        {
                            "current": i + 1,
                            "total": total,
                            "percent": ((i + 1) / max(total, 1)) * 100,
                            "current_file": dest,
                        }
                    )
            except Exception as e:
                err_list.append({"file": file_entry.get("original_path", ""), "error": str(e)})

        return {
            "success": True,
            "restored": restored,
            "errors": len(err_list),
            "error_details": err_list,
        }

    @staticmethod
    def _hash_file(path: str, algorithm: str = "sha256") -> str:
        h = hashlib.new(algorithm)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _create_zip(source_dir: str, output_path: str, level: int = 6) -> None:
        with zipfile.ZipFile(
            output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=min(level, 9)
        ) as zf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, source_dir)
                    zf.write(filepath, arcname)

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

    @staticmethod
    def _get_system_info() -> Dict[str, str]:
        import platform

        return {
            "os": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "node": platform.node(),
            "username": os.getenv("USERNAME") or "",
        }
