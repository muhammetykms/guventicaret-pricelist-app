# -*- coding: utf-8 -*-
from typing import List, Tuple, Optional, Dict, Any
from ..config import EXCEL_DIR, EXCEL_FILES
from ..services.excel_store import ExcelStore

COLUMNS = ["İsim","Birim Fiyat (TL)","Satış Fiyat (TL)","ID"]

class KatkiRepository:
    def __init__(self):
        self.store = ExcelStore(EXCEL_DIR / EXCEL_FILES["Katkı Maddesi"], "Katkı Maddesi", COLUMNS)

    def all(self, q: str = "") -> List[Tuple]:
        rows = self.store.list(q, search_cols=["İsim"])
        out=[]
        for r in rows:
            out.append((
                r.get("ID"),
                r.get("İsim",""), r.get("Birim Fiyat (TL)",""), r.get("Satış Fiyat (TL)",""),
            ))
        return out

    def get(self, pid: int) -> Optional[Tuple]:
        r = self.store.get(pid)
        if not r: return None
        return (
            r.get("ID"),
            r.get("İsim",""),
            r.get("Birim Fiyat (TL)",""), r.get("Satış Fiyat (TL)",""),
        )

    def insert(self, data: Dict[str, Any]) -> int:
        row = {
            "İsim": data.get("isim") or "",
            "Birim Fiyat (TL)": data.get("birim_fiyat") or "",
            "Satış Fiyat (TL)": data.get("satis_fiyat") or "",
        }
        return self.store.insert(row)

    def update(self, pid: int, data: Dict[str, Any]) -> None:
        patch = {
            "İsim": data.get("isim"),
            "Birim Fiyat (TL)": data.get("birim_fiyat"),
            "Satış Fiyat (TL)": data.get("satis_fiyat"),
        }
        self.store.update(pid, patch)

    def delete(self, pid: int) -> None:
        self.store.delete(pid)
