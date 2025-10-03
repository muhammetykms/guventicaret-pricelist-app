# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import List, Optional, Callable

# Not: openpyxl gerekir:  pip install pandas openpyxl

def _norm(s: str) -> str:
    s = (s or "").lower()
    for ch in [" ", "-", "_", "."]:
        s = s.replace(ch, "")
    return s

class ExcelTable:
    """
    Tek sheet'li, düz başlıklı Excel tablo yönetimi.
    - Tablo başlıkları değişmez.
    - _rid sadece bellek içinde (Excel'e yazılmaz), satır takibi için.
    """
    def __init__(self,
                 path: Path,
                 sheet_name: str,
                 columns: List[str],
                 onload_tweak: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
                 onsave_tweak: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None):
        self.path = Path(path)
        self.sheet_name = sheet_name
        self.columns = columns
        self.onload_tweak = onload_tweak
        self.onsave_tweak = onsave_tweak

        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            # boş dosya üret
            with pd.ExcelWriter(self.path, engine="openpyxl") as w:
                pd.DataFrame(columns=self.columns).to_excel(w, index=False, sheet_name=self.sheet_name)

    def load(self) -> pd.DataFrame:
        try:
            df = pd.read_excel(self.path, sheet_name=self.sheet_name, dtype=object)
        except Exception:
            # sheet yoksa oluştur
            with pd.ExcelWriter(self.path, engine="openpyxl", mode="a", if_sheet_exists="new") as w:
                pd.DataFrame(columns=self.columns).to_excel(w, index=False, sheet_name=self.sheet_name)
            df = pd.read_excel(self.path, sheet_name=self.sheet_name, dtype=object)

        # sadece beklenen kolonları tut, eksik varsa doldur
        for c in self.columns:
            if c not in df.columns:
                df[c] = None
        df = df[self.columns].copy()

        # _rid ver
        df = df.reset_index(drop=True)
        df["_rid"] = df.index.astype(int)

        if self.onload_tweak:
            df = self.onload_tweak(df)

        return df

    def save(self, df: pd.DataFrame):
        # _rid'i at
        if "_rid" in df.columns:
            df = df.drop(columns=["_rid"])
        # sadece beklenen kolonları yaz
        df_out = df[self.columns].copy()

        if self.onsave_tweak:
            df_out = self.onsave_tweak(df_out)

        tmp = self.path.with_suffix(".tmp.xlsx")
        with pd.ExcelWriter(tmp, engine="openpyxl") as w:
            df_out.to_excel(w, index=False, sheet_name=self.sheet_name)
        tmp.replace(self.path)

    # CRUD (rid bazlı)
    def insert_row(self, row: dict) -> int:
        df = self.load()
        new = {c: row.get(c) for c in self.columns}
        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        df["_rid"] = range(len(df))
        self.save(df)
        return int(df.iloc[-1]["_rid"])

    def update_row(self, rid: int, row: dict):
        df = self.load()
        idx = df.index[df["_rid"] == rid]
        if len(idx) == 0:
            return
        i = idx[0]
        for c in self.columns:
            if c in row:
                df.at[i, c] = row[c]
        self.save(df)

    def delete_row(self, rid: int):
        df = self.load()
        df = df[df["_rid"] != rid].reset_index(drop=True)
        df["_rid"] = range(len(df))
        self.save(df)

    def search(self, query: str, in_cols: List[str]) -> pd.DataFrame:
        df = self.load()
        q = _norm(query or "")
        if not q:
            return df
        mask = False
        for c in in_cols:
            colvals = df[c].astype(str).map(_norm)
            mask = (mask | colvals.str.contains(q, na=False))
        return df[mask]
