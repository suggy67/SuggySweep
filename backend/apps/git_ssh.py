import os
import shutil
from typing import Any, Dict, List

from apps._util import dir_size


class GitSSHExporter:
    def detect(self) -> List[Dict[str, Any]]:
        home = os.path.expanduser("~")
        gitconfig = os.path.join(home, ".gitconfig")
        ssh_dir = os.path.join(home, ".ssh")
        npmrc = os.path.join(home, ".npmrc")
        yarnrc = os.path.join(home, ".yarnrc")

        if not (
            os.path.isfile(gitconfig)
            or os.path.isdir(ssh_dir)
            or os.path.isfile(npmrc)
            or os.path.isfile(yarnrc)
        ):
            return []

        total = 0
        if os.path.isfile(gitconfig):
            total += os.path.getsize(gitconfig)
        if os.path.isdir(ssh_dir):
            total += dir_size(ssh_dir)
        for p in (npmrc, yarnrc):
            if os.path.isfile(p):
                total += os.path.getsize(p)

        return [
            {
                "id": "git_ssh",
                "name": "Git, SSH и npm/yarn",
                "path": home,
                "has_gitconfig": os.path.isfile(gitconfig),
                "has_ssh": os.path.isdir(ssh_dir),
                "has_npmrc": os.path.isfile(npmrc),
                "has_yarnrc": os.path.isfile(yarnrc),
                "total_size": total,
                "kind": "git_ssh",
            }
        ]

    def export(self, app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
        if app_id != "git_ssh":
            return {"error": "Неизвестный id"}
        items = self.detect()
        if not items:
            return {"error": "Нечего экспортировать"}
        home = items[0]["path"]
        export_dir = os.path.join(dest_path, "apps", "git_ssh")
        os.makedirs(export_dir, exist_ok=True)

        for name in (".gitconfig", ".npmrc", ".yarnrc"):
            src = os.path.join(home, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(export_dir, os.path.basename(src)))

        ssh_src = os.path.join(home, ".ssh")
        if os.path.isdir(ssh_src):
            shutil.copytree(ssh_src, os.path.join(export_dir, "ssh"), dirs_exist_ok=True)

        if not full_backup:
            pass

        return {
            "success": True,
            "export_path": export_dir,
            "size": dir_size(export_dir),
        }
