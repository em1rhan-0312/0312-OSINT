"""
0312-OSINT Extra Modules
  - Port Scanner
  - Subdomain Discovery
  - Site Technology Detection
  - Hash Lookup
  - Site Copier (web file downloader)
  - Admin Panel Finder
"""
import os
import re
import socket
import hashlib
import requests
import json
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


class PortScanner:
    COMMON_PORTS = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
        443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
        1433: "MSSQL", 1521: "Oracle", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt",
        8443: "HTTPS-Alt", 27017: "MongoDB"
    }

    def __init__(self, target, ports=None, timeout=2):
        self.target = target
        self.timeout = timeout
        self.ports = ports or list(self.COMMON_PORTS.keys())

    def scan(self, max_workers=50):
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._check_port, p): p for p in self.ports}
            for future in as_completed(futures):
                port, service, status = future.result()
                if status:
                    results.append((port, service))
        return sorted(results, key=lambda x: x[0])

    def _check_port(self, port):
        service = self.COMMON_PORTS.get(port, "Unknown")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            result = s.connect_ex((self.target, port))
            s.close()
            return (port, service, result == 0)
        except:
            return (port, service, False)


class SubdomainFinder:
    def __init__(self, domain):
        self.domain = domain

    def find(self, wordlist=None):
        if wordlist is None:
            wordlist = ["www", "mail", "ftp", "admin", "blog", "shop", "api",
                        "dev", "test", "cdn", "m", "mobile", "webmail", "smtp",
                        "pop", "ns1", "ns2", "vpn", "secure", "portal",
                        "support", "help", "forum", "news", "wiki", "app",
                        "status", "docs"]
        found = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self._check, sub): sub for sub in wordlist}
            for future in as_completed(futures):
                sub, ip = future.result()
                if ip:
                    found.append((sub, ip))
        return found

    def _check(self, sub):
        try:
            ip = socket.gethostbyname(f"{sub}.{self.domain}")
            return (sub, ip)
        except:
            return (sub, None)


class TechDetect:
    def __init__(self, url):
        self.url = url if url.startswith(("http://", "https://")) else f"https://{url}"

    def detect(self):
        info = {"url": self.url, "server": None, "tech": []}
        try:
            r = requests.get(self.url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            })
            headers = r.headers
            if "Server" in headers:
                info["server"] = headers["Server"]
            if "X-Powered-By" in headers:
                info["tech"].append(headers["X-Powered-By"])
            ct = headers.get("Content-Type", "")
            if "charset=" in ct:
                info["tech"].append(f"Charset: {ct.split('charset=')[1].split(';')[0]}")
            if "Set-Cookie" in headers:
                for c in headers.get("Set-Cookie", "").split(","):
                    if "=" in c:
                        name = c.split("=")[0].strip()
                        info["tech"].append(f"Cookie: {name}")
            text = r.text.lower()
            if "wp-content" in text or "wp-includes" in text:
                info["tech"].append("WordPress")
            if "joomla" in text:
                info["tech"].append("Joomla")
            if "drupal" in text:
                info["tech"].append("Drupal")
            if "shopify" in text:
                info["tech"].append("Shopify")
            if "cloudflare" in text or "cf-ray" in headers:
                info["tech"].append("CloudFlare")
            if "nginx" in headers.get("Server", "").lower():
                info["tech"].append("Nginx")
            if "apache" in headers.get("Server", "").lower():
                info["tech"].append("Apache")
            if "openresty" in headers.get("Server", "").lower():
                info["tech"].append("OpenResty")
            info["status"] = r.status_code
            info["size"] = len(r.content)
        except Exception as e:
            info["error"] = str(e)
        return info


class HashLookup:
    API_URLS = {
        "md5": "https://md5decrypt.net/Api/api.php?hash={}&hash_type=md5&email=test@test.com&code=test",
        "sha1": "https://md5decrypt.net/Api/api.php?hash={}&hash_type=sha1&email=test@test.com&code=test",
        "sha256": "https://md5decrypt.net/Api/api.php?hash={}&hash_type=sha256&email=test@test.com&code=test",
    }

    def __init__(self, hash_value):
        self.hash_value = hash_value.strip().lower()

    def identify_type(self):
        length = len(self.hash_value)
        if length == 32:
            return "MD5"
        elif length == 40:
            return "SHA1"
        elif length == 64:
            return "SHA256"
        elif length == 128:
            return "SHA512"
        elif length == 16:
            return "MySQL3" if all(c in "0123456789abcdef" for c in self.hash_value) else "Unknown"
        return "Unknown"

    def crack(self):
        ht = self.identify_type().lower()
        if ht in self.API_URLS:
            try:
                r = requests.get(self.API_URLS[ht].format(self.hash_value), timeout=10)
                if r.text and "ERROR" not in r.text:
                    return r.text.strip()
            except:
                pass
        return None

    @staticmethod
    def generate(text, algo="md5"):
        h = hashlib.new(algo)
        h.update(text.encode())
        return h.hexdigest()


class AdminPanelFinder:
    PATHS = [
        "admin", "administrator", "adminpanel", "panel", "yonetim", "login",
        "giris", "admin/login", "admin/login.php", "admin/index.php",
        "admin/admin.php", "administrator/login", "admin/panel",
        "admin/dashboard", "dashboard", "wp-admin", "admin.aspx",
        "cp", "controlpanel", "admincp", "admin/controlpanel",
        "admin/index.html", "admin1", "admin2", "siteadmin",
        "adminarea", "admin/pages", "admin/home", "admin/cms",
        "admin/manage", "admin/user", "admin/users",
        "yonetim/panel", "yonetim/giris", "panel/admin",
        "panel/login", "giris-yap", "kullanici-girisi",
        "moderator", "webadmin", "sysadmin", "admin/account",
        "backend", "admin/backend", "management", "admin/management",
        "login.aspx", "signin", "sign-in", "user/login",
    ]

    def __init__(self, url):
        self.base = url.rstrip("/") if url.startswith(("http://", "https://")) else f"https://{url}"

    def scan(self, timeout=5):
        found = []
        for path in self.PATHS:
            full = f"{self.base}/{path}"
            try:
                r = requests.get(full, timeout=timeout, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
                })
                if r.status_code in (200, 201, 202, 204):
                    found.append({"path": full, "status": r.status_code, "size": len(r.content)})
                elif r.status_code in (301, 302, 303, 307, 308):
                    found.append({"path": full, "status": r.status_code, "redirect": r.headers.get("Location", "")})
                elif r.status_code == 401:
                    found.append({"path": full, "status": r.status_code, "note": "Authorization required"})
                elif r.status_code == 403:
                    found.append({"path": full, "status": r.status_code, "note": "Forbidden"})
            except:
                pass
        return found


class SiteCopier:
    def __init__(self, url, output_dir="output"):
        self.url = url if url.startswith(("http://", "https://")) else f"https://{url}"
        self.output_dir = output_dir
        self.visited = set()
        self.queue = []
        self.downloaded = 0
        self.domain = urlparse(self.url).netloc

    def _save_file(self, url, content, is_binary=False):
        parsed = urlparse(url)
        path = parsed.path or "/index.html"
        if path.endswith("/"):
            path += "index.html"
        local = os.path.join(self.output_dir, self.domain, path.lstrip("/"))
        os.makedirs(os.path.dirname(local), exist_ok=True)
        mode = "wb" if is_binary else "w"
        encoding = None if is_binary else "utf-8"
        with open(local, mode, encoding=encoding) as f:
            f.write(content)
        return local

    def _is_same_domain(self, link):
        try:
            return urlparse(link).netloc in ("", self.domain)
        except:
            return False

    def _extract_links(self, html, base):
        links = []
        for tag, attr in [("a", "href"), ("link", "href"), ("script", "src"),
                          ("img", "src"), ("source", "src"), ("video", "src")]:
            pattern = re.compile(f'<{tag}[^>]*{attr}=["\'](.*?)["\']', re.IGNORECASE)
            for m in pattern.finditer(html):
                link = m.group(1).split("#")[0].split("?")[0]
                if link and not link.startswith(("data:", "javascript:", "mailto:", "#")):
                    links.append(requests.compat.urljoin(base, link))
        return links

    def crawl(self):
        self.queue.append(self.url)
        while self.queue:
            current = self.queue.pop(0)
            if current in self.visited:
                continue
            self.visited.add(current)
            try:
                r = requests.get(current, timeout=15, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
                })
                ct = r.headers.get("Content-Type", "")
                if "text/html" in ct:
                    html = r.text
                    self._save_file(current, html)
                    self.downloaded += 1
                    for link in self._extract_links(html, current):
                        if self._is_same_domain(link) and link not in self.visited:
                            self.queue.append(link)
                else:
                    self._save_file(current, r.content, is_binary=True)
                    self.downloaded += 1
            except:
                pass
        return {
            "pages_crawled": len(self.visited),
            "files_downloaded": self.downloaded,
            "output": os.path.join(self.output_dir, self.domain)
        }
