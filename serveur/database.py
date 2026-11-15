"""Module de gestion de la base de données locale (SQLite).

Permet d'historiser les événements de préemption V2I (passages du SAMU)
dans un fichier de base de données.
"""

import sqlite3
from datetime import datetime
import os

class DatabaseV2I:
    """Classe gérant la connexion et les requêtes SQL vers la base SQLite."""

    def __init__(self, db_name: str = "logs_systeme.db") -> None:
        """Initialise la connexion à la base de données.

        Args:
            db_name (str, optional): Nom du fichier de base de données. Par défaut "logs_systeme.db".
        """
        # On récupère le chemin absolu du dossier pour éviter les erreurs si on lance le script d'ailleurs
        dossier_actuel = os.path.dirname(os.path.abspath(__file__))
        self.chemin_db = os.path.join(dossier_actuel, db_name)
        
        self.initialiser_bdd()

    def initialiser_bdd(self) -> None:
        """Crée la table d'historique si elle n'existe pas déjà.

        Returns:
            None
        """
        # Utilisation du context manager (with) pour fermer la connexion proprement à la fin
        with sqlite3.connect(self.chemin_db) as connexion:
            curseur = connexion.cursor()
            # Création de la table de logs
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

    def enregistrer_trame(self, axe: str, action: str) -> None:
        """Insère un nouvel événement réseau dans la base de données.

        Args:
            axe (str): L'axe concerné par l'action (ex: "S->N").
            action (str): L'action déclenchée (ex: "URGENCE" ou "FIN").

        Returns:
            None
        """
        # Formatage de l'heure exacte (timestamp)
        maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect(self.chemin_db) as connexion:
            curseur = connexion.cursor()
            # Requête préparée (avec les ?) pour la sécurité (évite les injections SQL)
            curseur.execute('''
                INSERT INTO historiques_samu (date_heure, axe, action)
                VALUES (?, ?, ?)
            ''', (maintenant, axe, action))
            connexion.commit()
            
        print(f"[SQLite] Enregistré : {maintenant} | {action} -> {axe}")