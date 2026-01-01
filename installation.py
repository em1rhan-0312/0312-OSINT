import subprocess
import sys
import os

def print_status(message):
    print(f"[*] {message}")

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error executing: {command}\n{e}")
        sys.exit(1)

def main():
    print("\n--- 0312-OSINT Termux (Android) Installer ---\n")
    
    print_status("Updating system packages...")
    run_command("pkg update -y && pkg upgrade -y")


    print_status("Installing build essentials for Termux...")
    run_command("pkg install -y python clang make libffi-dev openssl-dev git")

    print_status("Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")

    if os.path.exists("requirements.txt"):
        print_status("Installing dependencies from requirements.txt...")
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
    else:
        print("[!] requirements.txt not found! Installing basic dependencies...")
        run_command(f"{sys.executable} -m pip install requests beautifulsoup4 colorama prettytable")

    print("\n" + "="*40)
    print("[+] Installation completed successfully!")
    print("[+] You can now start the tool by running: python main.py")
    print("="*40 + "\n")

    # Automatically launch the tool
    launch = input("Would you like to start the tool now? (y/n): ").lower()
    if launch == 'y':
        print_status("Launching 0312-OSINT...")
        os.system(f"{sys.executable} main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Installation cancelled by user.")
        sys.exit(0)
