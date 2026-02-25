#-------------------------------------------------
# Meshtastic Packet Monitor - aiutocomputerhelp.it
#---------------------------------------------2026

import serial
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
import queue

DEFAULT_PORT = "COM3"
DEFAULT_BAUDRATE = 115200

DEFAULT_KEYWORDS = ["Received packet", "SNR", "RSSI", "error"]


class SerialMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meshtastic Packet Monitor + Filtri - aiutocomputerhelp.it")
        self.root.geometry("1100x650")

        self.running = True
        self.ser = None
        self.serial_thread = None
        self.match_count = 0

        self.port_var = tk.StringVar(value=DEFAULT_PORT)
        self.baud_var = tk.StringVar(value=str(DEFAULT_BAUDRATE))
        self.keywords_var = tk.StringVar(value=", ".join(DEFAULT_KEYWORDS))
        self.keywords = list(DEFAULT_KEYWORDS)

        self.ui_queue = queue.Queue()

        top = tk.Frame(root)
        top.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(top, text="Porta:").pack(side=tk.LEFT)
        port_entry = tk.Entry(top, textvariable=self.port_var, width=12)
        port_entry.pack(side=tk.LEFT, padx=(4, 12))

        tk.Label(top, text="Baudrate:").pack(side=tk.LEFT)
        baud_entry = tk.Entry(top, textvariable=self.baud_var, width=10)
        baud_entry.pack(side=tk.LEFT, padx=(4, 12))

        tk.Label(top, text="Filtri (separati da virgola):").pack(side=tk.LEFT)
        tk.Entry(top, textvariable=self.keywords_var, width=45).pack(side=tk.LEFT, padx=(4, 12), fill=tk.X, expand=True)

        # Pulsanti Connetti e Sconnetti
        self.connect_btn = tk.Button(top, text="Connetti", command=self.connect_serial, bg="#4CAF50", fg="white")
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 4))
        
        self.disconnect_btn = tk.Button(top, text="Sconnetti", command=self.disconnect_serial, bg="#f44336", fg="white", state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(top, text="Applica filtri", command=self.apply_filters).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(top, text="Pulisci match", command=self.clear_matches).pack(side=tk.LEFT)

        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        left_frame = tk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Log Seriale Completo").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        tk.Label(right_frame, text="Stringhe Trovate").pack(anchor="w")
        self.match_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, bg="#111", fg="#00ff00")
        self.match_text.pack(fill=tk.BOTH, expand=True)

        bottom = tk.Frame(right_frame)
        bottom.pack(fill=tk.X, pady=(6, 0))

        self.counter_label = tk.Label(bottom, text="Match: 0")
        self.counter_label.pack(side=tk.LEFT)

        self.status_label = tk.Label(bottom, text="Stato: non connesso")
        self.status_label.pack(side=tk.RIGHT)

        self.log_text.tag_config("highlight", foreground="red")

        self.root.after(50, self.process_ui_queue)

#############
        
    def apply_filters(self):
        raw = self.keywords_var.get().strip()
        if not raw:
            messagebox.showwarning("Filtri", "Inserisci almeno una parola chiave.")
            return

        kw = [k.strip() for k in raw.split(",") if k.strip()]
        if not kw:
            messagebox.showwarning("Filtri", "Nessun filtro valido trovato.")
            return

        self.keywords = kw
        self.ui_queue.put(("log", f"[INFO] Filtri aggiornati: {', '.join(self.keywords)}\n"))

    def clear_matches(self):
        self.match_text.delete("1.0", tk.END)
        self.match_count = 0
        self.counter_label.config(text="Match: 0")

# Avvia la connessione seriale
    def connect_serial(self):
        
         
        if self.serial_thread and self.serial_thread.is_alive():
            messagebox.showwarning("Connessione", "Connessione già attiva")
            return
            
         
        current_port = self.port_var.get().strip()
        current_baud = self.baud_var.get().strip()
        
        
        if not current_port:
            messagebox.showerror("Errore", "Inserisci una porta COM valida")
            return
        
        if not current_baud.isdigit():
            messagebox.showerror("Errore", "Il baudrate deve essere un numero")
            return
            
         
        self.connect_btn.config(state=tk.DISABLED)
        self.disconnect_btn.config(state=tk.NORMAL)
        
         
        self.serial_thread = threading.Thread(
            target=self.read_serial_thread,
            args=(current_port, int(current_baud)),
            daemon=True
        )
        self.serial_thread.start()
        
        self.ui_queue.put(("log", f"[INFO] Tentativo di connessione a {current_port} @ {current_baud}...\n"))

# termina connessione
    def disconnect_serial(self):
       
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                self.ui_queue.put(("log", "[INFO] Disconnessione in corso...\n"))
        except Exception as e:
            self.ui_queue.put(("log", f"[ERRORE] Durante la disconnessione: {e}\n"))
        finally:
            self.ser = None
            

##########
    def open_serial_no_reset(self, port, baud):
         
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = baud
        ser.timeout = 1
        ser.dtr = False
        ser.rts = False
        ser.open()
        ser.setDTR(False)
        ser.setRTS(False)
        time.sleep(0.3)

        return ser

    def read_serial_thread(self, port, baud):
         
        try:
            self.ser = self.open_serial_no_reset(port, baud)
            self.ui_queue.put(("status", f"connesso a {port} @ {baud}"))
            self.ui_queue.put(("log", f"[INFO] Connesso a {port} @ {baud}\n"))
        except Exception as e:
            self.ui_queue.put(("status", "errore"))
            self.ui_queue.put(("log", f"[ERRORE] Impossibile connettersi a {port}: {e}\n"))
            # Riabilita pulsante connetti in caso di errore
            self.ui_queue.put(("enable_connect", None))
            return

        # Ciclo di lettura
        while self.running and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue

                self.ui_queue.put(("log", line + "\n"))

                for keyword in self.keywords:
                    if keyword.lower() in line.lower():
                        self.ui_queue.put(("match", f"[{keyword}] {line}\n"))
                        self.ui_queue.put(("inc", None))
                        self.ui_queue.put(("beep", None))
                        break

            except Exception as e:
                if self.ser and self.ser.is_open:
                    self.ui_queue.put(("log", f"[ERRORE] Lettura seriale: {e}\n"))
                break

        # Pulizia alla fine del thread
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                self.ui_queue.put(("log", "[INFO] Porta seriale chiusa\n"))
        except Exception as e:
            self.ui_queue.put(("log", f"[ERRORE] Durante la chiusura: {e}\n"))
        finally:
            self.ser = None
            self.ui_queue.put(("status", "disconnesso"))
            self.ui_queue.put(("enable_connect", None))
########
            
    def process_ui_queue(self):
        
        if not self.running or not self.root.winfo_exists():
            return

        try:
            while True:
                kind, payload = self.ui_queue.get_nowait()

                if kind == "log":
                    self.append_log(payload)
                elif kind == "match":
                    self.match_text.insert(tk.END, payload)
                    self.match_text.see(tk.END)
                elif kind == "inc":
                    self.match_count += 1
                    self.counter_label.config(text=f"Match: {self.match_count}")
                elif kind == "status":
                    self.status_label.config(text=f"Stato: {payload}")
                elif kind == "beep":
                    try:
                        import winsound
                        winsound.Beep(1000, 150)
                    except Exception:
                        pass
                elif kind == "enable_connect":
                    self.connect_btn.config(state=tk.NORMAL)
                    self.disconnect_btn.config(state=tk.DISABLED)

        except queue.Empty:
            pass

        self.root.after(50, self.process_ui_queue)


# Aggiunge testo al log con evidenziazione
    def append_log(self, text):
        
        self.log_text.insert(tk.END, text)

        for keyword in self.keywords:
            if keyword.lower() in text.lower():
                start = self.log_text.index("end-1c linestart")
                end = self.log_text.index("end-1c lineend")
                self.log_text.tag_add("highlight", start, end)
                break

        self.log_text.see(tk.END)

    def on_close(self):
        """Gestisce la chiusura della finestra"""
        self.running = False
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass
        self.root.destroy()

#######################################################################
if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
    
