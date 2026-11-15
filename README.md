# Carrefour intelligent V2I – Équipe WebTL

**SAÉ 3.02 – BUT Réseaux et Télécommunications, IUT de Colmar (UHA)**  
**Groupe WebTL :** Louis LEIBRICH et Antoine THOMANN

La maquette représente le croisement de la rue de la Semm, de la route de Fribourg et de l'axe Nord-Sud à Colmar. Elle démontre comment une infrastructure routière communicante (**V2I** – *Vehicle-to-Infrastructure*) réceptionne des trames réseau TCP/JSON émises par un véhicule de secours (SAMU 68) pour déclencher une préemption immédiate des feux tricolores, dégager la voie prioritaire et journaliser l'intervention dans une base SQLite.

---

## Installer et lancer

### 1. Installer Python, pip et Git

Le projet demande **Python 3.10 ou plus récent**. `pip` sert à installer les bibliothèques du projet, dont `PySide6`. Git sert à récupérer le code depuis GitHub.

**Windows avec PowerShell**

Installez [Python pour Windows](https://www.python.org/downloads/windows/) (en cochant la case *Add Python to PATH* lors de l'installation) et [Git pour Windows](https://git-scm.com/install/windows). Ouvrez ensuite un nouveau terminal PowerShell et vérifiez les versions installées :

~~~powershell
python --version
python -m pip --version
git --version
~~~

`pip` est fourni avec Python. Si la commande affiche `No module named pip`, lancez `python -m ensurepip --upgrade` et vérifiez à nouveau.

**Ubuntu Desktop / Debian**

Ouvrez un terminal (`Ctrl + Alt + T`) et installez les paquets requis (dont `libxcb-cursor0`, indispensable sous Linux pour l'affichage des fenêtres Qt) :

~~~bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git libxcb-cursor0 -y

python3 --version
python3 -m pip --version
git --version
~~~

### 2. Cloner le projet

Dans le terminal, placez-vous dans le dossier où vous voulez ranger le projet. Les commandes sont les mêmes sous Windows et Linux.

~~~bash
git clone https://github.com/MZLBR/SAE_302_WebTL.git
cd SAE_302_WebTL
~~~

### 3. Installer les dépendances et lancer la maquette

L’environnement virtuel `venv` isole les bibliothèques du projet dans son propre dossier.

#### Scénario A : Test sur une seule machine (Local)

**Windows avec PowerShell**

Dans un premier terminal, créez l'environnement virtuel, installez les dépendances et lancez le serveur graphique du carrefour :

~~~powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python serveur/main.py
~~~

Dans un deuxième terminal PowerShell, depuis la racine du projet, activez l'environnement virtuel et lancez la console embarquée du client SAMU :

~~~powershell
.\venv\Scripts\activate
python client/client_samu.py
~~~

**Ubuntu Desktop / Debian**

Dans un premier terminal, lancez le serveur :

~~~bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 serveur/main.py # NE SURTOUT PAS LANCER EN ROOT NI AVEC SUDO
~~~

Dans un deuxième terminal, depuis la racine du projet, lancez le client :

~~~bash
source venv/bin/activate
python3 client/client_samu.py
~~~

*Note pour un test sur un seul PC :* Dans `client/client_samu.py`, vérifiez que la constante `HOST` est réglée sur `'127.0.0.1'` (ou sur l'adresse IPv4 locale de votre machine).

---

#### Scénario B : Déploiement Réseau LAN sur 2 machines (PC Client + VM Ubuntu Serveur)

Pour faire communiquer deux machines distinctes (ou un PC hôte Windows et une machine virtuelle Ubuntu Desktop sous VirtualBox/VMware) :

1. **Configuration réseau de la VM :** Configurez la carte réseau de la machine virtuelle en mode **Accès par pont (Bridged Adapter)** pour qu'elle obtienne sa propre adresse IP sur le réseau local via le DHCP.
2. **Récupérer l'adresse IP du serveur :** Sur la VM Ubuntu qui affiche le carrefour, ouvrez un terminal et tapez :

~~~bash
ip a
~~~

*(ou `hostname -I`)* et notez l'adresse IPv4 associée à l'interface active (ex: `enp0s3` -> `192.168.1.80`).

3. **Lancer le serveur sur la VM Ubuntu :** Le serveur écoute par défaut sur `0.0.0.0:5000` (toutes les interfaces réseau) :

~~~bash
source venv/bin/activate
python3 serveur/main.py
~~~

4. **Lancer le client sur le second PC :** Lancez le script client et saisissez l'adresse IPv4 de la VM serveur lorsqu'elle vous est demandée dans le terminal (ou appuyez sur `Entrée` pour utiliser l'IP par défaut) :

~~~powershell
python client/client_samu.py
~~~

---

## Faire une démonstration

1. **Observation du cycle automatique :** Au lancement de `serveur/main.py`, la fenêtre de supervision s'ouvre. Les véhicules civils (bleus) apparaissent aléatoirement, respectent les distances de sécurité et s'arrêtent aux feux rouges. Le cycle alterne toutes les 8 secondes (avec une phase d'orange de 3 secondes).
2. **Contrôle manuel via l'interface :** Le **Panneau de Contrôle** à droite de l'écran permet d'interagir directement avec la simulation :
   * Cliquez sur **🚗 Ajouter Civil** pour injecter immédiatement un véhicule dans le trafic.
   * Cliquez sur **⏸ Pause / Lecture** pour figer ou reprendre la simulation et l'horloge des feux.
   * Cliquez sur **🚑 Générer SAMU** (ou utilisez les touches `1`, `2` et `0` du clavier) pour tester une préemption locale.
3. **Déclenchement d'une préemption réseau V2I :** Depuis le terminal exécutant `client/client_samu.py`, choisissez l'une des commandes proposées :
   * Tapez `1` + `Entrée` pour demander la priorité sur l'axe **Nord-Sud (`S->N`)**.
   * Tapez `2` + `Entrée` pour demander la priorité sur la **Rue de la Semm (`O->E`)**.
4. **Réaction du carrefour :** Le serveur vérifie le jeton d'authentification (`SAMU68-KEY`). L'encart **Logs système (SQLite)** passe au rouge (`ÉTAT : PRÉEMPTION`), la voie prioritaire est immédiatement dégagée pour éviter tout blocage, les feux basculent en sécurité (passage par l'orange si nécessaire puis blocage au vert sur l'axe du SAMU), et le véhicule d'urgence rouge traverse le carrefour à vitesse élevée (avec capacité de dépassement sécurisé).
5. **Fin d'intervention :** Dans le terminal client, tapez `0` + `Entrée`. Le client envoie la trame `FIN`, le carrefour affiche `FIN D'ALERTE` et reprend son cycle automatique normal.
6. **Vérification de la base de données SQLite :** Pour afficher l'historique horodaté de toutes les interventions enregistrées dans `serveur/logs_systeme.db`, exécutez dans le terminal :

~~~bash
python serveur/lire_bdd.py
~~~

---

## Où lire le code

| Fichier ou dossier | Rôle |
|---|---|
| `serveur/main.py` | Point d'entrée du serveur : instancie l'interface graphique, démarre le thread réseau et connecte les signaux Qt |
| `serveur/interface.py` | Dessin 2D du carrefour (`QPainter`), cycle des feux tricolores, panneau de contrôle et gestion de la préemption |
| `serveur/vehicule.py` | Modèle physique des véhicules (coordonnées, arrêt aux feux, distances de sécurité et algorithme de dépassement du SAMU) |
| `serveur/reseau_thread.py` | Serveur socket TCP asynchrone (`QThread`) écoutant sur `0.0.0.0:5000`, décodage JSON et vérification du token |
| `serveur/database.py` | Gestionnaire SQLite3 (`DatabaseV2I`) créant la table `historiques_samu` et insérant les événements horodatés |
| `serveur/lire_bdd.py` | Utilitaire en ligne de commande pour afficher dans le terminal le contenu de `logs_systeme.db` |
| `client/client_samu.py` | Console embarquée du véhicule d'urgence envoyant les trames TCP/JSON (`URGENCE`, `FIN`) au serveur |
| `requirements.txt` | Liste des dépendances Python externes (`PySide6>=6.5.0`) |

---

## Dépannage (Troubleshooting)

* **Erreur VirtualBox `VERR_SVM_DISABLED` ou `VT-x is disabled` :** Redémarrez le PC hôte, ouvrez le BIOS/UEFI et activez la virtualisation matérielle (**SVM Mode** sur processeur AMD Ryzen ou **Intel Virtualization Technology** sur Intel).
* **Erreur d'affichage VM Ubuntu `[drm] *ERROR* vmwgfx` ou écran noir :** Éteignez la machine virtuelle. Dans les paramètres VirtualBox (*Affichage*), augmentez la mémoire vidéo à **128 Mo** et sélectionnez le contrôleur graphique **VBoxSVGA**.
* **Erreur `ConnectionRefusedError` sur le client :** Vérifiez que `serveur/main.py` est bien lancé, que l'adresse IP renseignée dans `client/client_samu.py` correspond à celle de la machine serveur (`ip a`), que la VM est en mode **Accès par pont (Bridge)** et que le pare-feu n'entrave pas le port TCP 5000 (`sudo ufw allow 5000/tcp`).

---

## Livrables et documentation du projet

Les documents d'analyse et de bilan demandés pour l'évaluation finale se trouvent à la racine du dépôt :
- [Bilan fonctionnel, technique et organisationnel](Bilan_Projet.pdf)
- [Annexe IA-graphie (Usage des IA génératives)](IAGraphie.pdf)
- [Dépendances Python du projet](requirements.txt)