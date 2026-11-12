import socket
import json
from PySide6.QtCore import QThread, Signal
from database import DatabaseV2I # NOUVEAU : On importe notre base de données

class ServeurV2I(QThread):
    alerte_recue = Signal(str)
    fin_alerte = Signal()
    log_reseau = Signal(str)

    def run(self):
        HOST = '0.0.0.0' # Prêt pour le réseau de l'IUT
        PORT = 5000
        
        # NOUVEAU : On initialise la connexion à la BDD
        bdd = DatabaseV2I()
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            self.log_reseau.emit(f"En écoute TCP sur le port {PORT}")
            
            while True:
                conn, addr = s.accept()
                with conn:
                    try:
                        data = conn.recv(1024)
                        if not data: continue
                            
                        trame = json.loads(data.decode('utf-8'))
                        
                        if trame.get("token") == "SAMU68-KEY":
                            action = trame.get("action")
                            axe = trame.get("axe", "Aucun")
                            
                            if action == "URGENCE":
                                self.log_reseau.emit(f"[{addr[0]}] AUTH OK : URGENCE {axe}")
                                self.alerte_recue.emit(axe)
                                bdd.enregistrer_trame(axe, "Début Préemption") # Enregistrement BDD
                                
                            elif action == "FIN":
                                self.log_reseau.emit(f"[{addr[0]}] AUTH OK : FIN D'ALERTE")
                                self.fin_alerte.emit()
                                bdd.enregistrer_trame("Tous", "Fin Préemption") # Enregistrement BDD
                        else:
                            self.log_reseau.emit(f"[{addr[0]}] REJETÉ : Token invalide")
                            
                    except json.JSONDecodeError:
                        self.log_reseau.emit(f"[{addr[0]}] ERREUR : Trame corrompue")