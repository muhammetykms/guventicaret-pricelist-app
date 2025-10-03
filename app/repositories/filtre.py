# -*- coding: utf-8 -*-
from typing import List, Tuple, Optional, Dict, Any
from ..config import EXCEL_DIR, EXCEL_FILES
from ..services.excel_store import ExcelStore

COLUMNS = ["Mal Kodu","Mal Adı","Birim Fiyat (TL)","Satış Fiyat (TL)","ID"]

class FiltreRepository:
    def __init__(self):
        self.store = ExcelStore(EXCEL_DIR / EXCEL_FILES["Filtre"], "Filtre", COLUMNS)

    def all(self, q: str = "") -> List[Tuple]:
        rows = self.store.list(q, search_cols=["Mal Kodu","Mal Adı"])
        out=[]
        for r in rows:
            out.append((
                r.get("Mal Kodu",""), r.get("Mal Adı",""),
                r.get("Birim Fiyat (TL)",""), r.get("Satış Fiyat (TL)",""),
                r.get("ID")
            ))
        return out

    def get(self, pid: int) -> Optional[Tuple]:
        r = self.store.get(pid)
        if not r: return None
        return (
            r.get("ID"),
            r.get("Mal Kodu",""), r.get("Mal Adı",""),
            r.get("Birim Fiyat (TL)",""), r.get("Satış Fiyat (TL)",""),
        )

    def insert(self, data: Dict[str, Any]) -> int:
        row = {
            "Mal Kodu": data.get("mal_kodu") or "",
            "Mal Adı": data.get("mal_adi") or "",
            "Birim Fiyat (TL)": data.get("birim_fiyat") or "",
            "Satış Fiyat (TL)": data.get("satis_fiyat") or "",
        }
        return self.store.insert(row)

    def update(self, pid: int, data: Dict[str, Any]) -> None:
        patch = {
            "Mal Kodu": data.get("mal_kodu"),
            "Mal Adı": data.get("mal_adi"),
            "Birim Fiyat (TL)": data.get("birim_fiyat"),
            "Satış Fiyat (TL)": data.get("satis_fiyat"),
        }
        self.store.update(pid, patch)

    def delete(self, pid: int) -> None:
        self.store.delete(pid)
