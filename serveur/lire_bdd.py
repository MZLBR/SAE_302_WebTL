"""Script utilitaire de lecture des journaux d'événements SQLite.

Affiche dans la console l'intégralité de l'historique enregistré dans
la table des logs de la base locale (logs_systeme.db).
"""

import sqlite3
import os

def afficher_historique() -> None:
    """Récupère et affiche le contenu de la table historiques_samu.

    Établit une connexion à la base de données locale, exécute une
    requête SELECT complète et formate la sortie dans le terminal.
    Gère l'exception si le fichier de base de données est introuvable.

    Returns:
        None
    """
    # Sécurisation du chemin absolu (évite les erreurs si on lance le script depuis la racine)
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    chemin_db = os.path.join(dossier_actuel, "logs_systeme.db")

    print("==================================================")
    print("      HISTORIQUE DES INTERVENTIONS (SQLite)       ")
    print("==================================================")

    try:
        # Ouverture de la connexion avec 'with' pour garantir la fermeture du fichier DB
        with sqlite3.connect(chemin_db) as connexion:
            curseur = connexion.cursor()
            
            # Requête SQL pour lire toute la table
            curseur.execute("SELECT * FROM historiques_samu")
            lignes = curseur.fetchall()
            
            if not lignes:
                print("Aucun historique trouvé. La base est vide.")
            else:
                for ligne in lignes:
                    # fetchall renvoie une liste de tuples : (id, date_heure, axe, action)
                    # Le :<10 permet de padder l'axe sur 10 caractères pour aligner les colonnes
                    print(f"ID {ligne[0]:02d} | {ligne[1]} | {ligne[2]:<10} | {ligne[3]}")
                    
    except sqlite3.OperationalError:
        # Catch de l'erreur si main.py n'a jamais tourné et que le fichier .db n'existe pas
        print("[-] Erreur : La base de données n'a pas encore été créée.")
        
    print("==================================================")

if __name__ == "__main__":
    afficher_historique()