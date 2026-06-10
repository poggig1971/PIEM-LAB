# -*- coding: utf-8 -*-
"""Estrae le analisi prezzi (file B e D) e genera gli shard di dettaglio."""
import json, os, pickle, re, sys
from python_calamine import CalamineWorkbook

SRC = "/sessions/lucid-blissful-bell/mnt/LOMBARDIA Prezzario Regionale dei lavori pubblici - edizione 2026"
OUT = os.path.join(SRC, "dashboard", "data")
PFX = "LOM261."

def strip(c):
    c = str(c or "").strip()
    return c[len(PFX):] if c.startswith(PFX) else c

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

SPLIT_RE = re.compile(r"\s*SPECIFICHE TECNICHE")

def short(s):
    s = str(s or "").strip()
    m = SPLIT_RE.search(s)
    return s[: m.start()].strip() if m else s

def parse_sheet(rows, analisi):
    cur = None
    cat = ""
    for r in rows:
        c0, c1 = str(r[0] or "").strip(), str(r[1] or "").strip()
        c2 = str(r[2] or "").strip()
        if c0.startswith(PFX):
            cur = strip(c0)
            cat = ""
            analisi[cur] = {"ris": [], "som": None, "sg": None, "ui": None, "tot": num(r[6])}
            continue
        if cur is None:
            continue
        if c1.startswith(PFX):
            analisi[cur]["ris"].append([
                cat, strip(c1), short(r[2]), str(r[3] or "").strip(),
                num(r[4]), num(r[5]), num(r[6]),
            ])
            continue
        if c1 and not c2 and c1 == c1.upper() and "RISORSA" in c1.upper():
            cat = c1.title().replace("Risorsa ", "")
            continue
        if c2.startswith("Sommano"):
            analisi[cur]["som"] = num(r[6])
        elif c2.startswith("Spese generali"):
            analisi[cur]["sg"] = num(r[6])
        elif c2.startswith("Utili"):
            analisi[cur]["ui"] = num(r[6])
        elif c2.startswith("PREZZO TOTALE"):
            analisi[cur]["tot"] = num(r[6])

def parse_file(path):
    analisi = {}
    wb = CalamineWorkbook.from_path(os.path.join(SRC, path))
    for sh in wb.sheet_names:
        rows = wb.get_sheet_by_name(sh).to_python(skip_empty_area=True)
        parse_sheet(rows, analisi)
        print(f"  {sh}: cumulato {len(analisi)} analisi")
    return analisi

def djb2(s, n):
    h = 5381
    for ch in s:
        h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    return h % n

SHARDS = {"A": 24, "C": 48, "E": 48}

if __name__ == "__main__":
    step = sys.argv[1]
    if step == "B":
        a = parse_file("Prezzario_2026_LOM261_XLS/B) Allegato Parte 1 - Analisi prezzi - Civile, Urbanizzazione, Difesa Suolo, Agroforestale.xlsx")
        pickle.dump(a, open("/tmp/analisi_B.pkl", "wb"))
        print("DONE B:", len(a))
    elif step == "D":
        a = parse_file("Prezzario_2026_LOM261_XLS/D) Allegato parte 2 – Analisi prezzi - Impianti Meccanici, Elettrici, Elettrotecnici, Idraulici e Antince.xlsx")
        pickle.dump(a, open("/tmp/analisi_D.pkl", "wb"))
        print("DONE D:", len(a))
    elif step == "MERGE":
        details = pickle.load(open("/tmp/details.pkl", "rb"))
        analisi = pickle.load(open("/tmp/analisi_B.pkl", "rb"))
        analisi.update(pickle.load(open("/tmp/analisi_D.pkl", "rb")))
        print("details", len(details), "analisi", len(analisi))
        os.makedirs(os.path.join(OUT, "det"), exist_ok=True)
        shards = {}
        matched = 0
        for cod, det in details.items():
            part = det.pop("part")
            an = analisi.get(cod)
            if an:
                det["an"] = an
                matched += 1
            det = {k: v for k, v in det.items() if v not in ("", None)}
            key = f"{part.lower()}{djb2(cod, SHARDS[part]):02d}"
            shards.setdefault(key, {})[cod] = det
        for key, data in shards.items():
            with open(os.path.join(OUT, "det", key + ".json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        print(f"shard scritti: {len(shards)}, voci con analisi: {matched}")
