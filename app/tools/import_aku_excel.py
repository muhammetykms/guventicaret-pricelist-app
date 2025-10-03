# -*- coding: utf-8 -*-
import argparse, pandas as pd
from ..repositories.db import connect, ensure_schema
from ..repositories.aku import AkuRepository
from ..services.excel_io import ensure_excels, write_aku

def main(path):
    df = pd.read_excel(path)
    df.columns = [str(c).strip().upper() for c in df.columns]
    def pick(*names):
        for n in names:
            for c in df.columns:
                if n in c: return c
        return None
    COL_URUN  = pick("ÜRÜN","URUN")
    COL_LST   = pick("KDV HARİÇ","KDV HARIC")
    COL_5     = pick("5%","%5")
    COL_8     = pick("8%","%8")
    COL_HURDA = pick("HURDA")
    COL_HRD   = pick("HRD")
    conn = connect(); ensure_schema(conn); repo = AkuRepository(conn)
    for _, r in df.iterrows():
        name = ("" if pd.isna(r.get(COL_URUN)) else str(r.get(COL_URUN))).strip()
        if not name: continue
        row = {
            "name": name,
            "list_no_vat": "" if pd.isna(r.get(COL_LST)) else str(r.get(COL_LST)),
            "disc5": "" if pd.isna(r.get(COL_5)) else str(r.get(COL_5)),
            "disc8": "" if pd.isna(r.get(COL_8)) else str(r.get(COL_8)),
            "scrap": "" if pd.isna(r.get(COL_HURDA)) else str(r.get(COL_HURDA)),
            "hrd": "" if pd.isna(r.get(COL_HRD)) else str(r.get(COL_HRD)),
        }
        repo.upsert(row)
    ensure_excels(); write_aku(conn); conn.close()
    print("✓ Akü Excel import tamamlandı.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True)
    args = ap.parse_args()
    main(args.excel)
