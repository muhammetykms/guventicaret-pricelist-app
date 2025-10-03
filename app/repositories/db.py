# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path
from ..config import DB_PATH

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def ensure_schema(conn):
    cur = conn.cursor()

    # ---- Ana ürün tablosu (Filtre, Yağ'ın sade alanları, Antifriz, Katkı vs.) ----
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT,
        code TEXT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        cost_price REAL,        -- KDVsiz
        cost_price_vat REAL,    -- KDVli
        sale_price REAL,
        stock INTEGER DEFAULT 0,
        image_path TEXT,
        kdv_rate REAL DEFAULT 0.20,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # ---- Akü (Excel’deki gibi STRING tutuyoruz) ----
    cur.execute("""
    CREATE TABLE IF NOT EXISTS aku_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,                 -- ÜRÜN
        list_no_vat TEXT,                   -- KDV HARİÇ LİSTE FİYATI
        disc5 TEXT,                         -- 5% (2 ay vade)
        disc8 TEXT,                         -- 8% (nakit)
        scrap TEXT,                         -- HURDA
        hrd TEXT,                           -- HRD DÜŞÜLMÜŞ
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # ---- Yağ (Marka/Urun/Viskozite/Litre + fiyatlar) ----
    cur.execute("""
    CREATE TABLE IF NOT EXISTS yag_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marka TEXT,
        urun TEXT,
        viskozite TEXT,
        litre REAL,
        birim_fiyat REAL,       -- TL (net rakam)
        satis_fiyat REAL,       -- TL (net rakam)
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # ---- Filtre (Excel dosyasıyla bire bir alan isimli ayrı tablo isterseniz) ----
    cur.execute("""
    CREATE TABLE IF NOT EXISTS filtre_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mal_kodu TEXT,
        mal_adi TEXT,
        birim_fiyat REAL,       -- KDV'li birim tutar
        satis_fiyati REAL,      -- %20 kâr + 50’liklere yukarı yuvarlanmış
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # ---- Hızlı arama indeksleri ----
    cur.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_aku_name ON aku_items(name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_yag_urun ON yag_items(urun);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_filtre_adi ON filtre_items(mal_adi);")

    conn.commit()
