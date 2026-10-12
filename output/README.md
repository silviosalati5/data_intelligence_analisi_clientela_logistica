# Output: dataset finale

`dataset_analisi_completa.xlsx` è generato da `notebook/analisi_segmentazione_clienti.ipynb` (Fase 9) a partire dai file in `data/`. **Il file non è incluso nel repository**, perché contiene i dati dei singoli clienti (il foglio `Dataset Clienti` ha una riga per cliente); questa pagina documenta la struttura che si ottiene rieseguendo il notebook con il dataset originale. Contiene 6 fogli. Gli importi sono in euro; i riferimenti alle fasi indicano la sezione del notebook in cui la colonna viene calcolata.

## Foglio `Dataset Clienti` (20.436 righe, 58 colonne)

Una riga per cliente.

### Anagrafica

| Colonna | Definizione | Fase |
|---|---|---|
| `Company_ID` | Identificativo progressivo (1-20.436) assegnato secondo l'ordine delle righe del file originale. | 7 |
| `Provincia` | Sigla automobilistica. Sigle storiche aggiornate (FO→FC, PS→PU, OT→SS, CI→SU); `Estero` per TI ed EE; `prov_non_definite` per le province mancanti (3.000 clienti). La sigla `NA` (Napoli) è letta come testo. | 1, 3 |
| `ATECO` | Codice ATECO a 10 caratteri; `XXX` se mancante o `ND` (403 clienti). | 2 |
| `ATECO_Desc` | Descrizione del codice, una sola per codice. Per i 23 codici con più descrizioni si usa quella ISTAT più specifica (o la più frequente, se il codice non è nel dizionario). | 2 |
| `Macro_Categ` | Sezione ATECO (A-U); `NON DEFINITA` per `XXX`. | 2, 8 |
| `Natura` | Natura giuridica del cliente, dal dataset originale (invariata). | - |
| `Dipendenti` | Numero di dipendenti; 0 se mancante o non numerico. Proxy della dimensione aziendale. | 4 |
| `Fatturato` | Fatturato **dichiarato dal cliente**. Conservato per tracciabilità, **non usato nelle analisi** perché poco affidabile: nel 29,5% dei clienti è zero o mancante, e non misura il ricavo generato per l'azienda. | 4 |

### Ricavi

| Colonna | Definizione | Fase |
|---|---|---|
| `m_sum` | Ricavo generato per l'azienda: somma dei 36 mesi (da `M-35` a `M-0`). | 4 |
| `ricavo_anno_1` | Somma di `M-35`...`M-24` (anno più vecchio). | 5 |
| `ricavo_anno_2` | Somma di `M-23`...`M-12`. | 5 |
| `ricavo_anno_3` | Somma di `M-11`...`M-0` (anno più recente). | 5 |

### Comportamento d'acquisto

| Colonna | Definizione | Fase |
|---|---|---|
| `mesi_attivi` | Numero di mesi con ricavo maggiore di zero (0-36). | 5 |
| `pct_mesi_attivi` | `mesi_attivi / 36 × 100`. | 5 |
| `primo_mese_offset` | Offset del primo mese con ricavo (35 = il più vecchio). | 5 |
| `ultimo_mese_offset` | Offset dell'ultimo mese con ricavo (0 = il più recente). | 5 |

### Segmentazioni

| Colonna | Definizione | Fase |
|---|---|---|
| `periodo_di_vita` | `Vecchi` se `primo_mese_offset` > 9, altrimenti `Recenti`; `Persi` se `ultimo_mese_offset` ≥ 3, altrimenti `Attivi`. Quattro valori: Vecchi Attivi, Vecchi Persi, Recenti Attivi, Recenti Persi. | 6 |
| `comportamento_frequenza` | In base a `pct_mesi_attivi`: `Continuativi` sopra l'80%, `Occasionali` sotto il 30%, `Scostanti` nel mezzo. | 6 |
| `trend_ricavo` | `Aumento`, `Diminuzione` o `Stabile`, dalla pendenza di Theil-Sen sui 36 mesi con test di Kendall (α = 0,05, soglia del 2% al mese rispetto alla spesa media). | 6 |
| `trend_rel_slope` | Pendenza di Theil-Sen espressa in % mensile della spesa media. | 6 |

### Segnale di collasso

| Colonna | Definizione | Fase |
|---|---|---|
| `var_yoy_perc` | Variazione % del ricavo dell'anno 3 rispetto all'anno 2. Vuota se il ricavo dell'anno 2 è zero (6.321 clienti). | 7B |
| `flag_collasso` | `1` se il cliente è rilevante (`ricavo_anno_2` ≥ 75° percentile, pari a 1.401 €) e vale (a) `ricavo_anno_3` sotto il 50% di `ricavo_anno_2`, oppure (b) ricavo degli ultimi 6 mesi sotto il 5% della propria media semestrale precedente. Altrimenti `0`. | 7B |

### Serie mensile

`M-35`, `M-34`, ..., `M-0`: ricavo del cliente in ciascun mese (36 colonne). `M-0` è il mese più recente. I valori negativi sono storni o note di credito.

## Fogli aggregati

| Foglio | Righe | Colonne |
|---|---|---|
| `Aggregazione Provincia` | 109 | `Provincia`, `numero_clienti`, `ricavo_totale` (somma di `m_sum`), `clienti_attivi` (periodo di vita Attivi), `clienti_persi` (numero meno attivi), `%_attivi` |
| `Aggregazione ATECO` | 1.204 | `Macro_Categ_code`, `ATECO`, `ATECO_Desc` e le stesse misure; una riga per codice |
| `Aggregazione Macro Area` | 22 | `Macro_Categ_code`, `Macro_Categ` e le stesse misure; le 21 sezioni A-U più `X` (non definita), anche se senza clienti |

## Fogli di dettaglio

Hanno le stesse 22 colonne di analisi del foglio `Dataset Clienti`, senza la serie mensile.

| Foglio | Righe | Criterio |
|---|---|---|
| `Clienti Persi` | 9.430 | `periodo_di_vita` = Vecchi Persi o Recenti Persi |
| `Rischio Churn` | 723 | `ricavo_anno_2` ≥ 75° percentile, `m_sum` > 0 e `ultimo_mese_offset` ≥ 2 (nessun acquisto da almeno 2 mesi) |
