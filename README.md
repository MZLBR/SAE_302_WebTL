# SAÉ 3.02 - Système de Régulation et Préemption V2I (Équipe WebTL)

## 👥 Identification du Binôme
* **Nom du groupe :** Équipe WebTL
* **Étudiants :** Louis LEIBRICH & Antoine THOMANN
* **Formation :** BUT Réseaux et Télécommunications (2ème année) – IUT de Colmar (UHA)

---

## 📌 Présentation du Projet
Ce projet est une application communicante simulant un carrefour routier intelligent doté d'une technologie **V2I (Vehicle-to-Infrastructure)**. Développée en Python, l'application permet de superviser le trafic civil en temps réel (interface 2D) et d'intercepter des trames réseau TCP/JSON émises par des véhicules prioritaires (SAMU) afin de déclencher une préemption immédiate des feux tricolores et de dégager la voie concernée. Toutes les opérations critiques sont journalisées dans une base de données SQLite locale.

### Arborescence du dépôt
```text
SAE_302_WebTL/
├── client/
│   └── client_samu.py       # Script d'émission des trames d'urgence TCP/JSON
├── serveur/
│   ├── main.py              # Point d'entrée de l'application serveur
│   ├── interface.py         # Interface graphique 2D (PyQt6/PySide6) et logique des feux
│   ├── vehicule.py          # Modélisation physique et déplacement des véhicules
│   ├── reseau_thread.py     # Écoute asynchrone par sockets TCP (QThread)
│   ├── database.py          # Gestionnaire de base de données SQLite3
│   └── lire_bdd.py          # Utilitaire de consultation de l'historique des logs
├── Bilan_Projet.pdf         # Rapport fonctionnel, technique et organisationnel
├── IAGraphie.pdf            # Déclaration et analyse de l'usage des IA génératives
├── requirements.txt         # Liste des dépendances Python
└── README.md                # Documentation d'installation et d'utilisation