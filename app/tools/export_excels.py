# -*- coding: utf-8 -*-
import argparse
from ..repositories.db import connect, ensure_schema
from ..services.excel_io import (
    ensure_excels,
    write_aku,
    write_yag,
    write_filtre,
    write_antifriz,
    write_katki,
)

def main():
    _ = argparse.ArgumentParser().parse_args()
    conn = connect(); ensure_schema(conn)
    ensure_excels()
    write_aku(conn)
    write_yag(conn)
    write_filtre(conn)
    write_antifriz(conn)
    write_katki(conn)
    conn.close()
    print("✓ Tüm kategoriler ayrı Excel dosyalarına yazıldı.")

if __name__ == "__main__":
    main()
