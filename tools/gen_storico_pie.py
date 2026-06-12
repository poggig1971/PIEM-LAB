# -*- coding: utf-8 -*-
"""Genera data/storico_pie.json: serie storica del prezzario Piemonte
marzo 2022, luglio 2022 (straordinaria), 2023, 2024, 2025, 2026 — per voce.

Sorgenti attese nella cartella radice del progetto:
- Prezzario_Piemonte_2022_TREND_marzo_luglio.xlsx        (marzo + luglio 2022)
- PrezziarioRegione Piemonte Raffronto 2024_23 Circolare.xlsx  (2023, per codice 2024)
- PrezziarioRegione Piemonte Raffronto 2024_25 Circolare.xlsx  (2024+2025, codici rettificati)
- 01 PIEMONTE 26/tabella-transcodifica-2025-2026.xls     (raccordo 2025->2026)
- dashboard/data/voci_P.json                              (prezzi 2026)

Richiede: pip install python-calamine --break-system-packages
"""
import json, os, re, sys
from python_calamine import CalamineWorkbook

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEAF = re.compile(r"^\d{2}\.[A-Z]\d{2}\.[A-Z]\d{2}\.\d{3}")

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def find(name):
    for root, _, files in os.walk(BASE):
        for f in files:
            if name.lower() in f.lower():
                return os.path.join(root, f)
    sys.exit(f"file non trovato: {name}")

# marzo + luglio 2022
wb = CalamineWorkbook.from_path(find("TREND_marzo_luglio"))
e22m, e22l = {}, {}
for r in wb.get_sheet_by_name("TREND").to_python(skip_empty_area=True)[1:]:
    cod = str(r[1] or "").strip()
    if LEAF.match(cod):
        m, l = num(r[4]), num(r[5])
        if m is not None: e22m[cod] = m
        if l is not None: e22l[cod] = l
print("2022: marzo", len(e22m), "| luglio", len(e22l))

# 2023 (per codice 2024)
wb = CalamineWorkbook.from_path(find("Raffronto 2024_23"))
e23 = {}
for r in wb.get_sheet_by_name("DataBase").to_python(skip_empty_area=True)[4:]:
    cod = str(r[5] or "").strip()
    if LEAF.match(cod):
        v = num(r[10])
        if v is not None: e23[cod] = v
print("2023:", len(e23))

# 2024 + 2025 + codici rettificati
wb = CalamineWorkbook.from_path(find("Raffronto 2024_25"))
rett = {}
for r in wb.get_sheet_by_name("2024").to_python(skip_empty_area=True)[9:]:
    o, rt = str(r[3] or "").strip(), str(r[4] or "").strip()
    if LEAF.match(o) and LEAF.match(rt): rett[o] = rt
serie = {}
for r in wb.get_sheet_by_name("DataBase").to_python(skip_empty_area=True)[5:]:
    cod = str(r[6] or "").strip()
    if not LEAF.match(cod): continue
    e25v, e24v = num(r[9]), num(r[11])
    if e25v is None and e24v is None: continue
    serie[cod] = {"sezn": str(r[2] or "").strip(), "d25": str(r[7] or "").strip()[:120],
                  "um": str(r[8] or "").strip(), "e24": e24v, "e25": e25v}
print("2024/2025:", len(serie), "| rettificati:", len(rett))

# aggancio 2022/2023 (identita' di codice -> rettificato)
def remap(d):
    return {rett.get(k, k): v for k, v in d.items()}
e22m, e22l, e23 = remap(e22m), remap(e22l), remap(e23)
for cod, v in serie.items():
    v["e22m"], v["e22l"], v["e23"] = e22m.get(cod), e22l.get(cod), e23.get(cod)

# transcodifica 2025->2026 (TUTTE le destinazioni, anche PR/AT/RU)
wb = CalamineWorkbook.from_path(find("tabella-transcodifica-2025-2026"))
tr = {}
for r in wb.get_sheet_by_name(wb.sheet_names[0]).to_python(skip_empty_area=True):
    c25 = str(r[0] or "").replace("\x00", "").strip()
    c26 = str(r[2] or "").replace("\x00", "").strip() if len(r) > 2 else ""
    if re.match(r"^\d{2}\.", c25) and re.match(r"^([A-Z]{2}\w*|\d{2})\.", c26):
        tr[c25] = c26
print("transcodifica:", len(tr))

# prezzi 2026
pie = json.load(open(os.path.join(BASE, "dashboard", "data", "voci_P.json"), encoding="utf-8"))["voci"]
p26 = {v[0]: v[3] for v in pie}
voci, sez_names = [], {}
for cod in sorted(serie):
    v = serie[cod]
    c26 = tr.get(cod, cod)
    e26 = p26.get(c26)
    if c26 not in p26: c26 = None
    s = cod[:2]
    if v["sezn"]: sez_names.setdefault(s, v["sezn"][:70])
    # 2 decimali: i prezzi pubblicati sono a 2 decimali; il listino 2026 xlsx
    # ha valori grezzi a 4 decimali che creano false micro-variazioni
    def p(x): return round(x, 2) if x else None
    voci.append([cod, c26, s, v["d25"], v["um"],
                 p(v["e22m"]), p(v["e22l"]), p(v["e23"]), p(v["e24"]), p(v["e25"]), p(e26)])
out = {"anni": ["marzo 2022", "luglio 2022 (straord.)", "2023", "2024", "2025", "2026"],
       "sez": sez_names, "voci": voci}
dest = os.path.join(BASE, "dashboard", "data", "storico_pie.json")
with open(dest, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print("scritto", dest, "| voci:", len(voci), "| %.1f MB" % (os.path.getsize(dest) / 1e6))
