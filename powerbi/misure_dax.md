# Misure e colonne calcolate DAX

Le formule usate nelle dashboard Power BI del progetto. Le tabelle `Clienti`, `Dim_cliente`, `FactRicavoMensile` e le altre sono descritte in `power_query.md`. Le misure si creano nella tabella `Clienti`, salvo dove indicato; vanno create una alla volta (tasto destro sulla tabella > *Nuova misura*), mentre le due colonne calcolate si creano con *Nuova colonna*.

Non sono incluse le misure del Data Quality Index con valori scritti a mano e quelle delle pagine di lavoro non pubblicate.

## Colonne calcolate (tabella `Clienti`)

### Area Geografica
Assegna ogni provincia a Nord, Centro o Sud. Il Sud comprende anche Sicilia e Sardegna; i clienti senza provincia o all'estero risultano «Non classificata».

```
Area Geografica =
SWITCH(
    TRUE(),

    -- NORD
    Clienti[Provincia] IN {
        "AO", "TO", "VC", "NO", "BI", "VB", "CN", "AT", "AL",
        "MI", "MB", "VA", "CO", "LC", "SO", "BS", "BG",
        "PV", "CR", "MN", "LO",
        "BZ", "TN",
        "VR", "VI", "BL", "TV", "VE", "PD", "RO",
        "UD", "GO", "TS", "PN",
        "GE", "IM", "SP", "SV",
        "PC", "PR", "RE", "MO", "BO", "FE", "RA", "FC", "RN"
    }, "Nord",

    -- CENTRO
    Clienti[Provincia] IN {
        "MS", "LU", "PT", "FI", "LI", "PI", "AR", "SI", "GR", "PO",
        "PG", "TR",
        "PU", "AN", "MC", "FM", "AP",
        "VT", "RI", "RM", "LT", "FR"
    }, "Centro",

    -- SUD E ISOLE
    Clienti[Provincia] IN {
        "AQ", "TE", "PE", "CH",
        "CB", "IS",
        "CE", "BN", "NA", "AV", "SA",
        "FG", "BA", "TA", "BR", "LE", "BT",
        "PZ", "MT",
        "CS", "CZ", "KR", "VV", "RC",
        "PA", "TP", "AG", "CL", "EN", "ME", "RG", "SR",
        "CT",
        "SS", "NU", "OR", "CA", "SU"
    }, "Sud",

    "Non classificata"
)
```

### Top1pct
Vale 1 per il 1% dei clienti con il ricavo più alto nell'ultimo anno (205 clienti su 20.436), 0 per gli altri. È una colonna fissa e non dipende dai filtri dei grafici, per questo tutte le misure sul Top 1% la usano.

```
Top1pct =
VAR SogliaClienti = ROUNDUP ( COUNTROWS ( ALL ( Clienti ) ) / 100, 0 )
VAR Posizione = RANKX ( ALL ( Clienti ), Clienti[ricavo_anno_3], , DESC, SKIP )
RETURN IF ( Posizione <= SogliaClienti, 1, 0 )
```

## Misure di base

```
totale_clienti = DISTINCTCOUNT ( Clienti[Company_ID] )

Ricavo Medio per Cliente =
DIVIDE ( SUM ( Clienti[M_sum] ), [totale_clienti] )

Aumento_valore =
CALCULATE ( SUM ( Clienti[M_sum] ), Clienti[trend_ricavo] = "Aumento" )
```

`Rank ATECO Ricavo Medio` ordina i settori per ricavo medio, considerando solo quelli con almeno 5 clienti, soglia applicata nella misura stessa e quindi valida con qualsiasi filtro o selezione:

```
Rank ATECO Ricavo Medio =
VAR SettoriValidi =
    FILTER (
        ALLSELECTED ( Clienti[ATECO_Desc] ),
        CALCULATE ( [totale_clienti] ) >= 5
    )
RETURN
    IF (
        [totale_clienti] >= 5,
        RANKX ( SettoriValidi, [Ricavo Medio per Cliente], , DESC, DENSE )
    )
```

## Ricavi e clienti attivi per anno

Un cliente è attivo in un anno se il suo ricavo annuale è diverso da zero.

```
Ricavo anno 1 = SUM ( Clienti[ricavo_anno_1] )

Ricavo anno 2 = SUM ( Clienti[ricavo_anno_2] )

Ricavo anno 3 = SUM ( Clienti[ricavo_anno_3] )

Variazione ricavo anno 2 =
DIVIDE (
    SUM ( Clienti[ricavo_anno_2] ) - SUM ( Clienti[ricavo_anno_1] ),
    SUM ( Clienti[ricavo_anno_1] )
)

Variazione ricavo anno 3 =
DIVIDE (
    SUM ( Clienti[ricavo_anno_3] ) - SUM ( Clienti[ricavo_anno_2] ),
    SUM ( Clienti[ricavo_anno_2] )
)

Clienti attivi anno 1 =
CALCULATE ( COUNTROWS ( Clienti ), Clienti[ricavo_anno_1] <> 0 )

Clienti attivi anno 2 =
CALCULATE ( COUNTROWS ( Clienti ), Clienti[ricavo_anno_2] <> 0 )

Clienti attivi anno 3 =
CALCULATE ( COUNTROWS ( Clienti ), Clienti[ricavo_anno_3] <> 0 )

Variazione clienti attivi anno 2 =
DIVIDE ( [Clienti attivi anno 2] - [Clienti attivi anno 1], [Clienti attivi anno 1] )

Variazione clienti attivi anno 3 =
DIVIDE ( [Clienti attivi anno 3] - [Clienti attivi anno 2], [Clienti attivi anno 2] )
```

Nel modello esistono anche due misure equivalenti, usate in alcune schede: `Crescita Ricavi YoY` (uguale a `Variazione ricavo anno 3`) e `Clienti attivi ultimi 12M` (conta i clienti con ricavo dell'ultimo anno maggiore di zero, uguale a `Clienti attivi anno 3`).

```
Crescita Ricavi YoY =
DIVIDE (
    SUM ( Clienti[ricavo_anno_3] ) - SUM ( Clienti[ricavo_anno_2] ),
    SUM ( Clienti[ricavo_anno_2] ),
    0
)

Clienti attivi ultimi 12M =
COUNTROWS ( FILTER ( Clienti, Clienti[ricavo_anno_3] > 0 ) )
```

## Top 1% dei clienti

Tutte basate sulla colonna `Top1pct`. Nei grafici per provincia o per area, `Ricavo Top 1 pct per Provincia`, `Crescita Top 1% Provincia` e `Numero Clienti Top 1% Provincia` sommano i clienti del Top 1% che rientrano in ogni gruppo.

```
Clienti Top 1% =
CALCULATE ( DISTINCTCOUNT ( Clienti[Company_ID] ), Clienti[Top1pct] = 1 )

Quota Top 1 pct =
DIVIDE (
    CALCULATE ( SUM ( Clienti[ricavo_anno_3] ), Clienti[Top1pct] = 1 ),
    SUM ( Clienti[ricavo_anno_3] )
)

Ricavo Top 1 pct per Provincia =
CALCULATE ( SUM ( Clienti[ricavo_anno_3] ), Clienti[Top1pct] = 1 )

Crescita Top 1% Provincia =
CALCULATE (
    SUM ( Clienti[ricavo_anno_3] ) - SUM ( Clienti[ricavo_anno_2] ),
    Clienti[Top1pct] = 1
)

Numero Clienti Top 1% Provincia =
CALCULATE ( DISTINCTCOUNT ( Clienti[Company_ID] ), Clienti[Top1pct] = 1 )
```

## Clienti persi

Sono i clienti con ciclo di vita «Vecchi Persi» o «Recenti Persi» (nessun acquisto da almeno 3 mesi).

```
Clienti persi =
CALCULATE (
    DISTINCTCOUNT ( Clienti[Company_ID] ),
    Clienti[periodo_di_vita] IN { "Vecchi Persi", "Recenti Persi" }
)

Quota clienti persi = DIVIDE ( [Clienti persi], [totale_clienti] )
```

## Grafico mensile

Seconda serie del grafico del ricavo mensile: mostra solo i mesi sotto 7 milioni, cioè i tre minimi ricorrenti (M-28, M-16 e M-4). Si trova nella tabella `FactRicavoMensile`.

```
Ricavo mesi minimi =
VAR r = SUM ( FactRicavoMensile[Ricavo] )
RETURN IF ( r < 7000000, r )
```

## Variazioni per regione e settore

```
Variazione ricavo € =
SUM ( Clienti[ricavo_anno_3] ) - SUM ( Clienti[ricavo_anno_2] )

Variazione ricavo % =
DIVIDE ( [Variazione ricavo €], SUM ( Clienti[ricavo_anno_2] ) )

Variazione ricavo assoluta = ABS ( [Variazione ricavo €] )
```

`Variazione ricavo assoluta` serve ai filtri «Primi N» sulle variazioni: seleziona le variazioni più grandi, positive o negative, mentre le barre mostrano il valore con il segno.

## Qualità dei dati

Le misure usano la tabella `Dim_cliente`; `Clienti con Ricavi Negativi` è nella tabella `Dim_ateco`.

```
Numero Clienti = DISTINCTCOUNT ( Dim_cliente[Company_ID] )

% Clienti Provincia Valorizzata =
DIVIDE (
    CALCULATE ( [Numero Clienti], Dim_cliente[Provincia] <> "prov_non_definite" ),
    [Numero Clienti]
)

% Clienti ATECO Classificabile =
DIVIDE (
    CALCULATE ( [Numero Clienti], Dim_cliente[ATECO] <> "XXX" ),
    [Numero Clienti]
)

Clienti con Ricavi Negativi =
COUNTROWS (
    FILTER (
        VALUES ( Dim_cliente[Company_ID] ),
        CALCULATE (
            COUNTROWS ( FILTER ( FactRicavoMensile, FactRicavoMensile[Ricavo] < 0 ) )
        ) > 0
    )
)
```

## Valori di controllo

Dopo aver ricostruito il modello, queste misure devono dare i seguenti valori sull'intero dataset (nessun filtro):

| Misura | Valore |
|---|---|
| `totale_clienti` | 20.436 |
| `Ricavo anno 1` / `anno 2` / `anno 3` | 112.314.083 € / 106.347.530 € / 118.951.777 € |
| `Variazione ricavo anno 2` / `anno 3` | −5,3% / +11,9% |
| `Clienti attivi anno 1` / `anno 2` / `anno 3` | 15.723 / 14.115 / 13.874 |
| `Variazione clienti attivi anno 2` / `anno 3` | −10,2% / −1,7% |
| `Clienti Top 1%` e `Quota Top 1 pct` | 205 e 48,1% |
| `Clienti persi` e `Quota clienti persi` | 9.430 e 46,1% |
| `% Clienti Provincia Valorizzata` | 85,3% |
| `% Clienti ATECO Classificabile` | 98,0% |
| `Clienti con Ricavi Negativi` | 143 |
| `Ricavo mesi minimi` | tre soli mesi: 6,57 · 6,83 · 6,65 milioni di euro |
