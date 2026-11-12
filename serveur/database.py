import sqlite3
from datetime import datetime
import os

class DatabaseV2I:
    def __init__(self, db_name="logs_systeme.db"):
        # Place le fichier de la base de données dans le même dossier que ce script
        dossier_actuel = os.path.dirname(os.path.abspath(__file__))
        self.chemin_db = os.path.join(dossier_actuel, db_name)
        self.initialiser_bdd()

    def initialiser_bdd(self):
        # Crée la table si elle n'existe pas encore
        with sqlite3.connect(self.chemin_db) as connexion:
            curseur = connexion.cursor()
            curseur.execute('''
                CREATE TABLE IF NOT EXISTS historiques_samu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_heure TEXT,
                    axe TEXT,
                    action TEXT
                )
            ''')
            connexion.commit()
            print("[SQLite] Base de données prête.")

    def enregistrer_trame(self, axe, action):
        # Récupère l'heure exacte
        maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insère la ligne dans la base de données
        with sqlite3.connect(self.chemin_db) as connexion:
            curseur = connexion.cursor()
            curseur.execute('''
                INSERT INTO historiques_samu (date_heure, axe, action)
                VALUES (?, ?, ?)
            ''', (maintenant, axe, action))
            connexion.commit()
            
        print(f"[SQLite] Enregistré : {maintenant} | {action} -> {axe}")