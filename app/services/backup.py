# -*- coding: utf-8 -*-
"""
Manuel yedekleme: Excel klasörünü ZIP'e alır.
'Şimdi Yedekle' butonu bunu çağırır.
"""

import datetime
import shutil
from pathlib import Path
from ..config import EXCEL_DIR, BACKUP_DIR
from .excel_io import ensure_excels

def backup_now() -> str:
    """
    EXCEL_DIR içeriğini BACKUP_DIR içine zaman damgalı ZIP olarak kopyalar.
    Dönüş: oluşturulan zip dosyasının yolu (str).
    """
    # Excel klasörleri yoksa oluştur (başlık sayfalarıyla)
    ensure_excels()

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not EXCEL_DIR.exists():
        # Yedeklenecek bir şey yok ama yine de boş bir zip oluşturma
        (BACKUP_DIR / ".keep").touch(exist_ok=True)
        return str(BACKUP_DIR)

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_base = BACKUP_DIR / f"excel-backup-{ts}"
    # ZIP oluştur
    shutil.make_archive(str(archive_base), 'zip', root_dir=str(EXCEL_DIR))
    return str(archive_base.with_suffix(".zip"))
