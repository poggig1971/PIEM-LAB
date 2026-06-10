# -*- coding: utf-8 -*-
"""Estrae le voci del Prezzario Lombardia 2026 in JSON per la dashboard. v2"""
import json, os, pickle, re
from python_calamine import CalamineWorkbook

SRC = "/sessions/lucid-blissful-bell/mnt/LOMBARDIA Prezzario Regionale dei lavori pubblici - edizione 2026"
OUT = os.path.join(SRC, "dashboard", "data")
os.makedirs(OUT, exist_ok=True)

PFX = "LOM261."

def strip(c):
    c = str(c or "").strip()
    return c[len(PFX):] if c.startswith(PFX) else c

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def clean(s):
    s = str(s or "").strip()
    return "" if s in ("nd", "ND", "n.d.") else s

SPLIT_RE = re.compile(r"\nLAVORO:|\nSERVIZIO:|\s*SPECIFICHE TECNICHE|\nOP\d")

def split_decl(decl):
    m = SPLIT_RE.search(decl)
    if not m:
        return decl, ""
    short = decl[: m.start()].strip()
    rest = decl[m.start():].strip()
    rest = re.sub(r"\nOP\d.*$", "", "\n" + rest, flags=re.S).strip()
    return short, rest

def load_rows(path, sheet="Ricerca"):
    wb = CalamineWorkbook.from_path(os.path.join(SRC, path))
    sh = sheet if sheet else wb.sheet_names[0]
    return wb.get_sheet_by_name(sh).to_python(skip_empty_area=True)

def load_fact(path, suffix):
    d = {}
    for r in load_rows(path)[1:]:
        c = strip(r[0])
        if c.endswith(suffix):
            p = num(r[3])
            if p:
                d[c[: -len(suffix)]] = round(p, 2)
    return d

print("Carico fattori di variabilita...")
elev = load_fact("Fattori di variabilita_2026_LOM261_XLS/Elenco Voci Elevata complessità.xlsx", "_Cb")
mode = load_fact("Fattori di variabilita_2026_LOM261_XLS/Elenco Voci Modesta complessità.xlsx", "_Ca")
sic = load_fact("Fattori di variabilita_2026_LOM261_XLS/Elenco Voci Sicurezza.xlsx", "_S")
print(f"  elevata {len(elev)} | modesta {len(mode)} | sicurezza {len(sic)}")

FILES = {
    "A": "Prezzario_2026_LOM261_XLS/A) Parte 1 - Elenco prezzi - Civile, Urbanizzazione, Difesa Suolo, Agroforestale.xlsx",
    "C": "Prezzario_2026_LOM261_XLS/C) Parte 2 - Elenco prezzi – Impianti Meccanici, Elettrici, Elettrotecnici, Idraulici e Antincendio.xlsx",
    "E": "Prezzario_2026_LOM261_XLS/E) Parte 3 - Elenco prezzi - Risorse Elementari (umane, materiali, strumentali e produttive-tecnologiche).xlsx",
}

details = {}
meta = {"edizione": "2026 (LOM261)", "parti": {}}

for part, path in FILES.items():
    print("Estraggo parte", part, "...")
    rows = load_rows(path)
    paths, path_idx = [], {}
    voci = []
    for r in rows[1:]:
        cod = strip(r[0])
        if not cod:
            continue
        decl_full = clean(r[1])
        decl, decl_rest = split_decl(decl_full)
        um = clean(r[2])
        prezzo = num(r[3])
        imp = num(r[4])
        ru = num(r[5])
        cod23 = clean(r[20]) if r[20] not in (None, "000000000") else ""
        lvls = [clean(r[i]) for i in range(9, 20)]
        lvls = [l for l in lvls if l]
        key = "|".join(lvls)
        if key not in path_idx:
            path_idx[key] = len(paths)
            paths.append(key)
        voci.append([
            cod, decl, um,
            prezzo if prezzo else 0,
            ru if ru else 0,
            cod23,
            path_idx[key],
            elev.get(cod), mode.get(cod), sic.get(cod),
            clean(r[66]),
        ])
        details[cod] = {
            "declx": decl_rest,
            "imp": imp,
            "d23": clean(r[21]),
            "tip": clean(r[23]),
            "spec": clean(r[45]),
            "crit": clean(r[36]),
            "inc": clean(r[67]),
            "esc": clean(r[68]),
            "norma": clean(r[22]),
            "leggi": clean(r[49]),
            "cam": clean(r[51]),
            "soa": clean(r[64]),
            "sett": clean(r[65]),
            "kw": clean(r[66]),
            "part": part,
        }
    with open(os.path.join(OUT, f"voci_{part}.json"), "w", encoding="utf-8") as f:
        json.dump({"paths": paths, "voci": voci}, f, ensure_ascii=False, separators=(",", ":"))
    meta["parti"][part] = len(voci)
    print(f"  {len(voci)} voci, {len(paths)} percorsi")

print("Estraggo parte F...")
rows = load_rows("Prezzario_2026_LOM261_XLS/F) Parte 4 - Elenco prezzi - Precedente struttura.xlsx", None)
fv = []
for r in rows[1:]:
    cod = strip(r[0])
    if not cod:
        continue
    prezzo = num(r[3])
    ru = num(r[5])
    fv.append([cod, clean(r[1]), clean(r[2]),
               round(prezzo, 2) if prezzo else 0,
               round(ru * 100, 2) if ru else 0])
with open(os.path.join(OUT, "voci_F.json"), "w", encoding="utf-8") as f:
    json.dump({"voci": fv}, f, ensure_ascii=False, separators=(",", ":"))
meta["parti"]["F"] = len(fv)
print(f"  {len(fv)} righe")

with open(os.path.join(OUT, "meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False)
with open("/tmp/details.pkl", "wb") as f:
    pickle.dump(details, f)
print("DONE voci.", len(details))