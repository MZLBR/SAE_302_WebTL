"""Client réseau V2I pour simuler l'ordinateur de bord d'un véhicule du SAMU.

Ce script se connecte au serveur du carrefour (la VM) en TCP
et envoie des trames JSON pour forcer la préemption des feux.
"""

import socket
import json
import time

def envoyer_trame(host: str, action: str, axe: str = "") -> None:
    """Envoie une trame réseau au serveur du carrefour.

    Crée une socket TCP, se connecte à la VM et transmet l'ordre au format JSON.

    Args:
        host (str): L'adresse IP du serveur du carrefour.
        action (str): L'ordre à envoyer ("URGENCE" ou "FIN").
        axe (str, optional): L'axe de circulation (ex: "S->N"). Vide par défaut.

    Returns:
        None
    """
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
            s.settimeout(3.0) # Évite de bloquer longtemps si l'IP est mauvaise
            s.connect((host, PORT))
            # On convertit le dico en string JSON puis en bytes pour l'envoi réseau
            s.sendall(json.dumps(trame).encode('utf-8'))
        print(f"[+] Succès : Trame '{action}' envoyée au carrefour ({host}:{PORT}).")
    except (ConnectionRefusedError, TimeoutError, OSError):
        print(f"[-] Erreur : Le serveur ({host}:{PORT}) est injoignable.")

if __name__ == "__main__":
    print("========================================")
    print("   CONSOLE EMBARQUÉE V2I - SAMU 68      ")
    print("========================================")
    
    # Permet de saisir l'IP sans modifier le code le jour de l'examen
    ip_saisie = input("IP du serveur carrefour [Entrée par défaut = 192.168.1.80] : ").strip()
    HOST = ip_saisie if ip_saisie else "192.168.1.80"
    print(f"[i] Cible configurée sur : {HOST}:5000")
    
    # Boucle infinie pour garder le menu interactif ouvert
    while True:
        print("\nCommandes disponibles :")
        print("  [1] Demander la priorité (Nord-Sud)")
        print("  [2] Demander la priorité (Rue de la Semm)")
        print("  [0] Fin d'intervention (Retour à la normale)")
        
        choix = input("\nVotre choix : ")
        
        if choix == "1":
            envoyer_trame(HOST, "URGENCE", "S->N")
        elif choix == "2":
            envoyer_trame(HOST, "URGENCE", "O->E")
        elif choix == "0":
            envoyer_trame(HOST, "FIN")
            print("[i] Fin d'alerte envoyée. Reprise du trafic civil.")
        else:
            print("[!] Commande invalide.")
        
        # Petite pause pour éviter de spammer le processeur
        time.sleep(0.5)