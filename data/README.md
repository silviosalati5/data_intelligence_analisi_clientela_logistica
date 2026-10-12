# Dati di input

Cartella con i file di input del progetto. Il dataset dei clienti (`dataset.csv`) è stato fornito dalla scuola a fini didattici e **non è pubblicato** in questo repository, per decisione della scuola: qui è descritto il formato atteso. Sono inclusi `ATECO.xlsb` (classificazione pubblica ISTAT) e `mapping_province.xlsx`.

| File | Formato | Contenuto | Usato da |
|---|---|---|---|
| `dataset.csv` (non incluso) | CSV, separatore `;`, codifica `latin1` | Un cliente per riga (20.436 clienti). Colonne anagrafiche: `ATECO`, `ATECO_Desc`, `Natura`, `Fatturato`, `Dipendenti`, `Provincia`. Colonne mensili: 36 colonne da `M-35` (mese più vecchio) a `M-0` (mese più recente) con i ricavi del mese. | Notebook |
| `ATECO.xlsb` | Excel binario | Classificazione delle attività economiche ATECO 2007, in forma gerarchica (3.157 voci). Colonne: `Codice ISTAT`, `Descrizione ISTAT`, `Codice Completo`, `Codice Dotless`, `Codice REA (solo num)`. | Notebook |
| `mapping_province.xlsx` | Excel, foglio `Sheet1` | 110 province con regione e coordinate di riferimento (usate dalle mappe e dai grafici per regione). Colonne: `Codice_Provincia` (sigla), `Codice_ISTAT_Provincia`, `Capoluogo`, `Regione`, `Latitudine`, `Longitudine`, `Tipo` (Provincia / UTS, Città Metropolitana). Non include `Estero` e `prov_non_definite`, che non compaiono sulle mappe. | Mappe delle dashboard (non letto dal notebook) |

## Note

- **Sigla `NA` (Napoli).** In `dataset.csv` la provincia `NA` va letta come testo. In Pandas la lettura automatica la converte in valore mancante: il notebook usa `keep_default_na=False` e considera mancanti solo le celle vuote (3.000 clienti senza provincia).
- **Coordinate (`mapping_province.xlsx`).** `Latitudine` e `Longitudine` sono celle numeriche con 6 decimali. Se le coordinate passano per un CSV aperto in Excel con impostazioni regionali italiane, il punto decimale può essere letto come separatore delle migliaia (`42.349848` diventa `42349848`): dopo ogni importazione controllare che le latitudini siano comprese tra 36 e 47.
- **File ISTAT.** La classificazione ATECO deriva da una pubblicazione dell'ISTAT, rilasciata con licenza Creative Commons Attribuzione (CC BY): è consentito riutilizzarla citando la fonte (Istituto nazionale di statistica, ISTAT). La regione di ciascuna provincia in `mapping_province.xlsx` coincide con quella dell'elenco ISTAT dei comuni.
- **Notebook.** Legge solo `dataset.csv` e `ATECO.xlsb` e si ferma con un errore chiaro se uno dei due manca. Per rieseguirlo bisogna copiare `dataset.csv` in questa cartella.
