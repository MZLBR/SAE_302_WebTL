import sqlite3
import os

def afficher_historique():
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    chemin_db = os.path.join(dossier_actuel, "logs_systeme.db")

    print("==================================================")
    print("      HISTORIQUE DES INTERVENTIONS (SQLite)       ")
    print("==================================================")

    try:
        with sqlite3.connect(chemin_db) as connexion:
            curseur = connexion.cursor()
            curseur.execute("SELECT * FROM historiques_samu")
            lignes = curseur.fetchall()
            
            if not lignes:
                print("Aucun historique trouvé. La base est vide.")
            else:
                for ligne in lignes:
                    # ligne correspond à : (id, date_heure, axe, action)
                    print(f"ID {ligne[0]:02d} | {ligne[1]} | {ligne[2]:<10} | {ligne[3]}")
    except sqlite3.OperationalError:
        print("Erreur : La base de données n'a pas encore été créée.")
        
    print("==================================================")

if __name__ == "__main__":
    afficher_historique()