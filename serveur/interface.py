"""Interface graphique principale (UI) et logique du carrefour V2I.

Ce module gère l'affichage 2D via PyQt6/PySide6, le cycle temporel des feux, 
la physique basique des véhicules et l'intégration des événements réseau 
(préemption) reçus par le QThread.
"""

import sys
import random
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, QTimer

from vehicule import Vehicule

class FenetreCarrefour(QMainWindow):
    """Classe principale de l'interface graphique héritant de QMainWindow."""

    def __init__(self) -> None:
        """Initialise la fenêtre, les timers et les éléments graphiques du tableau de bord.

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("Supervision V2I - Carrefour Semm / Fribourg (Colmar)")
        
        # On élargit la fenêtre à 1100px pour caser le panneau de contrôle à droite
        self.setFixedSize(1100, 600)
        self.setStyleSheet("background-color: #1e1e1e;")

        # --- VARIABLES D'ÉTAT ---
        self.etat_feux = 0 
        self.mode_statut = "NORMAL - CYCLE AUTOMATIQUE"
        self.derniere_trame = "Aucune trame reçue"
        self.alerte_active = False
        self.en_pause = False

        # --- GESTION DE LA CIRCULATION ---
        self.liste_vehicules = []

        # Timers gérant la boucle d'événements PyQt
        self.timer_spawn = QTimer()
        self.timer_spawn.timeout.connect(self.generer_vehicule_civil)
        self.timer_spawn.start(3000)

        self.timer_physique = QTimer()
        self.timer_physique.timeout.connect(self.mettre_a_jour_physique)
        self.timer_physique.start(33) # Environ 30 FPS pour un affichage fluide

        self.timer_feux = QTimer()
        self.timer_feux.timeout.connect(self.changer_feux)
        self.timer_feux.start(8000)

        # ================= BOUTONS DU PANNEAU DE CONTRÔLE =================
        
        self.btn_samu = QPushButton("🚑 Générer SAMU", self)
        self.btn_samu.setGeometry(820, 50, 260, 45)
        self.btn_samu.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; font-size: 14px; border-radius: 5px;")
        # Fonction lambda pour passer un argument directement au clic
        self.btn_samu.clicked.connect(lambda: self.activer_urgence(random.choice(["S->N", "O->E"])))

        self.btn_civil = QPushButton("🚗 Ajouter Civil", self)
        self.btn_civil.setGeometry(820, 110, 260, 45)
        self.btn_civil.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; font-size: 14px; border-radius: 5px;")
        self.btn_civil.clicked.connect(self.generer_vehicule_civil)

        self.btn_pause = QPushButton("⏸ Pause / Lecture", self)
        self.btn_pause.setGeometry(820, 170, 260, 45)
        self.btn_pause.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold; font-size: 14px; border-radius: 5px;")
        self.btn_pause.clicked.connect(self.basculer_pause)

    # ================= LOGIQUE DES VÉHICULES =================
    
    def generer_vehicule_civil(self) -> None:
        """Génère un nouveau véhicule civil sur un axe aléatoire.

        Vérifie qu'il n'y a pas d'urgence en cours et qu'aucun autre véhicule
        ne bloque le point d'apparition (anti-collision au spawn).

        Returns:
            None
        """
        # On bloque le spawn si le carrefour est en urgence ou en pause
        if self.alerte_active or self.en_pause: return
        
        axe = random.choice(["S->N", "N->S", "O->E", "E->O"])
        nouveau_vehicule = Vehicule(axe, est_samu=False)
        
        # Sécurité : on évite que les voitures spawnent les unes sur les autres
        trop_proche = False
        for v in self.liste_vehicules:
            if v.axe == axe and not v.est_samu:
                if axe == "S->N" and v.y > 540: trop_proche = True
                elif axe == "N->S" and v.y < 20: trop_proche = True
                elif axe == "O->E" and v.x < 10: trop_proche = True
                elif axe == "E->O" and v.x > 790: trop_proche = True
                
        if not trop_proche:
            self.liste_vehicules.append(nouveau_vehicule)

    def mettre_a_jour_physique(self) -> None:
        """Calcule la nouvelle position de tous les véhicules à l'écran.

        Gère l'avancement en fonction de l'état des feux et supprime les 
        véhicules qui sortent du champ de la fenêtre.

        Returns:
            None
        """
        if self.en_pause: return
        ns_vert = (self.etat_feux == 0)
        semm_vert = (self.etat_feux == 2)

        # On itère sur une copie de la liste ([:]) pour pouvoir supprimer des éléments proprement
        for v in self.liste_vehicules[:]:
            feu_vert = ns_vert if v.axe in ["S->N", "N->S"] else semm_vert
            v.avancer(feu_vert, self.liste_vehicules)
            
            # Nettoyage de la RAM : on supprime la voiture si elle sort de la map
            if v.y < -100 or v.x > 900 or v.y > 700 or v.x < -100:
                self.liste_vehicules.remove(v)
                
        # On force PyQt à redessiner la frame
        self.update()

    # ================= LOGIQUE D'URGENCE & PAUSE =================

    def basculer_pause(self) -> None:
        """Met en pause ou relance la simulation (timers et physique).

        Returns:
            None
        """
        self.en_pause = not self.en_pause
        if self.en_pause:
            self.timer_feux.stop()
            self.mode_statut = "EN PAUSE"
        else:
            if not self.alerte_active: self.timer_feux.start(8000)
            self.mode_statut = "NORMAL - CYCLE AUTOMATIQUE"
        self.update()

    def keyPressEvent(self, event) -> None:
        """Intercepte les touches du clavier pour le contrôle manuel (debug).

        Args:
            event (QKeyEvent): L'événement clavier natif de PyQt.

        Returns:
            None
        """
        if event.key() == Qt.Key.Key_1: self.activer_urgence("S->N")
        elif event.key() == Qt.Key.Key_2: self.activer_urgence("O->E")
        elif event.key() == Qt.Key.Key_0: self.reprendre_cycle_normal()

    def activer_urgence(self, axe_prioritaire: str) -> None:
        """Force la préemption du carrefour pour un véhicule d'urgence.

        Arrête le cycle normal, dégage la voie prioritaire, génère le SAMU
        et modifie l'état des feux selon l'axe demandé.

        Args:
            axe_prioritaire (str): L'axe à libérer (ex: "S->N").

        Returns:
            None
        """
        self.timer_feux.stop()
        self.alerte_active = True
        self.mode_statut = f"PRÉEMPTION - {axe_prioritaire}"

        # Dégagement d'urgence : on purge les civils de l'axe pour libérer la route
        self.liste_vehicules = [v for v in self.liste_vehicules if v.axe != axe_prioritaire]
        
        samu = Vehicule(axe_prioritaire, est_samu=True)
        self.liste_vehicules.append(samu)

        # Logique de basculement des feux au vert
        if axe_prioritaire in ["S->N", "N->S"]:
            if self.etat_feux == 2:
                self.etat_feux = 3
                self.update()
                QTimer.singleShot(3000, lambda: self.forcer_etat(0))
            else: self.forcer_etat(0)
        elif axe_prioritaire in ["O->E", "E->O"]:
            if self.etat_feux == 0:
                self.etat_feux = 1
                self.update()
                QTimer.singleShot(3000, lambda: self.forcer_etat(2))
            else: self.forcer_etat(2)

    def forcer_etat(self, nouvel_etat: int) -> None:
        """Modifie manuellement l'état des feux et rafraîchit l'affichage.

        Args:
            nouvel_etat (int): L'index du nouvel état (0, 1, 2 ou 3).

        Returns:
            None
        """
        self.etat_feux = nouvel_etat
        self.update()

    def reprendre_cycle_normal(self) -> None:
        """Désactive l'alerte V2I et relance le cycle régulier des feux.

        Returns:
            None
        """
        self.alerte_active = False
        self.mode_statut = "NORMAL - CYCLE AUTOMATIQUE"
        self.changer_feux()

    def mettre_a_jour_log(self, message: str) -> None:
        """Actualise le texte de la dernière trame affichée sur le panneau.

        Ce slot est appelé depuis le QThread réseau.

        Args:
            message (str): Le contenu brut ou formaté de la trame TCP.

        Returns:
            None
        """
        self.derniere_trame = message
        self.update()

    # ================= AFFICHAGE GRAPHIQUE =================

    def changer_feux(self) -> None:
        """Passe à l'état suivant dans le cycle des feux tricolores.

        Gère les tempos (8s pour le vert/rouge, 3s pour l'orange).

        Returns:
            None
        """
        self.etat_feux = (self.etat_feux + 1) % 4
        if self.etat_feux in [0, 2]: self.timer_feux.start(8000)
        else: self.timer_feux.start(3000)
        self.update()

    def dessiner_feu(self, painter: QPainter, x: int, y: int, couleur_hex: str, label: str) -> None:
        """Dessine un bloc de feu tricolore à l'aide du QPainter.

        Args:
            painter (QPainter): L'outil de dessin de PyQt.
            x (int): Coordonnée horizontale.
            y (int): Coordonnée verticale.
            couleur_hex (str): Le code couleur HTML (ex: "#00ff66").
            label (str): Le texte descriptif associé au feu.

        Returns:
            None
        """
        # Boîtier du feu
        painter.setBrush(QColor("#2c3e50"))
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawRect(x, y, 30, 30)
        
        # Effet de lumière (Halo transparent)
        halo = QColor(couleur_hex)
        halo.setAlpha(60)
        painter.setBrush(halo)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x - 5, y - 5, 40, 40)

        # L'ampoule principale
        painter.setBrush(QColor(couleur_hex))
        painter.drawEllipse(x + 5, y + 5, 20, 20)

    def dessiner_hud(self, painter: QPainter) -> None:
        """Génère l'encart d'informations textuelles (HUD) du panneau latéral.

        Args:
            painter (QPainter): L'outil de dessin de PyQt.

        Returns:
            None
        """
        # Dessin du bloc gris foncé en bas à droite
        painter.setBrush(QColor("#2c3e50"))
        painter.setPen(QPen(QColor("#1a252f"), 2))
        painter.drawRoundedRect(820, 350, 260, 200, 5, 5)

        painter.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(835, 380, "Logs système (SQLite) :")

        couleur_texte = "#ff3333" if self.alerte_active else "#00ff66"
        painter.setPen(QColor(couleur_texte))
        painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        painter.drawText(835, 420, f"> ÉTAT : {self.mode_statut}")
        
        painter.setPen(QColor("#bdc3c7"))
        painter.drawText(835, 460, "> DERNIÈRE TRAME :")
        painter.drawText(835, 480, f"  {self.derniere_trame}")

    def paintEvent(self, event) -> None:
        """Méthode native de Qt appelée à chaque rafraîchissement d'écran.

        S'occupe de l'ordre d'affichage (Z-index) : Routes -> Feux -> Voitures -> HUD.

        Args:
            event (QPaintEvent): L'événement de dessin de PyQt.

        Returns:
            None
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        stylo_pointille = QPen(QColor("#bdc3c7"), 2, Qt.PenStyle.DashLine)

        # 1. ROUTE FRIBOURG (Diagonale)
        painter.save()
        painter.translate(350, 350)
        painter.rotate(-45)
        painter.setBrush(QColor("#34495e"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(-400, 0, 400, 80)
        painter.restore()

        # 2. ROUTES PRINCIPALES (Croix centrale)
        painter.setBrush(QColor("#34495e"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(350, 0, 100, 600)
        painter.drawRect(0, 250, 800, 100)

        # Marquage au sol
        painter.setPen(stylo_pointille)
        painter.drawLine(400, 0, 400, 600)
        painter.drawLine(0, 300, 800, 300)
        
        painter.setBrush(QColor("#34495e"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(350, 250, 100, 100)

        # 3. FEUX TRICOLORES
        c_vert, c_orange, c_rouge = "#00ff66", "#ffaa00", "#ff3333"
        couleur_NS, couleur_SEMM = c_rouge, c_rouge
        
        if self.etat_feux == 0: couleur_NS = c_vert
        elif self.etat_feux == 1: couleur_NS = c_orange
        elif self.etat_feux == 2: couleur_SEMM = c_vert
        elif self.etat_feux == 3: couleur_SEMM = c_orange

        self.dessiner_feu(painter, 465, 200, couleur_NS, "Nord")
        self.dessiner_feu(painter, 305, 370, couleur_NS, "Sud")
        self.dessiner_feu(painter, 305, 200, couleur_SEMM, "Semm (O)")
        self.dessiner_feu(painter, 465, 370, couleur_SEMM, "Semm (E)")

        # 4. VEHICULES
        for v in self.liste_vehicules:
            if v.est_samu: painter.setBrush(QColor("#e74c3c"))
            else: painter.setBrush(QColor("#3498db"))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawRect(v.x, v.y, v.largeur, v.hauteur)

        # 5. PANNEAU DE CONTRÔLE (Masque la sortie des véhicules à droite)
        painter.setBrush(QColor("#ecf0f1"))
        painter.setPen(QPen(QColor("#bdc3c7"), 2))
        painter.drawRect(800, 0, 300, 600)

        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.setPen(QColor("#2c3e50"))
        painter.drawText(820, 30, "Panneau de Contrôle")

        # 6. HUD (Logs)
        self.dessiner_hud(painter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreCarrefour()
    fenetre.show()
    sys.exit(app.exec())