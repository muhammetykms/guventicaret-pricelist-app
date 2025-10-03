# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path

from ..config import THEME, ASSETS_DIR
from .styles import apply_styles
from ..services import backup

# Sekmeler (Excel tabanlı; conn parametresi YOK)
from .tabs.aku import AkuTab
from .tabs.yag import YagTab
from .tabs.filtre import FiltreTab
from .tabs.antifriz import AntifrizTab
from .tabs.katki import KatkiTab


class AppUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---- Tema / font / macOS ölçekleme ----
        apply_styles(self)

        self.title("Güven Ticaret Otomasyon")
        self.configure(bg=THEME["BG"])

        # ---- HEADER: yeşil şerit + logo + “Şimdi Yedekle” ----
        self._build_header()

        # ---- Kırmızı ayırıcı çizgi ----
        tk.Frame(self, bg=THEME["RED"], height=4).pack(fill="x")

        # ---- NOTEBOOK SARICI ----
        nbwrap = ttk.Frame(self, style="TFrame")
        nbwrap.pack(fill="both", expand=True)

        nb = ttk.Notebook(nbwrap)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        # ================= Sekmeler =================
        # Yağ
        page_yag = tk.Frame(nb, bg=THEME["BG"])
        nb.add(page_yag, text="Yağ")
        self._safe_build_tab(YagTab, page_yag, "Yağ")

        # Akü
        page_aku = tk.Frame(nb, bg=THEME["BG"])
        nb.add(page_aku, text="Akü")
        self._safe_build_tab(AkuTab, page_aku, "Akü")

        # Filtre
        page_filtre = tk.Frame(nb, bg=THEME["BG"])
        nb.add(page_filtre, text="Filtre")
        self._safe_build_tab(FiltreTab, page_filtre, "Filtre")

        # Antifriz
        page_antifriz = tk.Frame(nb, bg=THEME["BG"])
        nb.add(page_antifriz, text="Antifriz")
        self._safe_build_tab(AntifrizTab, page_antifriz, "Antifriz")

        # Katkı Maddesi
        page_katki = tk.Frame(nb, bg=THEME["BG"])
        nb.add(page_katki, text="Katkı")
        self._safe_build_tab(KatkiTab, page_katki, "Katkı")

        # Pencere boyutları
        self.minsize(1100, 720)
        self.geometry("1300x860")

    # ----------------- Parçalar -----------------
    def _build_header(self):
        header = tk.Frame(self, bg=THEME["GREEN"])
        header.pack(fill="x")

        # Logo
        logo_path = Path(ASSETS_DIR) / "logo.png"
        if logo_path.exists():
            try:
                img = Image.open(logo_path)
                target_w = 280
                if img.width:
                    ratio = target_w / float(img.width)
                    img = img.resize((int(img.width * ratio), int(img.height * ratio)))
                self._logo_img = ImageTk.PhotoImage(img)
                tk.Label(header, image=self._logo_img, bg=THEME["GREEN"]).pack(side="left", padx=12, pady=6)
            except Exception:
                tk.Label(header,
                         text="GÜVEN TİCARET",
                         font=("SF Pro Text", 20, "bold"),
                         fg="white", bg=THEME["GREEN"],
                         padx=12, pady=12).pack(side="left")
        else:
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

    def _safe_build_tab(self, TabClass, container, tab_name: str):
        """Sekme sınıflarını güvenli şekilde başlatır; hata olursa sekmede uyarı gösterir."""
        try:
            # Excel tabanlı olduğumuz için conn parametresi yok:
            TabClass(container)
        except Exception as e:
            print(f"[HATA] {tab_name} sekmesi oluşturulamadı:", e)
            err = tk.Label(
                container,
                text=f"{tab_name} sekmesi yüklenemedi:\n{e}",
                bg=THEME["BG"],
                fg="red",
                font=("SF Pro Text", 12, "bold"),
                justify="left"
            )
            err.pack(anchor="w", padx=14, pady=10)
