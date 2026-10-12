# Power BI

Il file `.pbix` delle dashboard non è incluso nel repository: contiene dati incorporati (circa 735 mila righe mensili), non si può leggere né confrontare su GitHub e mostra solo una parte di ciò che serve a capire il lavoro. Qui sono pubblicati il suo contenuto logico, che si legge direttamente:

- [`power_query.md`](power_query.md): le sei query che costruiscono il modello dai file del repository, con le relazioni tra le tabelle.
- [`misure_dax.md`](misure_dax.md): le misure e le colonne calcolate usate nelle dashboard, con i valori di controllo.

Gli screenshot delle pagine sono nella cartella [`../dashboard`](../dashboard). Le query leggono il file Excel generato dal notebook, che contiene dati dei clienti e non è incluso nel repository (vedi `../output/README.md`): senza quel file il modello non si può ricostruire, ma la logica resta documentata. Con il file a disposizione, seguendo i due documenti si può ricostruire il modello: dopo aver creato query, relazioni e misure, le misure devono dare i valori della tabella «Valori di controllo» in `misure_dax.md`.
