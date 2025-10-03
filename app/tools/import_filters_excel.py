# -*- coding: utf-8 -*-
"""
Filtre Excel importeri (yalnız filtre_items tablosunu etkiler)

Beklenen/karşılanacak başlıklar (esnek):
- "Mal Kodu"  (veya: Kod, Stok Kodu, Ürün Kodu, OEM, PartNo ...)
- "Mal Adı"   (veya: Ürün Adı, Açıklama, Mal Adi ...)
- "Birim Tutar" / "Birim Fiyat (KDVli)" / "Birim Fiyat" (KDV'li birim fiyat)

Satış fiyatı kuralı:
  sale_price = ceil_to_next_50( birim_tutar * 1.20 )

Kayıt politikası (filtre_items):
- mal_kodu     = Mal Kodu (yoksa NULL)
- mal_adi      = Mal Adı (zorunlu)
- birim_fiyat  = Birim Tutar (float, virgül doğru parse edilir)
- satis_fiyat  = %20 kâr + 50’liklere yukarı yuvarlama
"""

import argparse, re
import pandas as pd
from ..repositories.db import connect, ensure_schema

# ---- helpers ----
def _norm(s: str) -> str:
    if s is None: return ""
    s = str(s).strip().lower()
    tr = str.maketrans("ışğçöüâêîôû", "isgcouaeiou")
    s = s.translate(tr)
    s = re.sub(r"\s+", " ", s)
    return s

def _to_float(val):
    if val is None: return 0.0
    s = str(val).strip().upper()
    if s in ("", "-", "—", "N/A", "NA", "NONE"): return 0.0
    s = s.replace(" TL","").replace("₺","")
    s = re.sub(r"[^\d,.\-]", "", s)
    # 1.234.567,89 -> 1234567.89  |  312,55 -> 312.55
    if s.count(",")==1 and s.count(".")>1:
        s = s.replace(".","").replace(",",".")
    elif s.count(",")==1 and s.count(".")==0:
        s = s.replace(",",".")
    else:
        if s.count(".")==1 and s.count(",")==0:
            left,right = s.split(".")
            if re.fullmatch(r"\d{3}", right):  # 6.537 -> 6537
                s = left+right
        elif s.count(".")>1:
            s = s.replace(".","")
        s = s.replace(",",".")
    try:
        return float(s)
    except:
        return 0.0

def _pick(df, keys):
    cols = {c: _norm(c) for c in df.columns}
    for k in keys:
        nk = _norm(k)
        for orig, nc in cols.items():
            if nk in nc:
                return orig
    return None

def ceil_to_next_50(x: float) -> float:
    # 1327 -> 1350 ; 1300 -> 1300 ; 1310 -> 1350; 1251 -> 1300
    # 50’lik dilime YUKARI yuvarlar
    import math
    return float(int(math.ceil(x / 50.0) * 50))

# ---- main ----
def main(excel_path: str, drop_existing: bool=False):
    df = pd.read_excel(excel_path)

    col_code = _pick(df, ["mal kodu","kod","stok kodu","urun kodu","oem","partno"])
    col_name = _pick(df, ["mal adi","urun adi","adi","aciklama","urun"])
    col_unit = _pick(df, ["birim tutar","birim fiyat (kdvli)","kdvli birim","birim fiyat","brfiyat"])

    if not col_name or not col_unit:
        raise SystemExit("Excel başlıkları bulunamadı. En az 'Mal Adı' ve 'Birim Tutar' gerekli.")

    conn = connect(); ensure_schema(conn)
    cur = conn.cursor()

    if drop_existing:
        cur.execute("DELETE FROM filtre_items")
        conn.commit()

    inserted = updated = 0

    for _, row in df.iterrows():
        code = (str(row.get(col_code, "")).strip() if col_code else "")
        name = str(row.get(col_name, "")).strip()
        if not name:
            continue
        unit = _to_float(row.get(col_unit, 0))
        sale = ceil_to_next_50(unit * 1.20)

        ex = cur.execute(
            "SELECT id FROM filtre_items WHERE (mal_kodu IS ? OR mal_kodu=?) AND mal_adi=?",
            (None if not code else None, code if code else None, name)
        ).fetchone()
        if ex:
            cur.execute("""
                UPDATE filtre_items
                   SET mal_kodu=?, mal_adi=?, birim_fiyat=?, satis_fiyat=?, updated_at=datetime('now')
                 WHERE id=?
            """, (code or None, name, unit, sale, ex[0]))
            updated += 1
        else:
            cur.execute("""
                INSERT INTO filtre_items (mal_kodu, mal_adi, birim_fiyat, satis_fiyat, created_at, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (code or None, name, unit, sale))
            inserted += 1

    conn.commit(); conn.close()
    print(f"✓ Filtre import tamam: Eklendi {inserted}, Güncellendi {updated}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True, help="AKSU_filtresi_tam_tek_sayfa.xlsx")
    ap.add_argument("--drop-existing", action="store_true")
    args = ap.parse_args()
    main(args.excel, args.drop_existing)
