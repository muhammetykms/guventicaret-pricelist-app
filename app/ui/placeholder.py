# -*- coding: utf-8 -*-
import tkinter as tk

def add_placeholder(entry: tk.Entry, var: tk.StringVar, text: str = "Arama yapınız..."):
    """
    ttk.Entry / tk.Entry için basit placeholder.
    - İlk değer olarak placeholder yazar.
    - Odaklanınca temizler, boş bırakılırsa geri yazar.
    Not: Renk değiştirmiyoruz (ttk 'clam' teması fg set etmeyi sınırlayabilir).
    """
    # Eğer zaten bir değer yoksa placeholder yaz
    if not (var.get() or "").strip():
        var.set(text)
        entry._is_placeholder = True
    else:
        entry._is_placeholder = False

    def on_focus_in(_e):
        if getattr(entry, "_is_placeholder", False):
            var.set("")
            entry._is_placeholder = False

    def on_focus_out(_e):
        if not (var.get() or "").strip():
            var.set(text)
            entry._is_placeholder = True

    def on_key(_e):
        entry._is_placeholder = False

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry.bind("<Key>", on_key)
