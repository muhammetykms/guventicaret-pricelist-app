# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from ...services.pricing import parse_tr_money, calc_sale_from_unit, format_tr_money

def attach_auto_sale(form_parent,
                     unit_var: tk.StringVar,
                     sale_var: tk.StringVar,
                     default_auto: bool = True,
                     label_text: str = "Satış fiyatını otomatik hesapla (%20 kâr + 50'ye yuvarla)",
                     on_toggle=None):
    """
    - unit_var: Birim fiyat StringVar (KDV'li)
    - sale_var: Satış fiyatı StringVar
    - default_auto: başlangıçta otomatik mi açılsın?
    - label_text: checkbox metni
    - on_toggle: (opsiyonel) check değiştiğinde çalıştırılacak callback
    DÖNÜŞ:
      - chk_var (BooleanVar)
      - disable/enable state'i senkronize eder, unit_var değiştikçe auto ise sale_var'ı hesaplayıp doldurur.
    """
    chk_var = tk.BooleanVar(value=default_auto)

    # Checkbox
    chk = ttk.Checkbutton(
        form_parent,
        text=label_text,
        variable=chk_var,
        style="TCheckbutton",
        command=lambda: _on_change()
    )
    chk.grid(column=1, sticky="w", padx=(0, 6))

    def _recalc():
        if not chk_var.get():
            return
        unit = parse_tr_money(unit_var.get())
        sale = calc_sale_from_unit(unit, margin=0.20)
        sale_var.set(format_tr_money(sale))

    def _on_change():
        # otomatik ise hemen hesapla ve satış alanını kilitlemek için geri bildirim sağlayalım
        if chk_var.get():
            _recalc()
        if callable(on_toggle):
            on_toggle(chk_var.get())

    # unit değiştikçe hesapla
    def _bind_events(entry_widget):
        entry_widget.bind("<KeyRelease>", lambda _e: _recalc())
        entry_widget.bind("<FocusOut>",  lambda _e: _recalc())

    return chk_var, _bind_events, _recalc
