# app/config.py
# -*- coding: utf-8 -*-
from pathlib import Path
import sys

def _root_dir() -> Path:
    # PyInstaller altında (frozen) EXE'nin klasörü kökümüz olsun:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    # Geliştirme modunda mevcut dosyadan yukarı:
    return Path(__file__).resolve().parents[1]

ROOT_DIR  = _root_dir()
DB_PATH   = ROOT_DIR / "db" / "guventicaret.db"
EXCEL_DIR = ROOT_DIR / "excel"
BACKUP_DIR= ROOT_DIR / "backups"
ASSETS_DIR= ROOT_DIR / "assets"

THEME = {
    "BG": "#f4f7f4",
    "GREEN": "#0a7a3b",
    "RED": "#b22222",
}

CATEGORIES = ["Yağ", "Akü", "Filtre", "Antifriz", "Katkı Maddesi"]

EXCEL_FILES = {
    "Yağ": "Yaglar.xlsx",
    "Akü": "Akuler.xlsx",
    "Filtre": "Filtreler.xlsx",
    "Antifriz": "Antifriz.xlsx",
    "Katkı Maddesi": "KatkiMaddeleri.xlsx",
}

MAC_SCALING = 1.6
