# -*- coding: utf-8 -*-
import math

DEFAULT_KDV = 0.20  # gerekirse başka yerlerde de kullanırsın

def ceil_to_next_50(x: float) -> float:
    """x değerini 50'liklere YUKARI yuvarlar. 1327 -> 1350, 1500->1500."""
    if x is None: 
        return 0.0
    return float(int(math.ceil(x / 50.0) * 50))

def calc_sale_from_unit(unit_price: float, margin: float = 0.20) -> float:
    """
    Birim fiyat (KDV'li) üstüne %margin ekler ve 50'liklere YUKARI yuvarlayıp satış fiyatı verir.
    """
    try:
        base = float(unit_price or 0)
    except Exception:
        base = 0.0
    with_margin = base * (1.0 + margin)
    return ceil_to_next_50(with_margin)

def parse_tr_money(s) -> float:
    """
    '1.234,56' / '1.234,56 TL' / '1234,56' → 1234.56
    Sade  '1234' → 1234.0
    Boş/None → 0.0
    """
    if s is None:
        return 0.0
    t = str(s).strip().upper().replace(" TL", "").replace("₺","")
    # Noktaları (binlik) at, virgülü nokta yap
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except Exception:
        return 0.0

def format_tr_money(x) -> str:
    """1234.5 -> '1.234,50' (TL yazısını UI/Excel tarafında sen eklersin/eklemezsin)"""
    try:
        s = f"{float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return s
    except Exception:
        return str(x)
