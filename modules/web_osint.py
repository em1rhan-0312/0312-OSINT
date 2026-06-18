import json
import urllib.request
import urllib.parse
import socket

from . import config_loader as cfg
from . import display as disp
from .report import ReportEngine

class WebOSINT:
    def __init__(self):
        self.report = ReportEngine("output", "web_lookup")

    def lookup_ip(self, ip):
        disp.pheader(f"IP LOOKUP: {ip}")

        results = {"ip": ip, "sources": {}}

        self._check_ipinfo(ip, results)
        self._dns_lookup(ip, results)
        self._format_output("IP", results)

        self.report.add("ip_lookup", results)
        return results

    def lookup_domain(self, domain):
        disp.pheader(f"DOMAIN LOOKUP: {domain}")

        results = {"domain": domain, "sources": {}}

        self._dns_lookup(domain, results)
        self._whois_lookup(domain, results)
        self._format_output("Domain", results)

        self.report.add("domain_lookup", results)
        return results

    def _check_ipinfo(self, ip, results):
        key = cfg.get_api_key("ipinfo_key")
        url = f"https://ipinfo.io/{ip}/json"
        if key:
            url += f"?token={key}"

        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
            results["sources"]["ipinfo"] = {
                "city": data.get("city", ""),
                "region": data.get("region", ""),
                "country": data.get("country", ""),
                "loc": data.get("loc", ""),
                "org": data.get("org", ""),
                "postal": data.get("postal", ""),
                "timezone": data.get("timezone", ""),
            }
            disp.pout(f"  [+] IPinfo: {data.get('city', '?')}, {data.get('region', '?')}, {data.get('country', '?')}\n", disp.GREEN)
        except Exception as e:
            disp.pout(f"  [!] IPinfo error: {e}\n", disp.RED)

    def _dns_lookup(self, target, results):
        try:
            ip = socket.gethostbyname(target)
            results["sources"]["dns"] = {"resolved_ip": ip}
            disp.pout(f"  [+] DNS: {target} -> {ip}\n", disp.GREEN)

            try:
                host = socket.gethostbyaddr(ip)
                results["sources"]["dns"]["reverse"] = host[0]
                disp.pout(f"  [+] Reverse DNS: {host[0]}\n", disp.GREEN)
            except:
                pass
        except Exception as e:
            disp.pout(f"  [!] DNS error: {e}\n", disp.RED)

    def _whois_lookup(self, domain, results):
        try:
            import subprocess
            result = subprocess.run(
                ["whois", domain],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                whois_info = {}
                for line in lines[:30]:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        k = k.strip()
                        v = v.strip()
                        if v and k.lower() in [
                            "registrar", "creation date", "expiry date",
                            "registrant name", "registrant organization",
                            "registrant email", "name server", "admin email"
                        ]:
                            whois_info[k] = v
                if whois_info:
                    results["sources"]["whois"] = whois_info
                    for k, v in whois_info.items():
                        disp.pout(f"  [+] WHOIS {k}: {v}\n", disp.GREEN)
            else:
                disp.pout("  [!] WHOIS command not available\n", disp.YELLOW)
        except Exception as e:
            disp.pout(f"  [!] WHOIS error: {e}\n", disp.YELLOW)

    def _format_output(self, label, results):
        disp.psep()
        disp.pout(f"  {label}: {results.get(label.lower())}\n", disp.CYAN, bold=True)
        for source, data in results["sources"].items():
            disp.pout(f"  [{source}]\n", disp.BLUE, bold=True)
            for k, v in data.items():
                disp.pout(f"    {k}: {v}\n")
