import sys
from PySide6.QtWidgets import QApplication
from interface import FenetreCarrefour
from reseau_thread import ServeurV2I

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    fenetre = FenetreCarrefour()
    thread_reseau = ServeurV2I()
    
    # Connexion des signaux réseau -> actions graphiques
    thread_reseau.alerte_recue.connect(fenetre.activer_urgence)
    thread_reseau.fin_alerte.connect(fenetre.reprendre_cycle_normal)
    thread_reseau.log_reseau.connect(fenetre.mettre_a_jour_log)
    
    # Démarrage
    thread_reseau.start()
    fenetre.show()
    
    sys.exit(app.exec())