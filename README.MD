# Meshtastic Packet Monitor 

Un monitor seriale progettato specificamente per dispositivi **Meshtastic**. Visualizza e filtra i pacchetti in tempo reale con evidenziazione delle parole chiave e conteggio dei match.

##  Caratteristiche

-  **Connessione manuale** - Connetti/sconnetti quando vuoi senza reset automatico
-  **Doppia visualizzazione** - Log completo a sinistra, match filtrati a destra
-  **Filtri personalizzabili** - Monitora solo le parole chiave che ti interessano
-  **Alert sonori** - Beep ad ogni nuovo match trovato
-  **Conteggio match** - Contatore in tempo reale delle occorrenze
-  **Evidenziazione** - Righe con match evidenziate in rosso nel log principale
-  **Multi-threading** - Interfaccia sempre reattiva

##  Requisiti di Sistema

- Python 3.6 o superiore
- Porta seriale USB/COM disponibile

python -m venv venv
# Su Windows:
venv\Scripts\activate
# Su Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

python meshtastic_monitor.py
