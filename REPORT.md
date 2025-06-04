# Relazione Tecnica Traccia 1 - Web Server + Sito Web Statico (livello base/intermedio)

## Introduzione

Il progetto consiste nello sviluppo di un semplice server HTTP in Python, realizzato tramite socket, per la pubblicazione di un sito web statico. L’obiettivo è comprendere il funzionamento di base del protocollo HTTP e la gestione delle richieste da parte di un server.

## Struttura del progetto

- **config.py**: parametri di configurazione (host, porta, buffer, ecc.).
- **src/**: codice sorgente del server Python.
- **www/**: directory dei file statici (HTML, CSS, immagini, ecc.).

## Funzionamento del server

Il server utilizza la libreria standard `socket` per ascoltare le richieste su `localhost:8080`. Alla ricezione di una richiesta:
1. Analizza la richiesta HTTP e ne estrae il contenuto.
2. Verifica che versione e metodo della richiesta siano supportati.
3. Cerca il file richiesto nella cartella `www/`.
4. Se il file esiste, risponde con codice 200 e il contenuto del file.
5. Se il file non esiste, risponde con codice 404 e messaggio opportuno.
6. Se avviene un errore, risponde con codice 500 e l'errore avvenuto.

Il server gestisce anche la corretta chiusura delle connessioni al momento dello stop o in caso di errore.

## Estensioni implementate

- **Gestione MIME types**: il server determina il tipo di contenuto da restituire in base all’estensione del file.
- **Logging**: tutte le richieste vengono registrate su console.
- **Layout responsive e animazioni CSS**: il sito statico include stili moderni e adattivi.

## Modalità di esecuzione

Per avviare il server:

```bash
python3 -m src
```

Poi visitare [http://localhost:8080](http://localhost:8080) dal browser.

## Caratteristiche principali

Tra le componenti principali troviamo:
- [`ConnectionManager`](src/connection.py): classe wrapper del socket nativo per semplificarne l'utilizzo.
- [`HTTPClient`](src/server.py): classe wrapper del `ConnectionManager` per l'utilizzo dello standard HTTP.

Inoltre, come funzionalità extra, se viene richiesto un percorso ad una cartella, viene automaticamente fornito il file `index.html` al suo interno o un omonimo file `percorso.html` (dove `percorso` è il nome della cartella). Questo ad eccezione della richiesta di `/index`, che non fornirà il file `index.html` (volutamente, per rispecchiare il funzionamento di siti moderni).

## Conclusioni

Il progetto mostra come realizzare un server HTTP minimale in Python, gestendo richieste GET e servendo file statici, con estensioni utili per un’esperienza web moderna e flessibilità per un'eventuale espansione delle funzionalità.
