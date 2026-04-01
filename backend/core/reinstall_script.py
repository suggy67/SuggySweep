"""Генерация текстовых скриптов для списка установленных программ."""

import re
from typing import Any, Dict, List


def _escape_ps(s: str) -> str:
    return s.replace("`", "``").replace('"', '`"')


def generate_powershell(programs: List[Dict[str, Any]]) -> str:
    lines: List[str] = [
        "# Suggy Sweep — список ПО для переустановки Windows",
        "# Создан автоматически. Проверьте команды перед запуском.",
        "",
        "$ErrorActionPreference = 'Continue'",
        "",
        "function Test-Winget {",
        "  return $null -ne (Get-Command winget -ErrorAction SilentlyContinue)",
        "}",
        "",
        "if (-not (Test-Winget)) {",
        '  Write-Host "winget не найден. Установите App Installer из Microsoft Store."',
        "}",
        "",
        "# --- Список программ (имя | версия | издатель) ---",
    ]
    for p in programs:
        name = str(p.get("name") or "").strip()
        if not name:
            continue
        ver = str(p.get("version") or "").strip()
        pub = str(p.get("publisher") or "").strip()
        lines.append(f"# {name} | {ver} | {pub}")
    lines.extend(
        [
            "",
            "# --- Подсказки winget (поиск по имени) ---",
            "",
        ]
    )
    for p in programs:
        name = str(p.get("name") or "").strip()
        if not name:
            continue
        safe = re.sub(r"[^\w\s\.\-]", "", name)[:80].strip()
        if not safe:
            continue
        q = _escape_ps(safe)
        lines.append(f'# winget search --name "{q}"')
    lines.extend(
        [
            "",
            "# Экспорт списка в CSV",
            '$csv = @(',
        ]
    )
    for p in programs:
        name = str(p.get("name") or "").replace('"', '""')
        ver = str(p.get("version") or "").replace('"', '""')
        pub = str(p.get("publisher") or "").replace('"', '""')
        lines.append(
            f'  [PSCustomObject]@{{ Name = "{name}"; Version = "{ver}"; Publisher = "{pub}" }}'
        )
    lines.extend(
        [
            ")",
            '$csv | Export-Csv -Path "$PSScriptRoot\\suggy_programs_export.csv" -NoTypeInformation -Encoding UTF8',
            'Write-Host "CSV: $PSScriptRoot\\suggy_programs_export.csv"',
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_plain_list(programs: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for p in programs:
        name = str(p.get("name") or "").strip()
        if not name:
            continue
        ver = str(p.get("version") or "").strip()
        pub = str(p.get("publisher") or "").strip()
        lines.append(f"{name}\t{ver}\t{pub}")
    return "\n".join(lines) + "\n"
