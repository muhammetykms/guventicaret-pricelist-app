# -*- coding: utf-8 -*-
import sys
import tkinter as tk
import tkinter.ttk as ttk
from ..config import THEME

class _TtkButtonProxy:
    """ttk.Button yerine renkli tk.Button kullanan proxy (macOS için)."""
    def __init__(self, master=None, **kwargs):
        text = kwargs.pop("text", "")
        style = (kwargs.pop("style", "") or "").lower()
        cmd   = kwargs.pop("command", None)

        if "green.tbutton" in style:
            theme = dict(bg=THEME["GREEN"], fg="white",
                         activebackground="#096735", activeforeground="white")
        elif "red.tbutton" in style:
            theme = dict(bg=THEME["RED"], fg="white",
                         activebackground="#961c1c", activeforeground="white")
        elif "secondary.tbutton" in style:
            theme = dict(bg="#dde1e6", fg="black",
                         activebackground="#cbd0d6", activeforeground="black")
        else:
            theme = dict(bg="#f0f0f0", fg="black",
                         activebackground="#e6e6e6", activeforeground="black")

        self._w = tk.Button(master, text=text, command=cmd, bd=0, padx=14, pady=6,
                            relief="flat", highlightthickness=0, **theme)

    # delegasyon
    def pack(self, *a, **k): return self._w.pack(*a, **k)
    def grid(self, *a, **k): return self._w.grid(*a, **k)
    def place(self, *a, **k): return self._w.place(*a, **k)
    def configure(self, *a, **k): return self._w.configure(*a, **k)
    config = configure
    def destroy(self): return self._w.destroy()
    def __getattr__(self, n): return getattr(self._w, n)

def force_colored_ttk_buttons():
    """
    macOS'ta ttk.Button -> renkli tk.Button proxy.
    *import sırası çok önemli*: Tabs import edilmeden önce çağrılmalı!
    """
    if sys.platform != "darwin":
        return
    # Modülün kendisindeki Button'ı değiştir.
    ttk.Button = _TtkButtonProxy
    # Ayrıca, bu modüle daha önce import edilmiş referanslar varsa da etkilensin diye:
    import sys as _sys
    mod = _sys.modules.get("tkinter.ttk")
    if mod is not None:
        mod.Button = _TtkButtonProxy
