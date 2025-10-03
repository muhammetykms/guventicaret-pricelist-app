# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from ..config import EXCEL_DIR, EXCEL_FILES
from ..services.excel_store import ExcelStore

COLUMNS = ["ÜRÜN","KDV HARİÇ LİSTE FİYATI","5% (2 ay vade)","8% (nakit)","HURDA","HRD DÜŞÜLMÜŞ","ID"]

class AkuRepository:
    def __init__(self):
        self.store = ExcelStore(EXCEL_DIR / EXCEL_FILES["Akü"], "Akü", COLUMNS)

    def all(self, q: str = "") -> List[Tuple]:
        rows = self.store.list(q, search_cols=["ÜRÜN"])
        out=[]
        for r in rows:
            out.append((
                r.get("ID"),
                r.get("ÜRÜN",""), r.get("KDV HARİÇ LİSTE FİYATI",""),
                r.get("5% (2 ay vade)",""), r.get("8% (nakit)",""),
                r.get("HURDA",""), r.get("HRD DÜŞÜLMÜŞ",""),
            ))
        return out

    def get(self, pid: int) -> Optional[Tuple]:
        r = self.store.get(pid)
        if not r: return None
        return (
            r.get("ID"),
            r.get("ÜRÜN",""), r.get("KDV HARİÇ LİSTE FİYATI",""),
            r.get("5% (2 ay vade)",""), r.get("8% (nakit)",""),
            r.get("HURDA",""), r.get("HRD DÜŞÜLMÜŞ",""),
        )

    def insert(self, data: Dict[str, Any]) -> int:
        row = {
            "ÜRÜN": data.get("urun") or "",
            "KDV HARİÇ LİSTE FİYATI": data.get("list_no_vat") or "",
            "5% (2 ay vade)": data.get("disc5") or "",
            "8% (nakit)": data.get("disc8") or "",
            "HURDA": data.get("scrap") or "",
            "HRD DÜŞÜLMÜŞ": data.get("hrd") or "",
        }
        return self.store.insert(row)

    def update(self, pid: int, data: Dict[str, Any]) -> None:
        patch = {
            "ÜRÜN": data.get("urun"),
            "KDV HARİÇ LİSTE FİYATI": data.get("list_no_vat"),
            "5% (2 ay vade)": data.get("disc5"),
            "8% (nakit)": data.get("disc8"),
            "HURDA": data.get("scrap"),
            "HRD DÜŞÜLMÜŞ": data.get("hrd"),
        }
        self.store.update(pid, patch)

    def delete(self, pid: int) -> None:
        self.store.delete(pid)
