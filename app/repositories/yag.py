# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from ..config import EXCEL_DIR, EXCEL_FILES
from ..services.excel_store import ExcelStore

COLUMNS = ["Marka","Urun","Viskozite","Litre","Birim Fiyat (TL)","Satış Fiyat (TL)","ID"]

class YagRepository:
    def __init__(self):
        self.store = ExcelStore(
            file_path=EXCEL_DIR / EXCEL_FILES["Yağ"],
            sheet_name="Yağ",
            columns=COLUMNS
        )

    def all(self, q: str = "") -> List[Tuple]:
        rows = self.store.list(q, search_cols=["Marka","Urun","Viskozite"])
        out = []
        for r in rows:
            out.append((
                r.get("Marka",""), r.get("Urun",""), r.get("Viskozite",""),
                r.get("Litre",""), r.get("Birim Fiyat (TL)",""), r.get("Satış Fiyat (TL)",""),
                r.get("ID")
            ))
        return out

    def get(self, pid: int) -> Optional[Tuple]:
        r = self.store.get(pid)
        if not r: return None
        return (
            r.get("ID"),
            r.get("Marka",""), r.get("Urun",""), r.get("Viskozite",""),
            r.get("Litre",""), r.get("Birim Fiyat (TL)",""), r.get("Satış Fiyat (TL)",""),
        )

    def insert(self, data: Dict[str, Any]) -> int:
        # data: marka, urun, viskozite, litre, birim_fiyat(str), satis_fiyat(str)
        row = {
            "Marka": data.get("marka") or "",
            "Urun": data.get("urun") or "",
            "Viskozite": data.get("viskozite") or "",
            "Litre": data.get("litre") or "",
            "Birim Fiyat (TL)": data.get("birim_fiyat") or "",
            "Satış Fiyat (TL)": data.get("satis_fiyat") or "",
        }
        return self.store.insert(row)

    def update(self, pid: int, data: Dict[str, Any]) -> None:
        patch = {
            "Marka": data.get("marka"),
            "Urun": data.get("urun"),
            "Viskozite": data.get("viskozite"),
            "Litre": data.get("litre"),
            "Birim Fiyat (TL)": data.get("birim_fiyat"),
            "Satış Fiyat (TL)": data.get("satis_fiyat"),
        }
        self.store.update(pid, patch)

    def delete(self, pid: int) -> None:
        self.store.delete(pid)
