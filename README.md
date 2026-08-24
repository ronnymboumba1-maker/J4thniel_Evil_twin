README.md pour EVIL TWIN

```markdown
# 📡 EVIL TWIN ULTIME

## Attaque Evil Twin avec interface graphique

### 📌 Description

EVIL TWIN ULTIME est un outil de test de sécurité WiFi qui simule une attaque Evil Twin. Il permet de créer un faux point d'accès WiFi pour capturer les mots de passe dans un cadre éducatif et légal.

### ✨ Fonctionnalités

- ✅ **Scan WiFi** : Détection des réseaux disponibles
- ✅ **Création de faux AP** : Point d'accès identique au réseau cible
- ✅ **Capture de mots de passe** : Portail captif de vérification
- ✅ **Attaque de déauthentification** : Déconnexion des clients
- ✅ **Interface graphique** : Contrôle complet
- ✅ **Export des données** : Sauvegarde des mots de passe capturés

### 🚀 Installation

```bash
# 1. Cloner le dépôt
https://github.com/ronnymboumba1-maker/J4thniel_Evil_twin
cd J4thniel_Evil_twin

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Installer les dépendances système
sudo apt install aircrack-ng hostapd dnsmasq
```

🎯 Utilisation

```bash
# Lancer l'interface (nécessite sudo)
sudo python3 evil_twin.py
```