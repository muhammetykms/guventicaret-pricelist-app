# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from ...config import THEME
from ...repositories.aku import AkuRepository
from ...services.pricing import parse_tr_money, format_tr_money, calc_sale_from_unit
from ..placeholder import add_placeholder


def money(x):
    try:
        return f"{float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return x if x is not None else ""

class AkuTab:
    """
    Kolonlar (UI & Excel):
    ÜRÜN | KDV HARİÇ LİSTE FİYATI | 5% (2 ay vade) | 8% (nakit) | HURDA | HRD DÜŞÜLMÜŞ
    Not: Satış mantığında esas alınan "%8 (nakit)" kolonu.
    """
    def __init__(self, container):
        self.repo = AkuRepository()
        self.container = container
        self._build()

    def _build(self):
        top = tk.Frame(self.container, bg=THEME['BG']); top.pack(fill="x", pady=(8,6), padx=12)
        self.qv = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.qv, width=44, style="Input.TEntry"); ent.pack(side="left")
        ent.bind("<KeyRelease>", lambda _e: self.refresh())
        ttk.Button(top, text="Ara", style="Green.TButton", command=self.refresh).pack(side="left", padx=6)
        ttk.Button(top, text="Ekle", style="Green.TButton", command=self._add).pack(side="right", padx=6)
        ttk.Button(top, text="Düzenle", style="Red.TButton", command=self._edit).pack(side="right", padx=6)
        ttk.Button(top, text="Sil", style="Red.TButton", command=self._del).pack(side="right", padx=6)

        cols = ("urun","list_no_vat","disc5","disc8","scrap","hrd","id")
        headers = {"urun":"ÜRÜN","list_no_vat":"KDV HARİÇ LİSTE FİYATI","disc5":"5% (2 ay vade)",
                   "disc8":"8% (nakit)","scrap":"HURDA","hrd":"HRD DÜŞÜLMÜŞ","id":"ID"}
        widths = [360, 180, 150, 150, 120, 150, 60]

        frame = tk.Frame(self.container, bg=THEME['BG']); frame.pack(fill="both", expand=True, padx=12, pady=(4,12))
        self.tv = ttk.Treeview(frame, columns=cols, show="headings", height=18, style="Treeview")
        self.tv.grid(row=0, column=0, sticky="nsew")
        vs = ttk.Scrollbar(frame, orient="vertical", command=self.tv.yview); self.tv.configure(yscrollcommand=vs.set); vs.grid(row=0, column=1, sticky="ns")
        hs = ttk.Scrollbar(frame, orient="horizontal", command=self.tv.xview); self.tv.configure(xscrollcommand=hs.set); hs.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1); frame.grid_columnconfigure(0, weight=1)
        for i, c in enumerate(cols):
            self.tv.heading(c, text=headers[c]); self.tv.column(c, width=widths[i], anchor="w")

        self.tv.bind("<Double-1>", self._on_dblclick)
        self.refresh()

    def _on_dblclick(self, _e=None):
        pid = self._selected_id()
        if not pid: return
        p = self.repo.get(pid)
        if not p: return
        _id, name, ln, d5, d8, sc, hrd = p[:7] if len(p)>=7 else (p+(None,)* (7-len(p)))
        win = tk.Toplevel(self.container); win.title("Akü Detay"); win.configure(bg=THEME["BG"])
        items=[("ÜRÜN",name),("KDV HARİÇ LİSTE",ln),("5% (2 ay vade)",d5),("8% (nakit)",d8),("Hurda",sc),("HRD Düşülmüş",hrd)]
        for i,(k,v) in enumerate(items):
            tk.Label(win, text=f"{k}:", bg=THEME["BG"], font=("SF Pro Text",12,"bold")).grid(row=i,column=0,sticky="e",padx=10,pady=4)
            tk.Label(win, text=str(v or ""), bg=THEME["BG"], font=("SF Pro Text",12)).grid(row=i,column=1,sticky="w",padx=(0,12),pady=4)
        ttk.Button(win, text="Kapat", style="Red.TButton", command=win.destroy).grid(row=len(items),column=0,columnspan=2,pady=10)

    def refresh(self):
        self.tv.delete(*self.tv.get_children())
        for row in self.repo.all(self.qv.get()):
            pid, name, ln, d5, d8, sc, hrd = row[:7] if len(row)>=7 else (list(row)+[None]*(7-len(row)))
            self.tv.insert("", "end", values=(name or "", ln or "", d5 or "", d8 or "", sc or "", hrd or "", pid))

    def _selected_id(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen bir satır seçin.")
            return None
        return self.tv.item(sel[0])["values"][-1]

    def _add(self): self._open_form(None)
    def _edit(self):
        pid = self._selected_id()
        if pid: self._open_form(pid)
    def _del(self):
        pid = self._selected_id()
        if not pid: return
        if messagebox.askyesno("Onay", "Seçili ürünü silmek istiyor musunuz?"):
            self.repo.delete(pid); self.refresh()

    def _open_form(self, pid):
        win = tk.Toplevel(self.container); win.title("Akü " + ("Ekle" if pid is None else "Düzenle")); win.configure(bg=THEME['BG'])
        for c in (0,1): win.grid_columnconfigure(c, weight=1)

        vars = {k: tk.StringVar() for k in ["urun","list_no_vat","disc5","disc8","scrap","hrd"]}
        def row(r, key, label):
            tk.Label(win, text=label+":", bg=THEME['BG'], font=("SF Pro Text",12,"bold")).grid(row=r,column=0,sticky="e",pady=6,padx=(10,10))
            e = ttk.Entry(win, textvariable=vars[key], width=44, style="Input.TEntry"); e.grid(row=r,column=1,sticky="we",padx=(0,10),pady=6)
            return e

        e_name = row(0,"urun","ÜRÜN")
        e_ln   = row(1,"list_no_vat","KDV HARİÇ LİSTE FİYATI")
        row(2,"disc5","5% (2 ay vade)")
        e_d8   = row(3,"disc8","8% (nakit)")
        row(4,"scrap","HURDA"); row(5,"hrd","HRD Düşülmüş")

        lf = ttk.LabelFrame(win, text="Satış fiyatını otomatik belirle", padding=10)
        lf.grid(row=6, column=0, columnspan=2, sticky="we", padx=10, pady=(4,10))
        lf.grid_columnconfigure(0, weight=1); lf.grid_columnconfigure(1, weight=1)

        auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(lf, text="KDV hariç listeden %20 kâr (KDV kabul etmiyoruz) ve 50/100/200'e yuvarla", variable=auto_var).grid(row=0,column=0,sticky="w")
        preview = tk.StringVar(value=""); tk.Label(lf, textvariable=preview, bg=THEME["BG"], fg=THEME.get("GREEN","#0a7a3b")).grid(row=0,column=1,sticky="e")

        def recalc_preview():
            try:
                # Akü’de satış olarak %8 (nakit) kolonunu kullanıyoruz; otomatikte LN no-vat üzerinden hesaplarız.
                base = parse_tr_money(vars["list_no_vat"].get())
                suggested = calc_sale_from_unit(base, 0.20)
                preview.set(f"Öneri (8% nakit): {format_tr_money(suggested)} TL")
                if auto_var.get(): vars["disc8"].set(format_tr_money(suggested))
            except Exception: pass

        auto_var.trace_add("write", lambda *_: recalc_preview())
        e_ln.bind("<KeyRelease>", lambda _e: recalc_preview())
        recalc_preview()

        if pid is not None:
            p = self.repo.get(pid)
            if p:
                _id, name, ln, d5, d8, sc, hrd = p[:7] if len(p)>=7 else (p+(None,)* (7-len(p)))
                vars["urun"].set(name or ""); vars["list_no_vat"].set("" if ln is None else str(ln))
                vars["disc5"].set(d5 or ""); vars["disc8"].set(d8 or "")
                vars["scrap"].set(sc or ""); vars["hrd"].set(hrd or "")
                recalc_preview()

        btns = tk.Frame(win, bg=THEME['BG']); btns.grid(row=7, column=0, columnspan=2, pady=10, sticky="e", padx=10)
        ttk.Button(btns, text="Kaydet", style="Green.TButton",
                   command=lambda: self._save(pid, vars, auto_var.get(), win)).pack(side="left", padx=6)
        ttk.Button(btns, text="İptal", style="Red.TButton", command=win.destroy).pack(side="left", padx=6)

    def _save(self, pid, vars, auto, win):
        try:
            ln  = parse_tr_money(vars["list_no_vat"].get())
            d8v = parse_tr_money(vars["disc8"].get())
            if auto:
                d8v = calc_sale_from_unit(ln, 0.20)
            data = {"urun": vars["urun"].get().strip(),
                    "list_no_vat": ln,
                    "disc5": vars["disc5"].get().strip() or None,
                    "disc8": d8v,
                    "scrap": vars["scrap"].get().strip() or None,
                    "hrd": vars["hrd"].get().strip() or None}
        except Exception as e:
            messagebox.showerror("Hata", f"Alanları kontrol edin:\n{e}"); return
        if not data["urun"]:
            messagebox.showerror("Hata", "ÜRÜN adı zorunlu."); return
        if pid is None: self.repo.insert(data)
        else: self.repo.update(pid, data)
        win.destroy(); self.refresh()
