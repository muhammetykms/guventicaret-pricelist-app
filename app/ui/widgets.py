# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from ..config import THEME

def make_button(master, text, kind="green", command=None):
    """
    kind: "green" | "red" | "secondary" | "plain"
    ttk renk uygulamazsa otomatik tk.Button'a düşer.
    """
    style_name = {
        "green": "Green.TButton",
        "red": "Red.TButton",
        "secondary": "Secondary.TButton",
        "plain": "TButton",
    }[kind]

    try:
        # Önce ttk ile dene
        btn = ttk.Button(master, text=text, command=command, style=style_name)
        # ttk tema arkaplanı basmıyorsa görünüm çok soluk kalır; macOS'ta sık olur.
        # Böyle bir durumda tk.Button kullan.
        if kind in ("green", "red", "secondary"):
            # küçük bir hile: ttk butonun bg özelliği yok; garantili görünüm için tk.Button
            raise RuntimeError("force_tk_button_on_macos")
        return btn
    except Exception:
        # Tk klasik buton -> renkler garantili çalışır
        colors = {
            "green": dict(bg=THEME["GREEN"], fg="white", activebackground="#096735", activeforeground="white"),
            "red": dict(bg=THEME["RED"], fg="white", activebackground="#961c1c", activeforeground="white"),
            "secondary": dict(bg="#dde1e6", fg="black", activebackground="#cbd0d6", activeforeground="black"),
            "plain": dict(bg="#f0f0f0", fg="black", activebackground="#e6e6e6", activeforeground="black"),
        }[kind]
        btn = tk.Button(master, text=text, command=command, bd=0, padx=14, pady=6, **colors)
        return btn
