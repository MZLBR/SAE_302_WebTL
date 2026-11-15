"""Module de modélisation des véhicules civils et prioritaires (SAMU).

Définit la classe Vehicule gérant les coordonnées 2D, la vitesse,
la taille (hitbox) et la logique de déplacement (feux, dépassement, freinage).
"""

class Vehicule:
    """Classe représentant une voiture (civile ou urgence) sur la carte."""

    def __init__(self, axe: str, est_samu: bool = False) -> None:
        """Initialise les paramètres physiques et l'axe de circulation.

        Configure les coordonnées de spawn (x, y), les vecteurs de direction
        (dx, dy) et les dimensions selon l'orientation (verticale ou horizontale).

        Args:
            axe (str): L'axe routier emprunté (ex: "S->N", "O->E").
            est_samu (bool, optional): Définit si le véhicule est prioritaire. Par défaut False.
        """
        self.axe = axe
        self.est_samu = est_samu
        # Le SAMU trace plus vite que les civils
        self.vitesse_max = 8 if est_samu else 3
        
        # Gestion du déboitement (True = voie de droite classique, False = à contresens)
        self.voie_normale = True 

        # Initialisation des coordonnées de spawn et des vecteurs de mouvement
        # S->N (monte), N->S (descend), O->E (droite), E->O (gauche)
        if axe == "S->N":
            self.x_normal, self.y_normal = 415, 600
            self.x_depass, self.y_depass = 365, 600
            self.dx, self.dy = 0, -1
        elif axe == "N->S":
            self.x_normal, self.y_normal = 365, -50
            self.x_depass, self.y_depass = 415, -50
            self.dx, self.dy = 0, 1
        elif axe == "O->E":
            self.x_normal, self.y_normal = -50, 315
            self.x_depass, self.y_depass = -50, 265
            self.dx, self.dy = 1, 0
        elif axe == "E->O":
            self.x_normal, self.y_normal = 850, 265
            self.x_depass, self.y_depass = 850, 315
            self.dx, self.dy = -1, 0
            
        self.x, self.y = self.x_normal, self.y_normal
        
        # Adaptation de la hitbox selon le sens (paysage ou portrait)
        self.largeur = 20 if self.dx == 0 else 35
        self.hauteur = 35 if self.dx == 0 else 20

    def avancer(self, feu_est_vert: bool, tous_les_vehicules: list) -> None:
        """Calcule la prochaine position du véhicule selon son environnement.

        Vérifie l'état des feux tricolores, gère l'anti-collision basique
        avec les autres véhicules de la liste, et intègre la logique de
        déboitement spécifique pour l'ambulance.

        Args:
            feu_est_vert (bool): True si le feu de cet axe est au vert.
            tous_les_vehicules (list): La liste complète des objets Vehicule instanciés.

        Returns:
            None
        """
        doit_s_arreter = False

        # --- 1. ARRÊT AUX FEUX (Sauf le SAMU qui grille tout) ---
        if not self.est_samu and not feu_est_vert:
            # On définit les zones de freinage juste avant les lignes de feu
            if self.axe == "S->N" and 380 <= self.y <= 400: doit_s_arreter = True
            elif self.axe == "N->S" and 200 <= self.y <= 220: doit_s_arreter = True
            elif self.axe == "O->E" and 280 <= self.x <= 300: doit_s_arreter = True
            elif self.axe == "E->O" and 460 <= self.x <= 480: doit_s_arreter = True

        # --- 2. INTELLIGENCE DU SAMU (Dépassement) ---
        if self.est_samu:
            obstacle_sur_voie_normale = False
            danger_sur_voie_depassement = False

            for autre in tous_les_vehicules:
                if autre is self: continue
                
                # Vérifie si un civil bloque devant sur ma voie
                sur_ma_voie = (abs(autre.x - self.x_normal) < 10) if self.dy != 0 else (abs(autre.y - self.y_normal) < 10)
                if sur_ma_voie:
                    dist = (autre.x - self.x_normal)*self.dx + (autre.y - self.y_normal)*self.dy
                    if 0 < dist < 90:
                        obstacle_sur_voie_normale = True

                # Radar anti-collision frontale sur la voie de dépassement
                sur_voie_opposee = (abs(autre.x - self.x_depass) < 10) if self.dy != 0 else (abs(autre.y - self.y_depass) < 10)
                if sur_voie_opposee:
                    dist_absolue = abs(autre.y - self.y) if self.dy != 0 else abs(autre.x - self.x)
                    if dist_absolue < 250: # Marge de sécurité de 250 pixels
                        danger_sur_voie_depassement = True

            # Prise de décision de l'IA de l'ambulance
            if self.voie_normale and obstacle_sur_voie_normale and not danger_sur_voie_depassement:
                self.voie_normale = False # On déboite à gauche
                if self.dy != 0: self.x = self.x_depass
                else: self.y = self.y_depass
            elif not self.voie_normale and not obstacle_sur_voie_normale:
                self.voie_normale = True # La voie s'est libérée, on se rabat
                if self.dy != 0: self.x = self.x_normal
                else: self.y = self.y_normal

        # --- 3. ANTI-COLLISION CLASSIQUE (Tous les véhicules) ---
        for autre in tous_les_vehicules:
            if autre is self: continue
            
            # Vérifie si les véhicules partagent le même couloir de pixels
            meme_couloir = (abs(autre.x - self.x) < 10) if self.dy != 0 else (abs(autre.y - self.y) < 10)
            if meme_couloir:
                # Calcul de la distance relative (positive = la voiture est devant)
                dist = (autre.x - self.x)*self.dx + (autre.y - self.y)*self.dy
                
                # Freinage classique si on approche du pare-chocs
                if 0 < dist < 50:
                    doit_s_arreter = True
                    
                # Si un civil voit le SAMU arriver en face à contresens, il pile direct
                if not self.est_samu and autre.est_samu and (0 < dist < 120):
                    doit_s_arreter = True

        # --- 4. APPLICATION DU MOUVEMENT ---
        if not doit_s_arreter:
            self.x += self.vitesse_max * self.dx
            self.y += self.vitesse_max * self.dy