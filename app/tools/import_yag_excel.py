# -*- coding: utf-8 -*-
import argparse, pandas as pd, re
from ..repositories.db import connect, ensure_schema
from ..repositories.yag import YagRepository
from ..services.excel_io import ensure_excels, write_yag

def _num(x):
    try:
        s = str(x).replace(" TL","").replace("₺","")
        if s.count(",")==1 and s.count(".")>1:
            s = s.replace(".","").replace(",",".")
        elif s.count(",")==1 and s.count(".")==0:
            s = s.replace(",",".")
        else:
            s = s.replace(",",".")
        return float(s)
    except: return None

def main(path):
    df = pd.read_excel(path)
    df.columns = [str(c).strip() for c in df.columns]
    mcol = next((c for c in df.columns if c.lower().startswith("marka")), "Marka")
    ucol = next((c for c in df.columns if "urun" in c.lower()), "Urun")
    vcol = next((c for c in df.columns if "visko" in c.lower()), "Viskozite")
    lcol = next((c for c in df.columns if "litre" in c.lower()), "Litre")
    bcol = next((c for c in df.columns if "birim" in c.lower()), "Birim Fiyat (TL)")
    scol = next((c for c in df.columns if "satış" in c.lower() or "satis" in c.lower()), "Satış Fiyat (TL)")

    conn = connect(); ensure_schema(conn); repo = YagRepository(conn)
    for _, r in df.iterrows():
        row = {
            "marka": ("" if pd.isna(r.get(mcol)) else str(r.get(mcol))).strip(),
            "urun":  ("" if pd.isna(r.get(ucol)) else str(r.get(ucol))).strip(),
            "viskozite": ("" if pd.isna(r.get(vcol)) else str(r.get(vcol))).strip(),
            "litre": _num(r.get(lcol)),
            "birim_fiyat": _num(r.get(bcol)),
            "satis_fiyat": _num(r.get(scol)),
        }
        if row["urun"]:
            repo.upsert(row)
    ensure_excels(); write_yag(conn); conn.close()
    print("✓ Yağ Excel import tamamlandı.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True)
    args = ap.parse_args()
    main(args.excel)
