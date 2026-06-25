import sys
import os
import signal
import argparse
from pathlib import Path

try:
    import readline
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import display as disp
from modules import config_loader as cfg
from modules.instagram import InstagramOSINT, ScraperOSINT
from modules.phone import PhoneOSINT
from modules.email_osint import EmailOSINT
from modules.username_search import UsernameSearch
from modules.web_osint import WebOSINT
from modules.ddos_module import DDoSAttack, run_ddos
from modules.ddos_menu import ddos_interactive_menu
from modules.sms_module import SMSBomber, run_sms_bomb
from modules.sms_menu import sms_interactive_menu
from modules.extra_osint import (
    PortScanner, SubdomainFinder, TechDetect,
    HashLookup, SiteCopier, AdminPanelFinder
)

IG = None
CONNECTED = False

COMMANDS = {}

ASCII_ART = r"""
  /$$$$$$   /$$$$$$    /$$    /$$$$$$          /$$$$$$   /$$$$$$  /$$$$$$ /$$   /$$ /$$$$$$$$
 /$$$_  $$ /$$__  $$ /$$$$   /$$__  $$        /$$__  $$ /$$__  $$|_  $$_/| $$$ | $$|__  $$__/
| $$$$\ $$|__/  \ $$|_  $$  |__/  \ $$       | $$  \ $$| $$  \__/  | $$  | $$$$| $$   | $$   
| $$ $$ $$   /$$$$$/  | $$    /$$$$$$//$$$$$$| $$  | $$|  $$$$$$   | $$  | $$ $$ $$   | $$   
| $$\ $$$$  |___  $$  | $$   /$$____/|______/| $$  | $$ \____  $$  | $$  | $$  $$$$   | $$   
| $$ \ $$$ /$$  \ $$  | $$  | $$             | $$  | $$ /$$  \ $$  | $$  | $$\  $$$   | $$   
|  $$$$$$/|  $$$$$$/ /$$$$$$| $$$$$$$$       |  $$$$$$/|  $$$$$$/ /$$$$$$| $$ \  $$   | $$   
 \______/  \______/ |______/|________/        \______/  \______/ |______/|__/  \__/   |__/  
"""

def print_logo():
    for line in ASCII_ART.split("\n"):
        if line.strip():
            disp.pout(line + "\n", disp.GREEN)
    disp.pout("=" * 40 + "\n", disp.CYAN)
    disp.pout("        Made By emirhan.0312\n", disp.BLUE, bold=True)
    disp.pout("=" * 40 + "\n", disp.CYAN)


def signal_handler(sig, frame):
    disp.pout("\n\nGoodbye!\n", disp.RED, bold=True)
    sys.exit(0)


def print_help():
    disp.pheader("AVAILABLE MODULES")
    for cmd, (desc, _) in sorted(COMMANDS.items()):
        disp.pout(f"  {cmd.ljust(22)}", disp.YELLOW)
        disp.pout(f"{desc}\n")
    disp.pout("\n  help/h             Show this help\n", disp.WHITE)
    disp.pout("  quit/exit/q        Exit 0312-OSINT\n", disp.WHITE)
    disp.pout("  clear/cls          Clear screen\n", disp.WHITE)


def print_menu():
    disp.pout("  [1]  Instagram OSINT\n", disp.GREEN)
    disp.pout("  [2]  Phone Number Lookup\n", disp.GREEN)
    disp.pout("  [3]  Email Lookup\n", disp.GREEN)
    disp.pout("  [4]  Username Search (25+ platforms)\n", disp.GREEN)
    disp.pout("  [5]  IP / Domain Lookup\n", disp.GREEN)
    disp.pout("  [6]  DDoS Attack Menu\n", disp.RED)
    disp.pout("  [7]  SMS Bomber Menu\n", disp.RED)
    disp.pout("  [8]  Port Scanner\n", disp.CYAN)
    disp.pout("  [9]  Subdomain Discovery\n", disp.CYAN)
    disp.pout("  [10] Site Tech Detection\n", disp.CYAN)
    disp.pout("  [11] Hash Lookup / Crack\n", disp.CYAN)
    disp.pout("  [12] Admin Panel Finder\n", disp.CYAN)
    disp.pout("  [13] Site File Copier\n", disp.CYAN)
    disp.pout("  [14] Help / All Commands\n", disp.YELLOW)
    disp.pout("  [15] Clear Screen\n", disp.WHITE)
    disp.pout("  [0]  Exit\n\n", disp.RED)


def cmd_help():
    print_help()


def cmd_quit():
    disp.pout("\nGoodbye!\n", disp.RED, bold=True)
    sys.exit(0)


def cmd_clear():
    os.system("cls" if os.name == "nt" else "clear")


def cmd_instagram_info(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            disp.perror("Instagram connection failed")
            return
        CONNECTED = True

    if not target:
        target = disp.pin("Target username: ", disp.YELLOW)
    if target:
        if IG.set_target(target):
            IG.get_info()


def cmd_instagram_followers(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_followers()


def cmd_instagram_following(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_following()


def cmd_instagram_analysis(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_follow_analysis()
        IG.get_posts_analysis()


def cmd_instagram_photos(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_photos()


def cmd_instagram_stories(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_stories()


def cmd_instagram_hashtags(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_hashtags()


def cmd_instagram_locations(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_locations()


def cmd_instagram_comments(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_comments()


def cmd_instagram_mutual():
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_mutual_followers_with()


def cmd_instagram_tagged(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_tagged()


def cmd_instagram_emails(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_emails()


def cmd_instagram_phones(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_phone_numbers()


def cmd_instagram_propic(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.get_profile_pic()


def cmd_instagram_report(target=None):
    global IG, CONNECTED
    if not CONNECTED:
        IG = InstagramOSINT()
        if not IG.login():
            return
        CONNECTED = True
    target = target or IG.target or disp.pin("Target username: ", disp.YELLOW)
    if target and IG.set_target(target):
        IG.generate_report()


def cmd_scrape(target=None):
    if not target:
        target = disp.pin("Target username: ", disp.YELLOW)
    if target:
        s = ScraperOSINT()
        if s.set_target(target):
            s.get_info()
            if not s.is_private:
                s.get_posts(limit=5)
            yn = disp.pin("Download profile picture? [y/N]: ", disp.YELLOW)
            if yn.lower() == "y":
                s.download_profile_pic()


def cmd_phone(phone=None):
    if not phone:
        phone = disp.pin("Phone number (with country code, e.g. +905551234567): ", disp.YELLOW)
    if phone:
        p = PhoneOSINT()
        p.lookup(phone)


def cmd_email(email=None):
    if not email:
        email = disp.pin("Email address: ", disp.YELLOW)
    if email:
        e = EmailOSINT()
        e.lookup(email)


def cmd_username(username=None):
    if not username:
        username = disp.pin("Username to search: ", disp.YELLOW)
    if username:
        u = UsernameSearch()
        u.search(username)


def cmd_ip(ip=None):
    if not ip:
        ip = disp.pin("IP address: ", disp.YELLOW)
    if ip:
        w = WebOSINT()
        w.lookup_ip(ip)


def cmd_domain(domain=None):
    if not domain:
        domain = disp.pin("Domain name: ", disp.YELLOW)
    if domain:
        w = WebOSINT()
        w.lookup_domain(domain)


def cmd_webcheck():
    ip = disp.pin("IP address or Domain: ", disp.YELLOW)
    if not ip:
        return
    w = WebOSINT()
    if ip.replace(".", "").isdigit():
        w.lookup_ip(ip)
    else:
        w.lookup_domain(ip)


def cmd_ddos(target=None, method=None, threads=None, duration=None):
    if not target:
        ddos_interactive_menu()
        return
    if not method:
        m = disp.pin("Method (GET/POST/TCP/UDP/etc): ", disp.YELLOW) or "GET"
    else:
        m = method
    port_input = disp.pin("Port [80]: ", disp.YELLOW)
    try:
        port = int(port_input) if port_input.strip() else None
    except:
        port = None
    if not threads:
        try:
            threads = int(disp.pin("Thread count [50]: ", disp.YELLOW) or "50")
        except:
            threads = 50
    if not duration:
        try:
            duration = int(disp.pin("Duration (seconds) [0=unlimited]: ", disp.YELLOW) or "30")
        except:
            duration = 30

    disp.pinfo(f"\nStarting DDoS attack: {m} -> {target}:{port or 80} ({threads} threads)\n")
    success, msg, stats = run_ddos(target, m, threads, duration, port)
    if success:
        disp.pok(f"Attack finished. Total packets sent: {stats['sent']}")
    else:
        disp.perror(msg)


def cmd_ddos_list():
    disp.pheader("AVAILABLE DDoS METHODS")
    for m in DDoSAttack.METHODS:
        disp.pout(f"  {m}\n", disp.YELLOW)


def cmd_sms_bomb(phone=None, count=None):
    if not phone:
        sms_interactive_menu()
        return
    if not count:
        try:
            count = int(disp.pin("SMS count per service [5]: ", disp.YELLOW) or "5")
        except:
            count = 5

    disp.pout(f"\n[!] Starting SMS bomb to {phone} ({count} rounds)...\n", disp.YELLOW)
    success, msg = run_sms_bomb(phone, count)
    if success:
        disp.pok(msg)
    else:
        disp.perror(msg)


def cmd_sms_services():
    bomber = SMSBomber("0")
    services = bomber.list_services()
    disp.pheader("AVAILABLE SMS SERVICES")
    for s in services:
        disp.pout(f"  {s}\n", disp.GREEN)


def cmd_portscan(target=None):
    if not target:
        target = disp.pin("IP or Domain: ", disp.YELLOW)
    if not target:
        return
    # Resolve domain
    try:
        ip = socket.gethostbyname(target)
    except:
        ip = target
    disp.pout(f"\n[*] Scanning {target} ({ip})...\n", disp.YELLOW)
    scanner = PortScanner(ip)
    results = scanner.scan()
    if results:
        disp.pheader(" OPEN PORTS ")
        for port, service in results:
            disp.pout(f"  {port}/tcp".ljust(20), disp.GREEN)
            disp.pout(f"{service}\n")
    else:
        disp.pout("  No open ports found on common ports.\n", disp.RED)


def cmd_subdomain(domain=None):
    if not domain:
        domain = disp.pin("Domain: ", disp.YELLOW)
    if not domain:
        return
    disp.pout(f"\n[*] Searching subdomains for {domain}...\n", disp.YELLOW)
    finder = SubdomainFinder(domain)
    results = finder.find()
    if results:
        disp.pheader(f" SUBDOMAINS FOUND: {len(results)} ")
        for sub, ip in results[:30]:
            disp.pout(f"  {sub}.{domain}".ljust(35), disp.GREEN)
            disp.pout(f"{ip}\n")
    else:
        disp.pout("  No subdomains found.\n", disp.RED)


def cmd_tech(url=None):
    if not url:
        url = disp.pin("URL: ", disp.YELLOW)
    if not url:
        return
    disp.pout(f"\n[*] Analyzing {url}...\n", disp.YELLOW)
    td = TechDetect(url)
    info = td.detect()
    disp.pheader(" TECHNOLOGY INFO ")
    disp.pout(f"  URL: {info.get('url')}\n", disp.WHITE)
    disp.pout(f"  Status: {info.get('status')}\n", disp.GREEN)
    disp.pout(f"  Server: {info.get('server')}\n", disp.CYAN)
    disp.pout(f"  Size: {info.get('size')} bytes\n", disp.WHITE)
    if info.get("tech"):
        disp.pout("\n  Detected:\n", disp.YELLOW)
        for t in info["tech"]:
            disp.pout(f"    - {t}\n", disp.GREEN)


def cmd_hash(hash_val=None):
    if not hash_val:
        hash_val = disp.pin("Hash: ", disp.YELLOW)
    if not hash_val:
        return
    hl = HashLookup(hash_val)
    ht = hl.identify_type()
    disp.pheader(f" HASH: {ht} ({len(hash_val)} chars) ")
    if ht != "Unknown":
        gen = hl.generate("test", ht.lower())
        disp.pout(f"  'test' -> {gen}\n", disp.WHITE)
    result = hl.crack()
    if result:
        disp.pok(f"  Cracked: {result}")
    else:
        disp.pout("  Not found in online databases.\n", disp.RED)
        disp.pout("  Tip: Try crackstation.net or hashes.com\n", disp.YELLOW)


def cmd_sitecopy(url=None):
    if not url:
        url = disp.pin("URL (https://site.com): ", disp.YELLOW)
    if not url:
        return
    disp.pout(f"\n[*] Copying {url} ...\n", disp.YELLOW)
    sc = SiteCopier(url)
    result = sc.crawl()
    if result.get("files_downloaded", 0) > 0:
        disp.pok(f"Done! {result['files_downloaded']} files saved to {result['output']}")
    else:
        disp.perror("No files downloaded")


def cmd_admin(url=None):
    if not url:
        url = disp.pin("URL (https://site.com): ", disp.YELLOW)
    if not url:
        return
    disp.pout(f"\n[*] Scanning admin panels on {url} ...\n", disp.YELLOW)
    pf = AdminPanelFinder(url)
    results = pf.scan()
    if results:
        disp.pok(f"Found {len(results)} potential admin paths:")
        for r in results:
            msg = f"  {r['path']} ({r['status']})"
            if "redirect" in r:
                msg += f" -> {r['redirect']}"
            if "note" in r:
                msg += f" [{r['note']}]"
            disp.pout(f"{msg}\n", disp.GREEN if r['status'] == 200 else disp.YELLOW)
    else:
        disp.pout("  No admin panels found.\n", disp.RED)


COMMANDS = {
    "help": ("Show this help", cmd_help),
    "h": ("Show this help", cmd_help),
    "quit": ("Exit 0312-OSINT", cmd_quit),
    "exit": ("Exit 0312-OSINT", cmd_quit),
    "q": ("Exit 0312-OSINT", cmd_quit),
    "clear": ("Clear screen", cmd_clear),
    "cls": ("Clear screen", cmd_clear),

    "email": ("Email OSINT lookup", cmd_email),
    "phone": ("Phone number OSINT lookup", cmd_phone),
    "username": ("Cross-platform username search (25+ sites)", cmd_username),
    "ip": ("IP address geolocation & DNS lookup", cmd_ip),
    "domain": ("Domain WHOIS & DNS lookup", cmd_domain),
    "web": ("IP/Domain combined lookup", cmd_webcheck),

    "scrape": ("Instagram: scrape public profile (no login)", lambda: cmd_scrape(None)),
    "ig":     ("Instagram: show target info (login required)", lambda: cmd_instagram_info(None)),
    "info":   ("Instagram: show target info", lambda: cmd_instagram_info(None)),
    "followers":  ("Instagram: get followers", lambda: cmd_instagram_followers(None)),
    "following":  ("Instagram: get following", lambda: cmd_instagram_following(None)),
    "analysis":   ("Instagram: follow analysis + post analysis", lambda: cmd_instagram_analysis(None)),
    "photos":     ("Instagram: download photos", lambda: cmd_instagram_photos(None)),
    "stories":    ("Instagram: download stories", lambda: cmd_instagram_stories(None)),
    "hashtags":   ("Instagram: hashtag analysis", lambda: cmd_instagram_hashtags(None)),
    "locations":  ("Instagram: geolocation extraction", lambda: cmd_instagram_locations(None)),
    "comments":   ("Instagram: extract all comments", lambda: cmd_instagram_comments(None)),
    "mutual":     ("Instagram: mutual followers analysis", cmd_instagram_mutual),
    "tagged":     ("Instagram: who tagged target", lambda: cmd_instagram_tagged(None)),
    "igemail":    ("Instagram: email scraping from followers", lambda: cmd_instagram_emails(None)),
    "igphone":    ("Instagram: phone scraping from followers", lambda: cmd_instagram_phones(None)),
    "propic":     ("Instagram: download profile picture", lambda: cmd_instagram_propic(None)),
    "report":     ("Instagram: generate HTML+JSON report", lambda: cmd_instagram_report(None)),

    "ddos":       ("DDoS interactive menu (Layer7/Layer4)", lambda: cmd_ddos(None, None, None, None)),
    "ddos-list":  ("List available DDoS methods", cmd_ddos_list),
    "sms":        ("SMS bomber interactive menu", lambda: cmd_sms_bomb(None, None)),
    "sms-list":   ("List available SMS services", cmd_sms_services),
    "portscan":   ("Scan open ports on IP/domain", lambda: cmd_portscan(None)),
    "subdomain":  ("Discover subdomains of a domain", lambda: cmd_subdomain(None)),
    "tech":       ("Detect website technologies", lambda: cmd_tech(None)),
    "hash":       ("Identify and crack hashes", lambda: cmd_hash(None)),
    "admin":      ("Find admin/panel login pages", lambda: cmd_admin(None)),
    "sitecopy":   ("Download website files (clone)", lambda: cmd_sitecopy(None)),
    "menu":       ("Show numbered main menu", print_menu),
}


def completer(text, state):
    options = [c for c in COMMANDS if c.startswith(text)]
    return options[state] if state < len(options) else None


def interactive_mode():
    signal.signal(signal.SIGINT, signal_handler)

    if os.name == "nt":
        try:
            import pyreadline
            pyreadline.Readline().parse_and_bind("tab: complete")
            pyreadline.Readline().set_completer(completer)
        except ImportError:
            pass
    else:
        try:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(completer)
        except ImportError:
            pass

    print_logo()
    print_menu()

    while True:
        try:
            signal.signal(signal.SIGINT, signal_handler)
            disp.pout("0312-OSINT> ", disp.CYAN, bold=True)
            raw = input()

            parts = raw.strip().split()
            if not parts:
                continue

            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            if cmd in COMMANDS:
                COMMANDS[cmd][1]()
            elif cmd == "target" and args:
                IG = InstagramOSINT()
                if IG.login():
                    CONNECTED = True
                    IG.set_target(args[0])
            elif cmd.isdigit():
                num = int(cmd)
                if num == 1:
                    cmd_instagram_info(None)
                elif num == 2:
                    cmd_phone(None)
                elif num == 3:
                    cmd_email(None)
                elif num == 4:
                    cmd_username(None)
                elif num == 5:
                    cmd_webcheck()
                elif num == 6:
                    cmd_ddos(None, None, None, None)
                elif num == 7:
                    cmd_sms_bomb(None, None)
                elif num == 8:
                    cmd_portscan(None)
                elif num == 9:
                    cmd_subdomain(None)
                elif num == 10:
                    cmd_tech(None)
                elif num == 11:
                    cmd_hash(None)
                elif num == 12:
                    cmd_admin(None)
                elif num == 13:
                    cmd_sitecopy(None)
                elif num == 14:
                    print_help()
                elif num == 15:
                    cmd_clear()
                    print_logo()
                    print_menu()
                elif num == 0:
                    cmd_quit()
            else:
                disp.perror(f"Unknown command: {cmd}")

        except KeyboardInterrupt:
            disp.pout("\n")
            continue
        except EOFError:
            cmd_quit()
        except Exception as e:
            disp.perror(f"Error: {e}")


def single_command_mode(cmd_str, args):
    cmd = cmd_str.lower()
    if cmd in COMMANDS:
        if cmd in ("scrape", "ig", "info", "followers", "following", "analysis", "photos",
                   "stories", "hashtags", "locations", "comments", "tagged",
                   "igemail", "igphone", "propic", "report"):
            target = args[0] if args else None
            if cmd == "scrape":
                cmd_scrape(target)
            elif cmd == "ig" or cmd == "info":
                cmd_instagram_info(target)
            elif cmd == "followers":
                cmd_instagram_followers(target)
            elif cmd == "following":
                cmd_instagram_following(target)
            elif cmd == "analysis":
                cmd_instagram_analysis(target)
            elif cmd == "photos":
                cmd_instagram_photos(target)
            elif cmd == "stories":
                cmd_instagram_stories(target)
            elif cmd == "hashtags":
                cmd_instagram_hashtags(target)
            elif cmd == "locations":
                cmd_instagram_locations(target)
            elif cmd == "comments":
                cmd_instagram_comments(target)
            elif cmd == "tagged":
                cmd_instagram_tagged(target)
            elif cmd == "igemail":
                cmd_instagram_emails(target)
            elif cmd == "igphone":
                cmd_instagram_phones(target)
            elif cmd == "propic":
                cmd_instagram_propic(target)
            elif cmd == "report":
                cmd_instagram_report(target)
        elif cmd in ("email", "phone", "username", "ip", "domain", "web"):
            arg_val = args[0] if args else None
            if cmd == "email":
                cmd_email(arg_val)
            elif cmd == "phone":
                cmd_phone(arg_val)
            elif cmd == "username":
                cmd_username(arg_val)
            elif cmd == "ip":
                cmd_ip(arg_val)
            elif cmd == "domain":
                cmd_domain(arg_val)
            elif cmd == "web":
                cmd_webcheck()
        elif cmd == "mutual":
            cmd_instagram_mutual()
        elif cmd == "ddos":
            target = args[0] if len(args) > 0 else None
            method = args[1] if len(args) > 1 else None
            threads = int(args[2]) if len(args) > 2 and args[2].isdigit() else None
            duration = int(args[3]) if len(args) > 3 and args[3].isdigit() else None
            cmd_ddos(target, method, threads, duration)
        elif cmd == "ddos-list":
            cmd_ddos_list()
        elif cmd == "sms":
            phone = args[0] if args else None
            count = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
            cmd_sms_bomb(phone, count)
        elif cmd == "sms-list":
            cmd_sms_services()
        elif cmd == "menu":
            print_menu()
        elif cmd in ("portscan", "subdomain", "tech", "hash", "admin", "sitecopy"):
            arg_val = args[0] if args else None
            if cmd == "portscan":
                cmd_portscan(arg_val)
            elif cmd == "subdomain":
                cmd_subdomain(arg_val)
            elif cmd == "tech":
                cmd_tech(arg_val)
            elif cmd == "hash":
                cmd_hash(arg_val)
            elif cmd == "admin":
                cmd_admin(arg_val)
            elif cmd == "sitecopy":
                cmd_sitecopy(arg_val)
        elif cmd in ("help", "h"):
            print_help()
    else:
        disp.perror(f"Unknown command: {cmd}")


def main():
    parser = argparse.ArgumentParser(
        description="0312-OSINT v2.0 - Multi-Platform OSINT Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  0312-OSINT                          Interactive mode
  0312-OSINT ig john_doe              Instagram info for john_doe
  0312-OSINT followers john_doe       Get john_doe's followers
  0312-OSINT phone +905551234567      Phone number lookup
  0312-OSINT email user@example.com   Email lookup
  0312-OSINT username john            25+ platform username search
  0312-OSINT ip 8.8.8.8              IP geolocation
  0312-OSINT domain example.com       Domain WHOIS lookup
  0312-OSINT ddos http://target.com   DDoS attack with args
  0312-OSINT ddos                     DDoS interactive menu
  0312-OSINT ddos-list                List DDoS methods
  0312-OSINT sms 905551234567         SMS bomber with args
  0312-OSINT sms                      SMS bomber interactive menu
  0312-OSINT portscan 8.8.8.8         Port scanner
  0312-OSINT subdomain example.com    Subdomain discovery
  0312-OSINT tech example.com         Technology detection
   0312-OSINT hash <md5/sha1/sha256>   Hash lookup / crack
   0312-OSINT admin example.com        Find admin panels
   0312-OSINT sitecopy example.com     Download website files
   0312-OSINT menu                     Show numbered main menu
        """
    )
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("arg", nargs="*", help="Command arguments")

    args = parser.parse_args()

    if args.command:
        single_command_mode(args.command, args.arg)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
