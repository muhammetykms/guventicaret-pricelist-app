# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path

from ..config import THEME, ASSETS_DIR
from ..repositories.db import connect, ensure_schema
from .styles import apply_styles
from ..services import backup

# Sekmeler
from .tabs.aku import AkuTab
from .tabs.yag import YagTab
from .tabs.filtre import FiltreTab
from .tabs.antifriz import AntifrizTab
from .tabs.katki import KatkiTab


class AppUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---- Tema / font / macOS ölçekleme ----
        # Not: apply_styles içinde macOS için clam teması + scaling ayarları bulunuyor.
        apply_styles(self)

        self.title("Güven Ticaret Otomasyon")
        self.configure(bg=THEME["BG"])

        # ---- DB ----
        self.conn = connect()
        ensure_schema(self.conn)

        # ---- HEADER: yeşil şerit + logo + “Şimdi Yedekle” ----
        self._build_header()

        # ---- Kırmızı ayırıcı çizgi ----
        tk.Frame(self, bg=THEME["RED"], height=4).pack(fill="x")

        # ---- NOTEBOOK ----
        nbwrap = ttk.Frame(self, style="TFrame")
        nbwrap.pack(fill="both", expand=True)

        nb = ttk.Notebook(nbwrap)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        # Yağ
        t = ttk.Frame(nb, style="TFrame")
        nb.add(t, text="Yağ")
        YagTab(t, self.conn)

        # Akü
        t = ttk.Frame(nb, style="TFrame")
        nb.add(t, text="Akü")
        AkuTab(t, self.conn)

        # Filtre
        t = ttk.Frame(nb, style="TFrame")
        nb.add(t, text="Filtre")
        FiltreTab(t, self.conn)

        # Antifriz
        t = ttk.Frame(nb, style="TFrame")
        nb.add(t, text="Antifriz")
        AntifrizTab(t, self.conn)

        # Katkı
        t = ttk.Frame(nb, style="TFrame")
        nb.add(t, text="Katkı")
        KatkiTab(t, self.conn)

        self.minsize(1100, 720)
        self.geometry("1300x860")

    # ----------------- Parçalar -----------------
    def _build_header(self):
        header = tk.Frame(self, bg=THEME["GREEN"])
        header.pack(fill="x")

        # Logo yolu (Path ile güvenli)
        logo_path = Path(ASSETS_DIR) / "logo.png"
        if logo_path.exists():
            try:
                img = Image.open(logo_path)
                # Retina’da net dursun diye genişliği ~280 px’e ölçekle
                target_w = 280
                if img.width:
                    ratio = target_w / float(img.width)
                    img = img.resize((int(img.width * ratio), int(img.height * ratio)))
                self._logo_img = ImageTk.PhotoImage(img)
                tk.Label(header, image=self._logo_img, bg=THEME["GREEN"]).pack(side="left", padx=12, pady=6)
            except Exception:
                # görüntü okunamazsa yazıyla fallback
                tk.Label(header,
                         text="GÜVEN TİCARET",
                         font=("SF Pro Text", 20, "bold"),
                         fg="white", bg=THEME["GREEN"],
                         padx=12, pady=12).pack(side="left")
        else:
            # dosya yoksa yazıyla fallback
            tk.Label(header,
                     text="GÜVEN TİCARET",
                     font=("SF Pro Text", 20, "bold"),
                     fg="white", bg=THEME["GREEN"],
                     padx=12, pady=12).pack(side="left")

        # Sağda “Şimdi Yedekle”
        right = tk.Frame(header, bg=THEME["GREEN"])
        right.pack(side="right", padx=12)
        ttk.Button(
            right,
            text="Şimdi Yedekle",
            style="Secondary.TButton",
            command=lambda: (backup.backup_now(), messagebox.showinfo("Tamam", "Yedek alındı."))
        ).pack(pady=20)
