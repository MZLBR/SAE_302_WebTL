"""Point d'entrée principal du serveur de simulation de carrefour V2I.

Initialise l'application graphique PyQt6/PySide6, instancie la fenêtre
principale du carrefour, configure le QThread réseau (sockets) et démarre
la boucle d'événements.
"""

import sys
from PySide6.QtWidgets import QApplication
from interface import FenetreCarrefour
from reseau_thread import ServeurV2I

# Point d'entrée classique d'un script Python
if __name__ == "__main__":
    # 1. Initialisation de la boucle d'événements Qt (indispensable pour l'UI)
    app = QApplication(sys.argv)
    
    # 2. Instanciation de nos deux composants : le graphique et le réseau
    fenetre = FenetreCarrefour()
    thread_reseau = ServeurV2I()
    
    # 3. Connexion des Signaux & Slots (Communication inter-threads)
    # C'est ce mécanisme qui permet au thread TCP de déclencher des actions
    # sur l'interface graphique de manière "thread-safe", sans la faire planter.
    thread_reseau.alerte_recue.connect(fenetre.activer_urgence)
    thread_reseau.fin_alerte.connect(fenetre.reprendre_cycle_normal)
    thread_reseau.log_reseau.connect(fenetre.mettre_a_jour_log)
    
    # 4. Démarrage des processus
    # On lance l'écoute réseau en arrière-plan (qui écoute sur 0.0.0.0:5000)
    thread_reseau.start()
    
    # On affiche l'interface graphique 2D à l'écran
    fenetre.show()
    
    # On maintient le programme en vie dans la boucle infinie de PyQt
    sys.exit(app.exec())