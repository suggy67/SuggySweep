import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List


class FileScanner:
    USER_DIRS = ["Desktop", "Documents", "Downloads", "Pictures", "Videos", "Music"]
    CATEGORIES = {
        "Документы": {".doc", ".docx", ".pdf", ".txt", ".md", ".xlsx", ".pptx"},
        "Изображения": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"},
        "Видео": {".mp4", ".mkv", ".mov", ".avi"},
        "Музыка": {".mp3", ".wav", ".flac", ".aac"},
        "Архивы": {".zip", ".rar", ".7z", ".tar", ".gz"},
        "Код/Проекты": {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yml", ".yaml"},
    }

    def __init__(self, user_home: str | None = None) -> None:
        self.user_home = user_home or os.path.expanduser("~")
        self.total_size = 0

    def scan(
        self, paths: List[str] | None = None, include_appdata: bool = True
    ) -> Generator[Dict, None, None]:
        scan_paths = paths or self._default_paths(include_appdata)
        for base_path in scan_paths:
            if not os.path.exists(base_path):
                continue
            for root, _, files in os.walk(base_path):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        stat = os.stat(filepath)
                    except OSError:
                        continue
                    ext = Path(filepath).suffix.lower()
                    item = {
                        "path": filepath,
                        "name": filename,
                        "extension": ext,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "category": self._categorize(ext),
                    }
                    self.total_size += stat.st_size
                    yield item

    def _default_paths(self, include_appdata: bool) -> List[str]:
        paths: List[str] = []
        for folder in self.USER_DIRS:
            full_path = os.path.join(self.user_home, folder)
            if os.path.exists(full_path):
                paths.append(full_path)
        if include_appdata:
            appdata = os.path.join(self.user_home, "AppData", "Roaming")
            if os.path.exists(appdata):
                paths.append(appdata)
        return paths

    def _categorize(self, ext: str) -> str:
        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category
        return "Другое"
