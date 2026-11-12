class Vehicule:
    def __init__(self, axe, est_samu=False):
        self.axe = axe
        self.est_samu = est_samu
        self.vitesse_max = 8 if est_samu else 3
        
        self.voie_normale = True # Indique si le véhicule est sur sa voie ou en dépassement

        # Configuration des 4 directions : 
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
        self.largeur = 20 if self.dx == 0 else 35
        self.hauteur = 35 if self.dx == 0 else 20

    def avancer(self, feu_est_vert, tous_les_vehicules):
        doit_s_arreter = False

        # --- 1. ARRÊT AUX FEUX (Sauf le SAMU) ---
        if not self.est_samu and not feu_est_vert:
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
                
                # Vérifier si un bouchon est devant sur ma voie normale
                sur_ma_voie = (abs(autre.x - self.x_normal) < 10) if self.dy != 0 else (abs(autre.y - self.y_normal) < 10)
                if sur_ma_voie:
                    dist = (autre.x - self.x_normal)*self.dx + (autre.y - self.y_normal)*self.dy
                    if 0 < dist < 90:
                        obstacle_sur_voie_normale = True

                # Vérifier si une voiture arrive en face sur la voie de dépassement
                sur_voie_opposee = (abs(autre.x - self.x_depass) < 10) if self.dy != 0 else (abs(autre.y - self.y_depass) < 10)
                if sur_voie_opposee:
                    dist_absolue = abs(autre.y - self.y) if self.dy != 0 else abs(autre.x - self.x)
                    if dist_absolue < 250: # Si la voiture en face est à moins de 250 pixels, danger !
                        danger_sur_voie_depassement = True

            # Décision de conduite du SAMU
            if self.voie_normale and obstacle_sur_voie_normale and not danger_sur_voie_depassement:
                self.voie_normale = False # On déboite à gauche !
                if self.dy != 0: self.x = self.x_depass
                else: self.y = self.y_depass
            elif not self.voie_normale and not obstacle_sur_voie_normale:
                self.voie_normale = True # La voie est libre, on se rabat à droite !
                if self.dy != 0: self.x = self.x_normal
                else: self.y = self.y_normal

        # --- 3. ANTI-COLLISION CLASSIQUE (Tous les véhicules) ---
        for autre in tous_les_vehicules:
            if autre is self: continue
            
            # Sont-ils physiquement sur le même couloir (x ou y) actuellement ?
            meme_couloir = (abs(autre.x - self.x) < 10) if self.dy != 0 else (abs(autre.y - self.y) < 10)
            if meme_couloir:
                # Distance : positive = devant, négative = derrière
                dist = (autre.x - self.x)*self.dx + (autre.y - self.y)*self.dy
                
                # Freinage normal derrière une voiture
                if 0 < dist < 50:
                    doit_s_arreter = True
                    
                # Si un civil voit un SAMU arriver en face à contresens (pendant un dépassement)
                # Le civil pile sur les freins d'urgence
                if not self.est_samu and autre.est_samu and (0 < dist < 120):
                    doit_s_arreter = True

        # --- 4. MOUVEMENT ---
        if not doit_s_arreter:
            self.x += self.vitesse_max * self.dx
            self.y += self.vitesse_max * self.dy