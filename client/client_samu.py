"""Client réseau V2I pour simuler l'ordinateur de bord d'un véhicule du SAMU.

Ce script se connecte au serveur du carrefour (la VM) en TCP
et envoie des trames JSON pour forcer la préemption des feux.
"""

import socket
import json
import time

def envoyer_trame(action: str, axe: str = "") -> None:
    """Envoie une trame réseau au serveur du carrefour.

    Crée une socket TCP, se connecte à la VM et transmet l'ordre au format JSON.

    Args:
        action (str): L'ordre à envoyer ("URGENCE" ou "FIN").
        axe (str, optional): L'axe de circulation (ex: "S->N"). Vide par défaut.

    Returns:
        None
    """
    # IP de la VM Ubuntu (à modifier le jour de la soutenance avec la commande 'ip a')
    HOST = '192.168.1.80'
    PORT = 5000
    
    # On prépare le dictionnaire avec les infos de sécurité du CdC
    trame = {
        "id_vehicule": "SAMU-68-ALPHA",
        "token": "SAMU68-KEY",
        "action": action,
        "axe": axe
    }
    
    try:
        # Ouverture de la socket en IPv4 (AF_INET) et TCP (SOCK_STREAM)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            # On convertit le dico en string JSON puis en bytes pour l'envoi réseau
            s.sendall(json.dumps(trame).encode('utf-8'))
        print(f"[+] Succès : Trame '{action}' envoyée au carrefour.")
    except ConnectionRefusedError:
        print("[-] Erreur : Le serveur du carrefour est injoignable (vérifier si la VM tourne).")

if __name__ == "__main__":
    print("========================================")
    print("   CONSOLE EMBARQUÉE V2I - SAMU 68      ")
    print("========================================")
    
    # Boucle infinie pour garder le menu interactif ouvert
    while True:
        print("\nCommandes disponibles :")
        print("  [1] Demander la priorité (Nord-Sud)")
        print("  [2] Demander la priorité (Rue de la Semm)")
        print("  [0] Fin d'intervention (Retour à la normale)")
        
        choix = input("\nVotre choix : ")
        
        if choix == "1":
            envoyer_trame("URGENCE", "S->N")
        elif choix == "2":
            envoyer_trame("URGENCE", "O->E")
        elif choix == "0":
            envoyer_trame("FIN")
            print("[i] Fin d'alerte envoyée. Reprise du trafic civil.")
        else:
            print("[!] Commande invalide.")
        
        # Petite pause pour éviter de spammer le processeur
        time.sleep(0.5)