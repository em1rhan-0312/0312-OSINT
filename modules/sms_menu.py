"""
0312-OSINT SMS Bomber Interactive Menu
"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules import display as disp
from modules.sms_module import SMSBomber


def print_sms_banner():
    os.system("cls" if os.name == "nt" else "clear")
    disp.pout("""
   ███████╗███╗   ███╗███████╗
   ██╔════╝████╗ ████║██╔════╝
   ███████╗██╔████╔██║███████╗
   ╚════██║██║╚██╔╝██║╚════██║
   ███████║██║ ╚═╝ ██║███████║
   ╚══════╝╚═╝     ╚═╝╚══════╝
   0312-OSINT SMS Bomber
""", disp.CYAN)


def sms_interactive_menu():
    while True:
        print_sms_banner()
        
        # Get available services count
        try:
            test_bomber = SMSBomber("0")
            services = test_bomber.list_services()
            svc_count = len(services)
        except:
            svc_count = 0
        
        disp.pheader(f" AVAILABLE SERVICES: {svc_count} ")
        disp.pout("\n  [1] SMS Send (Normal)\n", disp.GREEN)
        disp.pout("  [2] SMS Send (Turbo - Multi Thread)\n", disp.GREEN)
        disp.pout("  [3] List All Services\n", disp.YELLOW)
        disp.pout("  [M] Main Menu\n", disp.WHITE)
        disp.pout("  [Q] Quit\n\n", disp.RED)
        
        choice = disp.pin("Select: ", disp.YELLOW).strip().upper()
        
        if choice == "Q":
            sys.exit(0)
        elif choice == "M":
            return
        elif choice == "3":
            print_sms_banner()
            disp.pheader(f" SMS SERVICES ({svc_count}) ")
            bomber = SMSBomber("0")
            for s in bomber.list_services():
                disp.pout(f"  {s}\n", disp.GREEN)
            disp.pin("\nPress Enter to continue...", disp.YELLOW)
            continue
        elif choice in ("1", "2"):
            sms_send_menu(choice == "2")


def sms_send_menu(turbo=False):
    print_sms_banner()
    
    phone = disp.pin("Phone (05XX...): ", disp.YELLOW)
    if not phone or not phone.isdigit() or len(phone) != 11:
        disp.perror("Invalid phone number. Must be 11 digits.")
        disp.pin("\nPress Enter...", disp.YELLOW)
        return
    
    mail = disp.pin("Email (optional): ", disp.YELLOW)
    
    bomber = SMSBomber(phone)
    
    if turbo:
        try:
            count = int(disp.pin("SMS per service [5]: ", disp.YELLOW) or "5")
        except:
            count = 5
        
        disp.pout(f"\n[*] Turbo bombing {phone} with {count} SMS per service...\n", disp.GREEN)
        success, msg = bomber.bomb(count, delay=0.3)
    else:
        disp.pout(f"\n[*] Normal bombing {phone}...\n", disp.GREEN)
        success, msg = bomber.bomb(3, delay=1)
    
    if success:
        disp.pok(msg)
    else:
        disp.perror(msg)
    
    disp.pin("\nPress Enter to continue...", disp.YELLOW)
