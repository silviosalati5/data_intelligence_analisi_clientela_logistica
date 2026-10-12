# Query Power Query

Le sei query che costruiscono il modello delle dashboard Power BI a partire dai file del repository. Le prime tre leggono il foglio «Dataset Clienti» di `output/dataset_analisi_completa.xlsx` (file generato dal notebook, non incluso nel repository perché contiene dati dei clienti); la quarta legge le coordinate delle province da `data/mapping_province.xlsx`; le ultime due derivano dalla seconda.

**Come usarle.** In Power BI Desktop: *Home > Trasforma dati*; per ogni query crea una query vuota (*Nuova origine > Query vuota*), aprila con *Editor avanzato*, incolla il codice, assegna il nome indicato e sostituisci `<CARTELLA_REPOSITORY>` con il percorso della cartella in cui hai salvato il repository. Poi *Chiudi e applica*. Crea le query nell'ordine in cui compaiono qui: `Dim_ateco` e `Dim_macro_ateco` dipendono da `Dim_cliente`.

Il file di coordinate deve avere latitudini tra 35 e 50 e longitudini tra 6 e 19 (decimali con il punto): se un programma di fogli di calcolo ha rimosso il separatore decimale, la query si ferma con un errore.

## Relazioni da creare

Tutte «molti a uno», con filtro in un solo senso.

| Dal lato «molti» | Al lato «uno» |
|---|---|
| `Clienti[Provincia]` | `Province_Italia_PowerBI_2026[Codice_Provincia]` |
| `Clienti[ATECO]` | `Dim_ateco[ATECO]` |
| `Clienti[ATECO_Macro]` | `Dim_macro_ateco[ATECO_Macro]` |
| `Dim_cliente[ATECO]` | `Dim_ateco[ATECO]` |
| `Dim_cliente[ATECO_Macro]` | `Dim_macro_ateco[ATECO_Macro]` |
| `FactRicavoMensile[Company_ID]` | `Dim_cliente[Company_ID]` |

Nella tabella `FactRicavoMensile`, la colonna `Mese` va ordinata per `Indice Mese` in ordine decrescente (da M-35 a M-0). Il modello originale contiene anche alcune tabelle di lavoro non usate dalle pagine mostrate nel README, non incluse qui.

## 1. Clienti

Tabella principale, una riga per cliente (20.436 righe). Rispetto all'Excel, rinomina `m_sum` in `M_sum` e `pct_mesi_attivi` in `%_Mesi_Attivi`, aggiunge `Totale_36M` (uguale a `M_sum`), `Primi_12M` (uguale a `ricavo_anno_1`) e `ATECO_Macro`, sostituisce «XXX» con «Non definito» in `ATECO_Desc` e abbrevia la descrizione di 20 settori (record `NomiBrevi`): nel modello `ATECO_Desc` contiene il nome breve per quei codici, nell'Excel resta il nome ufficiale. `ATECO_Macro` si ricava dal codice: «XXX_Macro» per `XXX`, i primi 7 caratteri per i codici di 10 caratteri, il codice intero negli altri casi.

```
let
    NomiBrevi = [
        #"G.47.91.10" = "Commercio online",
        #"H.53.20.00" = "Corrieri e servizi postali",
        #"H.49.41.00" = "Trasporto merci su strada",
        #"N.82.99.99" = "Altri servizi alle imprese",
        #"J.62.01.00" = "Produzione di software",
        #"G.47.62.20" = "Cartoleria e forniture per ufficio",
        #"H.52.29.22" = "Servizi logistici per la distribuzione merci",
        #"N.82.19.09" = "Fotocopie e supporto d'ufficio",
        #"G.47.91.30" = "Vendita per corrispondenza",
        #"O.8411C1" = "Governo e organi costituzionali",
        #"H.52.21.90" = "Altre attività connesse ai trasporti terrestri",
        #"M.70.22.01" = "Consulenza per la logistica aziendale",
        #"N.77.40.00" = "Diritti di proprietà intellettuale",
        #"G.47.78.92" = "Spaghi, cordami e imballaggi",
        #"G.46.49.90" = "Ingrosso di prodotti di consumo non alimentari",
        #"G.47.71.10" = "Abbigliamento per adulti",
        #"G.46.49.40" = "Ingrosso di articoli sportivi",
        #"G.47.29.90" = "Altri prodotti alimentari al dettaglio",
        #"M.70.22.09" = "Consulenza imprenditoriale e amministrativa",
        #"G.47.22.00" = "Macellerie e prodotti a base di carne"
    ],
    Origine = Excel.Workbook(File.Contents("<CARTELLA_REPOSITORY>\output\dataset_analisi_completa.xlsx"), null, true),
    Foglio = Origine{[Item="Dataset Clienti",Kind="Sheet"]}[Data],
    #"Intestazioni alzate di livello" = Table.PromoteHeaders(Foglio, [PromoteAllScalars=true]),
    #"Modificato tipo" = Table.TransformColumnTypes(#"Intestazioni alzate di livello", {{"Company_ID", Int64.Type}, {"Provincia", type text}, {"ATECO", type text}, {"ATECO_Desc", type text}, {"Macro_Categ", type text}, {"Natura", type text}, {"Dipendenti", Int64.Type}, {"Fatturato", Int64.Type}, {"m_sum", Int64.Type}, {"ricavo_anno_1", Int64.Type}, {"ricavo_anno_2", Int64.Type}, {"ricavo_anno_3", Int64.Type}, {"mesi_attivi", Int64.Type}, {"pct_mesi_attivi", type number}, {"primo_mese_offset", Int64.Type}, {"ultimo_mese_offset", Int64.Type}, {"periodo_di_vita", type text}, {"comportamento_frequenza", type text}, {"trend_ricavo", type text}, {"trend_rel_slope", type number}, {"var_yoy_perc", type number}, {"flag_collasso", Int64.Type}, {"M-35", Int64.Type}, {"M-34", Int64.Type}, {"M-33", Int64.Type}, {"M-32", Int64.Type}, {"M-31", Int64.Type}, {"M-30", Int64.Type}, {"M-29", Int64.Type}, {"M-28", Int64.Type}, {"M-27", Int64.Type}, {"M-26", Int64.Type}, {"M-25", Int64.Type}, {"M-24", Int64.Type}, {"M-23", Int64.Type}, {"M-22", Int64.Type}, {"M-21", Int64.Type}, {"M-20", Int64.Type}, {"M-19", Int64.Type}, {"M-18", Int64.Type}, {"M-17", Int64.Type}, {"M-16", Int64.Type}, {"M-15", Int64.Type}, {"M-14", Int64.Type}, {"M-13", Int64.Type}, {"M-12", Int64.Type}, {"M-11", Int64.Type}, {"M-10", Int64.Type}, {"M-9", Int64.Type}, {"M-8", Int64.Type}, {"M-7", Int64.Type}, {"M-6", Int64.Type}, {"M-5", Int64.Type}, {"M-4", Int64.Type}, {"M-3", Int64.Type}, {"M-2", Int64.Type}, {"M-1", Int64.Type}, {"M-0", Int64.Type}}),
    #"Rinominate colonne" = Table.RenameColumns(#"Modificato tipo", {{"m_sum", "M_sum"}, {"pct_mesi_attivi", "%_Mesi_Attivi"}}),
    #"Aggiunta Totale_36M" = Table.AddColumn(#"Rinominate colonne", "Totale_36M", each [M_sum], Int64.Type),
    #"Aggiunta Primi_12M" = Table.AddColumn(#"Aggiunta Totale_36M", "Primi_12M", each [ricavo_anno_1], Int64.Type),
    #"Aggiunta ATECO_Macro" = Table.AddColumn(#"Aggiunta Primi_12M", "ATECO_Macro", each if [ATECO] = "XXX" then "XXX_Macro" else if Text.Length([ATECO]) = 10 then Text.Start([ATECO], 7) else [ATECO], type text),
    #"Sostituito valore" = Table.ReplaceValue(#"Aggiunta ATECO_Macro", "XXX", "Non definito", Replacer.ReplaceText, {"ATECO_Desc"}),
    #"Aggiunta nome breve" = Table.AddColumn(#"Sostituito valore", "ATECO_Desc_breve", each Record.FieldOrDefault(NomiBrevi, [ATECO], [ATECO_Desc]), type text),
    #"Rimossa ATECO_Desc" = Table.RemoveColumns(#"Aggiunta nome breve", {"ATECO_Desc"}),
    #"Nome breve in ATECO_Desc" = Table.RenameColumns(#"Rimossa ATECO_Desc", {{"ATECO_Desc_breve", "ATECO_Desc"}})
in
    #"Nome breve in ATECO_Desc"
```

## 2. Dim_cliente

Stessa origine di `Clienti`, senza la sostituzione di «XXX» e senza i nomi brevi. Alimenta le misure di qualità dei dati e le relazioni.

```
let
    Origine = Excel.Workbook(File.Contents("<CARTELLA_REPOSITORY>\output\dataset_analisi_completa.xlsx"), null, true),
    Foglio = Origine{[Item="Dataset Clienti",Kind="Sheet"]}[Data],
    #"Intestazioni alzate di livello" = Table.PromoteHeaders(Foglio, [PromoteAllScalars=true]),
    #"Modificato tipo" = Table.TransformColumnTypes(#"Intestazioni alzate di livello", {{"Company_ID", Int64.Type}, {"Provincia", type text}, {"ATECO", type text}, {"ATECO_Desc", type text}, {"Macro_Categ", type text}, {"Natura", type text}, {"Dipendenti", Int64.Type}, {"Fatturato", Int64.Type}, {"m_sum", Int64.Type}, {"ricavo_anno_1", Int64.Type}, {"ricavo_anno_2", Int64.Type}, {"ricavo_anno_3", Int64.Type}, {"mesi_attivi", Int64.Type}, {"pct_mesi_attivi", type number}, {"primo_mese_offset", Int64.Type}, {"ultimo_mese_offset", Int64.Type}, {"periodo_di_vita", type text}, {"comportamento_frequenza", type text}, {"trend_ricavo", type text}, {"trend_rel_slope", type number}, {"var_yoy_perc", type number}, {"flag_collasso", Int64.Type}, {"M-35", Int64.Type}, {"M-34", Int64.Type}, {"M-33", Int64.Type}, {"M-32", Int64.Type}, {"M-31", Int64.Type}, {"M-30", Int64.Type}, {"M-29", Int64.Type}, {"M-28", Int64.Type}, {"M-27", Int64.Type}, {"M-26", Int64.Type}, {"M-25", Int64.Type}, {"M-24", Int64.Type}, {"M-23", Int64.Type}, {"M-22", Int64.Type}, {"M-21", Int64.Type}, {"M-20", Int64.Type}, {"M-19", Int64.Type}, {"M-18", Int64.Type}, {"M-17", Int64.Type}, {"M-16", Int64.Type}, {"M-15", Int64.Type}, {"M-14", Int64.Type}, {"M-13", Int64.Type}, {"M-12", Int64.Type}, {"M-11", Int64.Type}, {"M-10", Int64.Type}, {"M-9", Int64.Type}, {"M-8", Int64.Type}, {"M-7", Int64.Type}, {"M-6", Int64.Type}, {"M-5", Int64.Type}, {"M-4", Int64.Type}, {"M-3", Int64.Type}, {"M-2", Int64.Type}, {"M-1", Int64.Type}, {"M-0", Int64.Type}}),
    #"Rinominate colonne" = Table.RenameColumns(#"Modificato tipo", {{"m_sum", "M_sum"}, {"pct_mesi_attivi", "%_Mesi_Attivi"}}),
    #"Aggiunta ATECO_Macro" = Table.AddColumn(#"Rinominate colonne", "ATECO_Macro", each if [ATECO] = "XXX" then "XXX_Macro" else if Text.Length([ATECO]) = 10 then Text.Start([ATECO], 7) else [ATECO], type text)
in
    #"Aggiunta ATECO_Macro"
```

## 3. FactRicavoMensile

Porta le 36 colonne mensili in righe: una riga per cliente e mese (735.696 righe), con le colonne `Company_ID`, `Mese`, `Ricavo` e `Indice Mese`. Serve al grafico del ricavo mensile.

```
let
    Origine = Excel.Workbook(File.Contents("<CARTELLA_REPOSITORY>\output\dataset_analisi_completa.xlsx"), null, true),
    Foglio = Origine{[Item="Dataset Clienti",Kind="Sheet"]}[Data],
    #"Intestazioni alzate di livello" = Table.PromoteHeaders(Foglio, [PromoteAllScalars=true]),
    #"Rimosse altre colonne" = Table.SelectColumns(#"Intestazioni alzate di livello", {"M-35", "M-34", "M-33", "M-32", "M-31", "M-30", "M-29", "M-28", "M-27", "M-26", "M-25", "M-24", "M-23", "M-22", "M-21", "M-20", "M-19", "M-18", "M-17", "M-16", "M-15", "M-14", "M-13", "M-12", "M-11", "M-10", "M-9", "M-8", "M-7", "M-6", "M-5", "M-4", "M-3", "M-2", "M-1", "M-0", "Company_ID"}),
    #"Modificato tipo" = Table.TransformColumnTypes(#"Rimosse altre colonne", {{"Company_ID", Int64.Type}}),
    #"Trasformate tramite UnPivot solo le colonne selezionate" = Table.Unpivot(#"Modificato tipo", {"M-35", "M-34", "M-33", "M-32", "M-31", "M-30", "M-29", "M-28", "M-27", "M-26", "M-25", "M-24", "M-23", "M-22", "M-21", "M-20", "M-19", "M-18", "M-17", "M-16", "M-15", "M-14", "M-13", "M-12", "M-11", "M-10", "M-9", "M-8", "M-7", "M-6", "M-5", "M-4", "M-3", "M-2", "M-1", "M-0"}, "Attributo", "Valore"),
    #"Rinominate colonne1" = Table.RenameColumns(#"Trasformate tramite UnPivot solo le colonne selezionate", {{"Attributo", "Mese"}, {"Valore", "Ricavo"}}),
    #"Modificato tipo1" = Table.TransformColumnTypes(#"Rinominate colonne1", {{"Ricavo", type number}}),
    #"Aggiunta colonna personalizzata" = Table.AddColumn(#"Modificato tipo1", "Indice Mese", each Number.FromText(Text.AfterDelimiter([Mese], "-")))
in
    #"Aggiunta colonna personalizzata"
```

## 4. Province_Italia_PowerBI_2026

Coordinate e regione di ciascuna provincia (110 righe), usate per le mappe e per i grafici per regione. Si ferma con un errore se le latitudini non sono tra 35 e 50.

```
let
    Origine = Excel.Workbook(File.Contents("<CARTELLA_REPOSITORY>\data\mapping_province.xlsx"), null, true),
    Fogli = Table.SelectRows(Origine, each [Kind] = "Sheet"),
    Foglio = Fogli{0}[Data],
    #"Intestazioni alzate di livello" = Table.PromoteHeaders(Foglio, [PromoteAllScalars=true]),
    #"Modificato tipo" = Table.TransformColumnTypes(#"Intestazioni alzate di livello", {{"Codice_Provincia", type text}, {"Codice_ISTAT_Provincia", Int64.Type}, {"Capoluogo", type text}, {"Regione", type text}, {"Latitudine", type number}, {"Longitudine", type number}, {"Tipo", type text}}),
    Controllo = if List.Max(#"Modificato tipo"[Latitudine]) > 50 or List.Min(#"Modificato tipo"[Latitudine]) < 35 then error "Coordinate non valide: le latitudini devono essere tra 35 e 50. Controlla i decimali del file (es. 45,458626 e non 45458626)" else #"Modificato tipo"
in
    Controllo
```

## 5. Dim_ateco

Elenco dei codici ATECO con la loro macro-categoria, derivato da `Dim_cliente`. Ospita la misura `Clienti con Ricavi Negativi`.

```
let
    Origine = Dim_cliente,
    #"Rimosse altre colonne" = Table.SelectColumns(Origine, {"ATECO", "ATECO_Macro"}),
    #"Rimossi duplicati" = Table.Distinct(#"Rimosse altre colonne")
in
    #"Rimossi duplicati"
```

## 6. Dim_macro_ateco

Elenco delle macro-categorie ATECO, derivato da `Dim_ateco`.

```
let
    Origine = Dim_ateco,
    #"Rimosse altre colonne" = Table.SelectColumns(Origine, {"ATECO_Macro"}),
    #"Rimossi duplicati" = Table.Distinct(#"Rimosse altre colonne")
in
    #"Rimossi duplicati"
```
