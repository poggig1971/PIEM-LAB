# Genera l'indice ISTAT REALE per singolo componente del paniere TOL e lo
# inserisce in data/tol_sim.json (campi: is = indice 2026, iss = serie 6 edizioni,
# isn = nota proxy/fonte). Base marzo 2022 = 100, finestre quadrimestrali (come reg/gasolio).
import re,json,collections,os
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISTAT=os.path.join(HERE,"..","istat dati")
qre=re.compile(r"'(?:\"'|[^'])*'")
def load(fn,cond,keyf):
    d=collections.defaultdict(dict)
    with open(fn,encoding='utf-8') as f:
        f.readline()
        for line in f:
            c=qre.sub("Q",line.rstrip("\n")).split(",")
            if cond(c):
                try: d[keyf(c)][c[12]]=float(c[13])
                except: pass
    return d
ppi=load(os.path.join(ISTAT,"Prezzi alla produzione dell'industria - mensili (base 2021) (IT1,145_360_DF_DCSC_PREZZPIND_1_4,1.0).csv"),
         lambda c:c[4]=='IND_PRIC_2021' and c[6]=='N' and c[8]=='D', lambda c:c[10])
retr=load(os.path.join(ISTAT,"Retribuzioni contrattuali (base 2021) (IT1,155_318_DF_DCSC_RETRCONTR1C_4,1.0).csv"),
          lambda c:c[0]=='M' and c[4]=='WAGE_H_2021' and c[9]=='Operaio', lambda c:c[11])
G=json.load(open("RAFFRONTO/gasolio_mase.json",encoding='utf-8'))
wins=G['finestre']; EDS=list(wins.keys())
gasser=[G['indice_base_mar2022'][k] for k in G['indice_base_mar2022']]
def rebase(series):
    if not series: return None
    base=[series[m] for m in wins[EDS[0]] if m in series]
    if not base: return None
    b=sum(base)/len(base); out=[]
    for e in EDS:
        vv=[series[m] for m in wins[e] if m in series]
        if not vv: return None
        out.append(round(sum(vv)/len(vv)/b*100,1))
    return out
def contract_for(ind):
    if 'metalmeccanico' in ind: return 'Settore metalmeccanico'
    if 'marittimi' in ind: return 'Trasporti marittimi'
    if 'Edilizia' in ind: return 'Edilizia'
    return None
PROXY={'Siderweb':('241','proxy: PPI ISTAT Siderurgia (ATECO 241)'),
       'UNRAE':('291','proxy: PPI ISTAT Autoveicoli (ATECO 291)'),
       'GME':('351','proxy: PPI ISTAT Energia elettrica (ATECO 351)')}
def comp_istat(c):
    f=c['fonte']; ind=c.get('indicatore','')
    if f=='Istat' and c.get('ateco'):
        if c['ateco'] in ppi: return rebase(ppi[c['ateco']]),''
        return None,'n.d. (ATECO 494 servizi PPS, non in questo dataset)'
    if f=='Istat' and 'RC per tipo' in ind:
        k=contract_for(ind); return (rebase(retr[k]),'') if k else (None,'')
    if f=='MASE': return gasser,'fonte MIMIT gasolio (benchmark energia)'
    if f in PROXY:
        a,note=PROXY[f]; return rebase(ppi[a]),note
    return None,'n.d. (fonte non-ISTAT: nessun indice nazionale)'
pan=json.load(open("RAFFRONTO/paniere_tol_rich.json",encoding='utf-8'))
# lookup (tol, nome, round(peso,4)) -> serie,nota
look={}
for c in pan['componenti']:
    s,note=comp_istat(c)
    look[(c['tol'],c['componente'],round(c['peso'],4))]=(s,note)
ts=json.load(open("data/tol_sim.json",encoding='utf-8'))
miss=0; filled=0
for tol,o in ts['tol'].items():
    for c in o['comp']:
        key=(tol,c['n'],round(c['p'],4))
        if key not in look: miss+=1; c['is']=None; c['isn']='?'; continue
        s,note=look[key]
        c['iss']=s; c['is']=(s[5] if s else None); c['isn']=note
        if s: filled+=1
print("comp totali:",sum(len(o['comp']) for o in ts['tol'].values()),"con ISTAT:",filled,"non agganciati:",miss)
ts['fonte_istat_comp']="Indice ISTAT per componente: PPI mensile mercato interno (base 2021) per ATECO e Retribuzioni contrattuali orarie operai (Edilizia/Metalmeccanico/Marittimi), ribasati a marzo 2022=100 sulle finestre quadrimestrali. Acciai/mezzi/energia: proxy PPI dichiarato. Rifiuti/esplosivi: n.d."
json.dump(ts,open("data/tol_sim.json","w",encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print("scritto data/tol_sim.json")
