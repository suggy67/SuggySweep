from typing import Any, Dict, List

from apps.discord import DiscordExporter
from apps.filezilla import FileZillaExporter
from apps.git_ssh import GitSSHExporter
from apps.obs import OBSExporter
from apps.putty import PuttyExporter
from apps.qbittorrent import QBittorrentExporter
from apps.steam import SteamExporter
from apps.telegram import TelegramExporter
from apps.transmission import TransmissionExporter
from apps.vscode import VSCodeExporter
from apps.winscp import WinSCPExporter


def detect_all_apps() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "telegram_clients": TelegramExporter().detect(),
        "discord": DiscordExporter().detect(),
        "vscode": VSCodeExporter().detect(),
        "steam": SteamExporter().detect(),
        "git_ssh": GitSSHExporter().detect(),
        "obs": OBSExporter().detect(),
        "qbittorrent": QBittorrentExporter().detect(),
        "filezilla": FileZillaExporter().detect(),
        "transmission": TransmissionExporter().detect(),
        "putty": PuttyExporter().detect(),
        "winscp": WinSCPExporter().detect(),
    }
