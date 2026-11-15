"""Module de gestion du serveur réseau TCP asynchrone (V2I).

Exécute un serveur de sockets TCP dans un thread séparé (QThread). 
Il écoute sur le port 5000 pour recevoir et décoder les trames JSON des véhicules
d'urgence, sans bloquer l'interface graphique principale.
"""

import socket
import json
from PySide6.QtCore import QThread, Signal
from database import DatabaseV2I

class ServeurV2I(QThread):
    """Thread réseau dédié à l'écoute des trames entrantes.

    Hérite de QThread pour tourner en tâche de fond. Utilise des signaux
    (pyqtSignal) pour communiquer avec l'interface graphique de manière sécurisée.
    """
    
    # Déclaration des signaux permettant de déclencher des fonctions dans main.py
    alerte_recue = Signal(str)
    fin_alerte = Signal()
    log_reseau = Signal(str)

    def run(self) -> None:
        """Méthode principale du thread exécutant la boucle réseau.

        Crée la socket TCP, la bind sur toutes les interfaces (0.0.0.0), 
        et attend les connexions. Décode le JSON reçu, vérifie le token de
        sécurité, et émet les signaux correspondants vers la GUI tout en 
        historisant dans la base SQLite.

        Returns:
            None
        """
        # L'adresse 0.0.0.0 permet d'écouter sur toutes les cartes réseau de la VM
        # (Très pratique car l'IP changera avec le DHCP de l'IUT)
        HOST = '0.0.0.0'
        PORT = 5000
        
        # Instanciation de la connexion à la base de données
        bdd = DatabaseV2I()
        
        # Création de la socket IPv4 (AF_INET) et TCP (SOCK_STREAM)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            self.log_reseau.emit(f"En écoute TCP sur le port {PORT}")
            
            # Boucle infinie pour maintenir le serveur ouvert
            while True:
                # La méthode accept() est bloquante, c'est pour ça qu'on utilise un QThread
                conn, addr = s.accept()
                with conn:
                    try:
                        # Lecture des données entrantes (buffer de 1024 octets)
                        data = conn.recv(1024)
                        if not data: continue
                            
                        # Désérialisation de la trame JSON (Bytes -> Dictionnaire Python)
                        trame = json.loads(data.decode('utf-8'))
                        
                        # Vérification de sécurité : Seules les trames avec le bon token sont traitées
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
                            # Rejet silencieux d'une trame non authentifiée
                            self.log_reseau.emit(f"[{addr[0]}] REJETÉ : Token invalide")
                            
                    except json.JSONDecodeError:
                        self.log_reseau.emit(f"[{addr[0]}] ERREUR : Trame corrompue")