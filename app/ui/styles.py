# -*- coding: utf-8 -*-
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

# Renkler / ölçek
from ..config import THEME, MAC_SCALING

def _apply_base_theme(root: tk.Tk):
    # HiDPI / Retina
    if platform.system() == "Darwin":
        try:
            root.tk.call("tk", "scaling", MAC_SCALING)  # 1.6–2.0
        except tk.TclError:
            pass

    s = ttk.Style(root)

    # Aqua renkleri yutar; clam'a geç
    try:
        s.theme_use("clam")
    except tk.TclError:
        pass

    # Varsayılan fontları büyüt
    for fname in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        try:
            tkfont.nametofont(fname).configure(size=13, family="SF Pro Text")
        except Exception:
            pass

    # Genel yüzeyler
    s.configure("TFrame", background=THEME["BG"])
    s.configure("TNotebook", background=THEME["BG"])
    s.configure("TNotebook.Tab", padding=(14, 8), font=("SF Pro Text", 12, "bold"))

    # Entry
    s.configure(
        "Input.TEntry",
        padding=8,
        fieldbackground="white",
        bordercolor="#e1e5ea",
        lightcolor="#e1e5ea",
        darkcolor="#e1e5ea",
    )

    # Treeview
    s.configure(
        "Treeview",
        background="white",
        fieldbackground="white",
        foreground="black",
        rowheight=32,
        font=("SF Pro Text", 13),
    )
    s.configure(
        "Treeview.Heading",
        font=("SF Pro Text", 13, "bold"),
        background="#e9ecef",
        foreground="black",
    )

    # ---- Renkli buton stilleri ----
    s.configure(
        "Green.TButton",
        background=THEME["GREEN"],
        foreground="white",
        padding=(18, 10),
        font=("SF Pro Text", 13, "bold"),
        bordercolor=THEME["GREEN"],
        focusthickness=3,
        focuscolor=THEME["GREEN"],
    )
    s.map("Green.TButton",
          background=[("active", "#0f9a4c")],
          foreground=[("disabled", "#dddddd")])

    s.configure(
        "Red.TButton",
        background=THEME["RED"],
        foreground="white",
        padding=(16, 10),
        font=("SF Pro Text", 13, "bold"),
        bordercolor=THEME["RED"],
    )
    s.map("Red.TButton", background=[("active", "#c23a3a")])

    s.configure(
        "Secondary.TButton",
        background="#e8eef4",
        foreground="#1f2937",
        padding=(12, 8),
        font=("SF Pro Text", 12, "bold"),
        bordercolor="#e8eef4",
    )

    return s


def _monkey_patch_button_default_style():
    """
    Projede style verilmeden oluşturulan ttk.Button'lar gri kalıyordu.
    Bu patch, *varsayılan* olarak Secondary.TButton kullanır ve
    buton metnine göre otomatik renk atar:
      - "Ekle", "Ara", "Kaydet", "İçe Aktar" -> Green.TButton
      - "Sil", "Düzenle", "Kapat", "İptal"   -> Red.TButton
    """
    orig_Button = ttk.Button

    def _classify(text: str) -> str:
        t = (text or "").strip().lower()
        if t in ("ekle", "ara", "kaydet", "içe aktar", "pdf yükle → fiyat güncelle", "şimdi yedekle"):
            return "Green.TButton"
        if t in ("sil", "düzenle", "iptal", "kapat"):
            return "Red.TButton"
        return "Secondary.TButton"

    class PatchedButton(orig_Button):  # type: ignore
        def __init__(self, master=None, **kw):
            style = kw.get("style")
            if not style:
                # 'text' üzerinden renk seç; yoksa Secondary
                style = _classify(kw.get("text", ""))
                kw["style"] = style
            super().__init__(master, **kw)

    ttk.Button = PatchedButton  # type: ignore


def apply_styles(root: tk.Tk):
    """
    Bunu ana pencerede *ilk iş* çağır:
        self.configure(bg=THEME['BG'])
        apply_styles(self)
    """
    _apply_base_theme(root)
    _monkey_patch_button_default_style()
