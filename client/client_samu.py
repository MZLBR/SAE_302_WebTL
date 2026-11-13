import socket
import json
import time

def envoyer_trame(action, axe=""):
    HOST = '192.168.1.80'  # ATTENTION : À CHANGER LE JOUR DE L'EXAMEN APRÈS AVOIR FAIT 'ip a' SUR LA VM
    PORT = 5000
    
    # Construction de la trame V2I
    trame = {
        "id_vehicule": "SAMU-68-ALPHA",
        "token": "SAMU68-KEY",
        "action": action,
        "axe": axe
    }
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(trame).encode('utf-8'))
        print(f"[+] Succès : Trame '{action}' envoyée au carrefour.")
    except ConnectionRefusedError:
        print("[-] Erreur : Le serveur du carrefour est injoignable (éteint ou mauvaise IP).")

if __name__ == "__main__":
    print("========================================")
    print("   CONSOLE EMBARQUÉE V2I - SAMU 68      ")
    print("========================================")
    
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
        
        time.sleep(0.5)