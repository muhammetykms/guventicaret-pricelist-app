# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
from ..config import EXCEL_DIR, EXCEL_FILES

def ensure_excels():
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)

    schemas = {
        "Yağ": ["Marka","Urun","Viskozite","Litre","Birim Fiyat (TL)","Satış Fiyat (TL)","ID"],
        "Akü": ["ÜRÜN","KDV HARİÇ LİSTE FİYATI","5% (2 ay vade)","8% (nakit)","HURDA","HRD DÜŞÜLMÜŞ","ID"],
        "Filtre": ["Mal Kodu","Mal Adı","Birim Fiyat (TL)","Satış Fiyat (TL)","ID"],
        "Antifriz": ["Marka","Urun","Litre","Birim Fiyat (TL)","Satış Fiyat (TL)","ID"],
        "Katkı Maddesi": ["İsim","Birim Fiyat (TL)","Satış Fiyat (TL)","ID"],
    }

    for cat, fname in EXCEL_FILES.items():
        p = EXCEL_DIR / fname
        if not p.exists():
            with pd.ExcelWriter(p, engine="openpyxl") as w:
                pd.DataFrame(columns=schemas[cat]).to_excel(w, index=False, sheet_name=cat)
        else:
            # başlıkları düzelt
            try:
                df = pd.read_excel(p, sheet_name=cat)
            except Exception:
                df = pd.DataFrame(columns=schemas[cat])
            changed = False
            for c in schemas[cat]:
                if c not in df.columns:
                    df[c] = None
                    changed = True
            df = df[schemas[cat]]
            if changed:
                with pd.ExcelWriter(p, engine="openpyxl", mode="w") as w:
                    df.to_excel(w, index=False, sheet_name=cat)
