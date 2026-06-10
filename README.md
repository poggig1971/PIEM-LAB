# Navigatore Prezzario Regionale Lombardia — edizione 2026

Dashboard web per la consultazione del Prezzario Regionale dei lavori pubblici della Lombardia, edizione 2026 (codifica LOM261), approvato con DGR XII/6071 del 27 aprile 2026.

Strumento di consultazione non ufficiale ad uso delle imprese. Fa fede esclusivamente la pubblicazione ufficiale di Regione Lombardia.

## Contenuti

La dashboard consente la navigazione delle quattro parti del prezzario: Parte 1 (opere compiute di edilizia civile, urbanizzazione, difesa del suolo e agroforestale, 5.828 voci), Parte 2 (impianti meccanici, elettrici, elettrotecnici, idraulici e antincendio, 13.624 voci), Parte 3 (risorse elementari umane, materiali e strumentali, 20.420 voci) e Parte 4 (raccordo con la precedente struttura, 3.154 voci).

Per ciascuna voce di opera compiuta la scheda di dettaglio riporta: prezzo unitario, importo al netto di spese generali e utili, incidenza della manodopera, prezzi per elevata e modesta complessità (fattori di variabilità), analisi prezzi completa con scomposizione in risorse elementari (quantità, costi unitari, spese generali, utili di impresa), criteri di misurazione, voci incluse ed escluse, raccordo con la codifica RL 2023, categoria SOA e riferimenti normativi.

## Funzionalità

Ricerca full-text per codice, descrizione e parole chiave; navigazione ad albero per categorie gerarchiche; ricerca estesa a tutte le parti; ordinamento per codice, prezzo e incidenza manodopera; esportazione in CSV dell'elenco filtrato; collegamenti ipertestuali dalle analisi prezzi alle schede delle risorse elementari.

## Pubblicazione su GitHub Pages

1. Creare un repository su GitHub (ad esempio `prezzario-lombardia-2026`).
2. Caricare l'intero contenuto della cartella `dashboard` (il file `index.html` e la cartella `data`) nella radice del repository. Per il caricamento da riga di comando:

   ```
   cd dashboard
   git init
   git add .
   git commit -m "Navigatore Prezzario Lombardia 2026"
   git branch -M main
   git remote add origin https://github.com/NOMEUTENTE/prezzario-lombardia-2026.git
   git push -u origin main
   ```

3. Nel repository: Settings → Pages → Source: «Deploy from a branch» → Branch: `main`, cartella `/ (root)` → Save.
4. Dopo alcuni minuti la dashboard sarà raggiungibile all'indirizzo `https://NOMEUTENTE.github.io/prezzario-lombardia-2026/`.

Il peso complessivo dei dati è di circa 57 MB (16 MB di elenchi voci e 41 MB di schede di dettaglio suddivise in 120 file caricati solo all'apertura delle singole schede). Il traffico effettivo per l'utente è molto inferiore grazie alla compressione e al caricamento progressivo.

## Esecuzione in locale

L'apertura diretta del file `index.html` non funziona (i browser bloccano il caricamento dei dati da file locale). Utilizzare il file `Avvia dashboard.bat` (richiede Python installato) oppure un qualsiasi server web statico.

## Rigenerazione dei dati

La cartella `tools` contiene gli script Python utilizzati per generare i file JSON a partire dagli XLSX ufficiali di Regione Lombardia (richiedono il pacchetto `python-calamine`). In caso di aggiornamento del prezzario è sufficiente aggiornare i percorsi nei file ed eseguire nell'ordine `extract_voci.py`, quindi `extract_analisi.py B`, `extract_analisi.py D` e `extract_analisi.py MERGE`.

## Fonti

Regione Lombardia, Prezzario regionale delle opere pubbliche — edizione 2026 (LOM261), approvato con DGR XII/6071 del 27/04/2026, file XLSX ufficiali: elenchi prezzi (parti 1-4), allegati analisi prezzi (parti 1-2), elenchi voci per fattori di variabilità (elevata complessità, modesta complessità, sicurezza). Prezzi in euro, IVA esclusa.
