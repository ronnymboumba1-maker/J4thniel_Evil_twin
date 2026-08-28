
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

📦 INSTALLATION COMPLÈTE

1. Dépendances système (obligatoires)

```bash
# Ubuntu/Debian/Kali
sudo apt-get update
sudo apt-get install -y aircrack-ng iwconfig iptables

# Arch Linux
sudo pacman -S aircrack-ng iwconfig iptables

# macOS (avec Homebrew)
brew install aircrack-ng
```

2. Dépendances Python

```bash
# Installer les dépendances Python
pip install -r requirements.txt

# Ou manuellement
pip install PySide6 requests
```

3. Vérification

```bash
# Vérifier que les outils sont installés
which airbase-ng
which aireplay-ng
which iwconfig
```

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