# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from ...config import THEME
from ...repositories.filtre import FiltreRepository
from ...services.pricing import parse_tr_money, format_tr_money, calc_sale_from_unit

def money(x):
    try:
        return f"{float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return x if x is not None else ""

class FiltreTab:
    """
    Tablo:
      Mal Kodu | Mal Adı | Birim Fiyat | Satış Fiyat | ID
    Çift tıklama: DETAY
    """
    def __init__(self, container):
        self.repo = FiltreRepository()
        self.container = container
        self._build()

    def _build(self):
        top = tk.Frame(self.container, bg=THEME['BG']); top.pack(fill="x", pady=(8,6), padx=12)

        self.qv = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.qv, width=44, style="Input.TEntry")
        ent.insert(0, "Arama yapınız…")
        ent.bind("<FocusIn>", lambda e: self._clear_ph(ent))
        ent.bind("<FocusOut>", lambda e: self._restore_ph(ent))
        ent.pack(side="left")
        ent.bind("<KeyRelease>", lambda _e: self.refresh())

        ttk.Button(top, text="Ara", style="Green.TButton", command=self.refresh).pack(side="left", padx=6)
        ttk.Button(top, text="Ekle", style="Green.TButton", command=self._add).pack(side="right", padx=6)
        ttk.Button(top, text="Düzenle", style="Red.TButton", command=self._edit).pack(side="right", padx=6)
        ttk.Button(top, text="Sil", style="Red.TButton", command=self._del).pack(side="right", padx=6)

        cols = ("mal_kodu","mal_adi","birim_fiyat","satis_fiyat","id")
        headers = {"mal_kodu":"Mal Kodu","mal_adi":"Mal Adı","birim_fiyat":"Birim Fiyat","satis_fiyat":"Satış Fiyat","id":"ID"}
        widths = [180, 650, 160, 160, 60]

        frame = tk.Frame(self.container, bg=THEME['BG']); frame.pack(fill="both", expand=True, padx=12, pady=(4,12))
        self.tv = ttk.Treeview(frame, columns=cols, show="headings", height=18, style="Treeview")
        self.tv.grid(row=0, column=0, sticky="nsew")
        vs = ttk.Scrollbar(frame, orient="vertical", command=self.tv.yview); self.tv.configure(yscrollcommand=vs.set); vs.grid(row=0, column=1, sticky="ns")
        hs = ttk.Scrollbar(frame, orient="horizontal", command=self.tv.xview); self.tv.configure(xscrollcommand=hs.set); hs.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1); frame.grid_columnconfigure(0, weight=1)

        for i, c in enumerate(cols):
            self.tv.heading(c, text=headers[c]); self.tv.column(c, width=widths[i], anchor="w", stretch=False)

        self.tv.bind("<Double-1>", lambda _e: self._show_detail())
        self.refresh()

    def _clear_ph(self, entry):
        if entry.get() == "Arama yapınız…":
            entry.delete(0, tk.END)
    def _restore_ph(self, entry):
        if not entry.get().strip():
            entry.insert(0, "Arama yapınız…")

    def refresh(self):
        self.tv.delete(*self.tv.get_children())
        q = self.qv.get().strip()
        if q == "Arama yapınız…": q = ""
        for mal_kodu, mal_adi, birim, satis, pid in self.repo.all(q):
            self.tv.insert("", "end", values=(mal_kodu or "", mal_adi or "", money(birim), money(satis), pid))

    def _selected_id(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen bir satır seçin."); return None
        return self.tv.item(sel[0])["values"][-1]

    def _show_detail(self):
        pid = self._selected_id()
        if not pid: return
        p = self.repo.get(pid)
        if not p: return
        _id, mk, ma, bf, sf = p

        win = tk.Toplevel(self.container); win.title("Filtre Detay"); win.configure(bg=THEME["BG"])
        items=[("Mal Kodu",mk),("Mal Adı",ma),("Birim Fiyat",f"{money(bf)} TL"),("Satış Fiyat",f"{money(sf)} TL")]
        for i,(k,v) in enumerate(items):
            tk.Label(win, text=f"{k}:", bg=THEME["BG"], font=("SF Pro Text",12,"bold")).grid(row=i,column=0,sticky="e",padx=10,pady=4)
            tk.Label(win, text=str(v or ""), bg=THEME["BG"], font=("SF Pro Text",12)).grid(row=i,column=1,sticky="w",padx=(0,12),pady=4)
        ttk.Button(win, text="Kapat", style="Red.TButton", command=win.destroy).grid(row=len(items),column=0,columnspan=2,pady=10)

    def _add(self): self._open_form(None)
    def _edit(self):
        pid = self._selected_id()
        if pid: self._open_form(pid)
    def _del(self):
        pid = self._selected_id()
        if not pid: return
        if messagebox.askyesno("Onay", "Seçili ürünü silmek istiyor musunuz?"):
            self.repo.delete(pid); self.refresh()

    # Form (ekle/düzenle) — otomatik satış fiyatı opsiyonu
    def _open_form(self, pid):
        win = tk.Toplevel(self.container); win.title("Filtre " + ("Ekle" if pid is None else "Düzenle")); win.configure(bg=THEME['BG'])
        for c in (0,1): win.grid_columnconfigure(c, weight=1)
        vars = {k: tk.StringVar() for k in ["mal_kodu","mal_adi","birim_fiyat","satis_fiyat"]}

        def row(r, key, label):
            tk.Label(win, text=label+":", bg=THEME['BG'], font=("SF Pro Text",12,"bold")).grid(row=r, column=0, sticky="e", pady=6, padx=(10,10))
            e = ttk.Entry(win, textvariable=vars[key], width=44, style="Input.TEntry"); e.grid(row=r, column=1, sticky="we", padx=(0,10), pady=6)
            return e

        e_code = row(0,"mal_kodu","Mal Kodu")
        e_name = row(1,"mal_adi","Mal Adı")
        e_unit = row(2,"birim_fiyat","Birim Fiyat")
        e_sale = row(3,"satis_fiyat","Satış Fiyat")

        lf = ttk.LabelFrame(win, text="Satış fiyatını otomatik belirle", padding=10)
        lf.grid(row=4, column=0, columnspan=2, sticky="we", padx=10, pady=(4,10))
        lf.grid_columnconfigure(0, weight=1); lf.grid_columnconfigure(1, weight=1)

        auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(lf, text="Birim fiyattan %20 kâr ve 50/100/200'e yuvarla", variable=auto_var).grid(row=0,column=0,sticky="w")
        preview = tk.StringVar(value=""); tk.Label(lf, textvariable=preview, bg=THEME["BG"], fg=THEME.get("GREEN","#0a7a3b")).grid(row=0,column=1,sticky="e")

        def recalc_preview():
            try:
                unit = parse_tr_money(vars["birim_fiyat"].get())
                suggested = calc_sale_from_unit(unit, 0.20)
                preview.set(f"Öneri: {format_tr_money(suggested)} TL")
                if auto_var.get(): vars["satis_fiyat"].set(format_tr_money(suggested))
            except Exception: pass

        auto_var.trace_add("write", lambda *_: recalc_preview())
        e_unit.bind("<KeyRelease>", lambda _e: recalc_preview())
        e_sale.configure(state="disabled"); recalc_preview()

        if pid is not None:
            _id, mk, ma, bf, sf = self.repo.get(pid)
            vars["mal_kodu"].set(mk or "")
            vars["mal_adi"].set(ma or "")
            vars["birim_fiyat"].set("" if bf is None else format_tr_money(bf))
            vars["satis_fiyat"].set("" if sf is None else format_tr_money(sf))
            recalc_preview()

        btns = tk.Frame(win, bg=THEME['BG']); btns.grid(row=5, column=0, columnspan=2, pady=10, sticky="e", padx=10)
        ttk.Button(btns, text="Kaydet", style="Green.TButton",
                   command=lambda: self._save(pid, vars, auto_var.get(), win)).pack(side="left", padx=6)
        ttk.Button(btns, text="İptal", style="Red.TButton", command=win.destroy).pack(side="left", padx=6)

    def _save(self, pid, vars, auto, win):
        try:
            unit = parse_tr_money(vars["birim_fiyat"].get())
            sale = parse_tr_money(vars["satis_fiyat"].get())
            if auto: sale = calc_sale_from_unit(unit, 0.20)
            data = {
                "mal_kodu": vars["mal_kodu"].get().strip() or None,
                "mal_adi": vars["mal_adi"].get().strip(),
                "birim_fiyat": unit,
                "satis_fiyat": sale
            }
        except Exception as e:
            messagebox.showerror("Hata", f"Alanları kontrol edin:\n{e}"); return
        if not data["mal_adi"]:
            messagebox.showerror("Hata", "Mal Adı zorunlu."); return
        if pid is None: self.repo.insert(data)
        else: self.repo.update(pid, data)
        win.destroy(); self.refresh()
