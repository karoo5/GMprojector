🎲 GMProjector

    Un proiettore da tavolo per il Game Master!
    Mostra immagini e riproduci musica direttamente da un'interfaccia di controllo (backend), trasmettendo in tempo reale a un frontend visibile ai giocatori.

📸 Cos'è GMProjector?

GMProjector è un'applicazione standalone per Windows pensata per master di giochi di ruolo o narratori. Permette di:

    Mostrare immagini a tutto schermo ai giocatori (frontend)

    Aggiungere ritratti PNG sovrapposti all'immagine principale (per NPC o stati)

    Riprodurre musica di sottofondo organizzata in cartelle tematiche (mood)

    Scrivere e mostrare testi su schermo

    Usare una doppia interfaccia: backend (per il master), frontend (per i giocatori)

⚙️ Come funziona

Quando avvii l’eseguibile gmprojector.exe, si apre il backend nel browser predefinito (http://localhost:5000).

Da lì puoi:

    Caricare un'immagine (JPG, PNG, GIF, ecc.) da mostrare

    Caricare uno o più ritratti PNG (che vengono visualizzati sopra l’immagine principale)

    Caricare un audio personalizzato, oppure selezionare un mood tra le cartelle presenti in audio/

    Scrivere un testo per mostrarlo in sovrimpressione

    Pulire lo schermo o resettare i ritratti/testo

    Aprire il frontend (http://localhost:5000/frontend) su un secondo schermo o un secondo device per i giocatori

📁 Struttura delle cartelle

Quando viene eseguito per la prima volta, il programma crea (se non presenti) queste cartelle:

/audio         # Contiene le sottocartelle dei mood musicali
/uploads       # Contiene immagini e file audio caricati manualmente

📂 Cartella audio/

Organizzata in sottocartelle, ognuna corrisponde a un “mood” selezionabile dal backend.
Esempio:

audio/
├── tension/
│   ├── dark-ambience.mp3
│   └── heartbeat.wav
├── calm/
│   └── forest.mp3

    Durante l’uso, verrà scelto randomicamente un file audio tra quelli della cartella selezionata.

📂 Cartella uploads/

Contiene:

    Le immagini .jpg, .png, ecc. caricate per lo sfondo principale

    I ritratti PNG sovrapposti

    I file audio personalizzati trascinati nell'interfaccia

🖥️ Modalità d'uso

    Avvia gmprojector.exe

    Nel browser si aprirà http://localhost:5000 (il backend)

    Aprire http://[indirizzo IP]:5000/frontend su un secondo schermo

    Usa i pulsanti del backend per controllare cosa vedranno i giocatori

💡 Suggerimenti

    Puoi caricare anche immagini animate .gif

    Se vuoi usare un secondo device (tablet, smartphone, altro PC) per il frontend, puoi accedere a http://<tuo_ip_lan>:5000/frontend (l’indirizzo IP ti verrà mostrato nel backend)

    I file presenti in audio/ vengono inclusi nella versione eseguibile (se compili tu) oppure estratti automaticamente se lanci il programma

🔧 Requisiti (solo per chi vuole modificarlo)

    Python 3.10+ (consigliato non installarlo da Microsoft Store)

    Flask

    Flask-SocketIO

    Eventlet (se si usa la modalità async)

    PyInstaller (per creare l'eseguibile standalone)

🛠️ Compilazione in .exe

    Non necessaria se usi il programma già pronto!
    Se vuoi compilarlo da solo, è stato progettato per funzionare con PyInstaller in modalità --onedir.

📜 Licenza & Credits

Questo progetto è distribuito gratuitamente.
Chiunque può:

    Usarlo

    Condividerlo

    Modificarlo

…purché mantenga i credits visibili nel backend e in eventuali redistribuzioni.

Autore: [W. Bersani]

Icona: generata con risorse open source.
Musiche: fornire proprie tracce royalty-free.
Progetto creato con ❤️ per la comunità dei giocatori di ruolo.
