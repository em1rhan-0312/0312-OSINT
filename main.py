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

IG = None
CONNECTED = False

ASCII_ART = r"""
 .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. |
| |     ____     | || |    ______    | || |     __       | || |    _____     | |
| |   .'    '.   | || |   / ____ `.  | || |    /  |      | || |   / ___ `.   | |
| |  |  .--.  |  | || |   `'  __) |  | || |    `| |      | || |  |_/___) |   | |
| |  | |    | |  | || |   _  |__ '.  | || |     | |      | || |   .'____.'   | |
| |  |  `--'  |  | || |  | \____) |  | || |    _| |_     | || |  / /____     | |
| |   '.____.'   | || |   \______.'  | || |   |_____|    | || |  |_______|   | |
| |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------' 
"""

COMMANDS = {}


def signal_handler(sig, frame):
    disp.pout("\n\nGoodbye!\n", disp.RED, bold=True)
    sys.exit(0)


BANNER = """
+====================================================================+
|       0312-OSINT v2.0 - Multi-Platform OSINT Framework             |
|       Instagram | Phone | Email | Username | IP | Domain           |
+====================================================================+
"""

def print_logo():
    for line in ASCII_ART.split("\n"):
        if line.strip():
            disp.pout(line + "\n", disp.GREEN)
    for line in BANNER.split("\n"):
        if line.strip():
            disp.pout(line + "\n", disp.CYAN)


def print_help():
    disp.pheader("AVAILABLE MODULES")
    for cmd, (desc, _) in sorted(COMMANDS.items()):
        disp.pout(f"  {cmd.ljust(22)}", disp.YELLOW)
        disp.pout(f"{desc}\n")
    disp.pout("\n  help/h             Show this help\n", disp.WHITE)
    disp.pout("  quit/exit/q        Exit 0312-OSINT\n", disp.WHITE)
    disp.pout("  clear/cls          Clear screen\n", disp.WHITE)


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

    while True:
        try:
            signal.signal(signal.SIGINT, signal_handler)
            disp.pout("\n0312-OSINT> ", disp.CYAN, bold=True)
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
