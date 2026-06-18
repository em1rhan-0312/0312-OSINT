import json
import urllib.request
import urllib.parse

from . import config_loader as cfg
from . import display as disp
from .report import ReportEngine

class EmailOSINT:
    def __init__(self):
        self.report = ReportEngine("output", "email_lookup")

    def lookup(self, email):
        disp.pheader(f"EMAIL LOOKUP: {email}")

        results = {
            "email": email,
            "sources": {}
        }

        self._check_hunterio(email, results)
        self._check_holehe(email, results)
        self._check_gravatar(email, results)
        self._format_output(results)

        self.report.add("email_lookup", results)
        return results

    def _check_hunterio(self, email, results):
        key = cfg.get_api_key("hunterio_key")
        if not key:
            disp.pout("  [*] hunter.io: no API key\n", disp.YELLOW)
            return

        try:
            domain = email.split("@")[1] if "@" in email else ""
            url = f"https://api.hunter.io/v2/email-verifier?api_key={key}&email={email}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())

            d = data.get("data", {})
            results["sources"]["hunterio"] = {
                "status": d.get("status", ""),
                "smtp_check": d.get("smtp_check"),
                "score": d.get("score"),
                "disposable": d.get("disposable"),
                "webmail": d.get("webmail"),
            }
            status = d.get("status", "unknown")
            color = disp.GREEN if status == "valid" else disp.RED
            disp.pout(f"  [+] hunter.io: {status} (score: {d.get('score')})\n", color)
        except Exception as e:
            disp.pout(f"  [!] hunter.io error: {e}\n", disp.RED)

    def _check_gravatar(self, email, results):
        import hashlib
        h = hashlib.md5(email.lower().encode()).hexdigest()
        url = f"https://en.gravatar.com/{h}.json"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
            entries = data.get("entry", [])
            if entries:
                entry = entries[0]
                results["sources"]["gravatar"] = {
                    "display_name": entry.get("displayName", ""),
                    "profile_url": entry.get("profileUrl", ""),
                    "thumbnail": entry.get("thumbnailUrl", ""),
                    "about": entry.get("about", ""),
                }
                disp.pout(f"  [+] Gravatar profile found: {entry.get('displayName')}\n", disp.GREEN)
        except urllib.request.HTTPError as e:
            if e.code == 404:
                disp.pout("  [-] No Gravatar profile\n", disp.YELLOW)
            else:
                disp.pout(f"  [!] Gravatar error: {e}\n", disp.RED)
        except Exception as e:
            pass

    def _check_holehe(self, email, results):
        disp.pout("  [*] holehe: pip install holehe for extended checking\n", disp.YELLOW)

    def _format_output(self, results):
        disp.psep()
        disp.pout(f"  Email: {results['email']}\n", disp.CYAN, bold=True)
        for source, data in results["sources"].items():
            disp.pout(f"  [{source}]\n", disp.BLUE, bold=True)
            for k, v in data.items():
                disp.pout(f"    {k}: {v}\n")
