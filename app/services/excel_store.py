# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Optional, Sequence
import pandas as pd

class ExcelStore:
    """
    Tek sayfalı basit bir Excel tablosu için CRUD.
    - Her tabloda 'ID' kolonu bulunur (int). Yoksa oluşturur.
    - Sayısal para kolonlarını (TL) string olarak yazarız, UI katmanı parse eder.
    """
    def __init__(self, file_path: Path, sheet_name: str, columns: Sequence[str], key_col: str = "ID"):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self.columns = list(columns)
        if "ID" not in self.columns:
            self.columns = self.columns + ["ID"]
        self.key_col = key_col
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file()

    # ---------- internal ----------
    def _ensure_file(self):
        if not self.file_path.exists():
            with pd.ExcelWriter(self.file_path, engine="openpyxl") as w:
                pd.DataFrame(columns=self.columns).to_excel(w, index=False, sheet_name=self.sheet_name)
        else:
            # başlıkları garanti et
            try:
                df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
            except Exception:
                df = pd.DataFrame(columns=self.columns)
            changed = False
            for c in self.columns:
                if c not in df.columns:
                    df[c] = None
                    changed = True
            # Sadece tanımlı kolonları bırak (sıra korunur)
            df = df[[c for c in self.columns if c in df.columns]]
            if changed:
                with pd.ExcelWriter(self.file_path, engine="openpyxl", mode="w") as w:
                    df.to_excel(w, index=False, sheet_name=self.sheet_name)

    def _read(self) -> pd.DataFrame:
        try:
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name, dtype=str)
        except Exception:
            df = pd.DataFrame(columns=self.columns)
        # Sütunları sırala / eksikleri ekle
        for c in self.columns:
            if c not in df.columns:
                df[c] = None
        df = df[self.columns]
        # ID düzelt
        if "ID" in df.columns:
            # string -> int (mümkünse)
            def _to_int(x):
                try:
                    return int(float(str(x)))  # "1.0" gibi şeyler için
                except:
                    return None
            df["ID"] = df["ID"].apply(_to_int)
            if df["ID"].isna().all():
                # Hepsine yeni ID atayalım (1..N)
                df["ID"] = range(1, len(df) + 1)
        return df

    def _write(self, df: pd.DataFrame):
        df = df[self.columns]
        with pd.ExcelWriter(self.file_path, engine="openpyxl", mode="w") as w:
            df.to_excel(w, index=False, sheet_name=self.sheet_name)

    def _next_id(self, df: pd.DataFrame) -> int:
        if "ID" not in df.columns or df.empty or df["ID"].isna().all():
            return 1
        return int(df["ID"].max()) + 1

    # ---------- public ----------
    def list(self, query: str = "", search_cols: Optional[Sequence[str]] = None) -> List[Dict[str, Any]]:
        df = self._read()
        if query:
            q = (query or "").lower().strip()
            search_cols = list(search_cols or [c for c in df.columns if c != "ID"])
            mask = None
            for c in search_cols:
                if c not in df.columns: 
                    continue
                col = df[c].fillna("").astype(str).str.lower()
                m = col.str.contains(q, na=False)
                mask = m if mask is None else (mask | m)
            if mask is not None:
                df = df[mask]
        # NaN -> ""
        df = df.fillna("")
        return df.to_dict(orient="records")

    def get(self, row_id: int) -> Optional[Dict[str, Any]]:
        df = self._read()
        row = df[df["ID"] == int(row_id)]
        if row.empty:
            return None
        return row.iloc[0].fillna("").to_dict()

    def insert(self, data: Dict[str, Any]) -> int:
        df = self._read()
        new_id = self._next_id(df)
        row = {c: data.get(c) for c in self.columns if c != "ID"}
        row["ID"] = new_id
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        self._write(df)
        return new_id

    def update(self, row_id: int, data: Dict[str, Any]) -> None:
        df = self._read()
        idx = df.index[df["ID"] == int(row_id)]
        if len(idx) == 0:
            return
        i = idx[0]
        for c in self.columns:
            if c == "ID":
                continue
            if c in data:
                df.at[i, c] = data[c]
        self._write(df)

    def delete(self, row_id: int) -> None:
        df = self._read()
        df = df[df["ID"] != int(row_id)]
        self._write(df)
