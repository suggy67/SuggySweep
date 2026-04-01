from typing import Any, Dict

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

_telegram = TelegramExporter()
_discord = DiscordExporter()
_vscode = VSCodeExporter()
_steam = SteamExporter()
_git_ssh = GitSSHExporter()
_obs = OBSExporter()
_qbit = QBittorrentExporter()
_fz = FileZillaExporter()
_tr = TransmissionExporter()
_putty = PuttyExporter()
_winscp = WinSCPExporter()

_TELEGRAM_IDS = frozenset(
    {"telegram", "ayugram", "64gram", "kotatogram"}
)


def export_application(app_id: str, dest_path: str, full_backup: bool = True) -> Dict[str, Any]:
    if app_id.startswith("portable_") or app_id in _TELEGRAM_IDS:
        return _telegram.export(app_id, dest_path, full_backup)
    if app_id in ("discord", "discordcanary", "discordptb"):
        return _discord.export(app_id, dest_path, full_backup)
    if app_id in ("vscode", "vscodium"):
        return _vscode.export(app_id, dest_path, full_backup)
    if app_id == "steam":
        return _steam.export(app_id, dest_path, full_backup)
    if app_id == "git_ssh":
        return _git_ssh.export(app_id, dest_path, full_backup)
    if app_id == "obs_studio":
        return _obs.export(app_id, dest_path, full_backup)
    if app_id == "qbittorrent":
        return _qbit.export(app_id, dest_path, full_backup)
    if app_id == "filezilla":
        return _fz.export(app_id, dest_path, full_backup)
    if app_id.startswith("transmission"):
        return _tr.export(app_id, dest_path, full_backup)
    if app_id == "putty":
        return _putty.export(app_id, dest_path, full_backup)
    if app_id == "winscp":
        return _winscp.export(app_id, dest_path, full_backup)
    return _telegram.export(app_id, dest_path, full_backup)
