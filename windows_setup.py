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
        return False
    return True

def main():
    print("\n--- 0312-OSINT Windows Quick Setup ---\n")
    
    # 1. Upgrade pip
    print_status("Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")

    # 2. Install requirements
    if os.path.exists("requirements.txt"):
        print_status("Installing dependencies from requirements.txt...")
        if run_command(f"{sys.executable} -m pip install -r requirements.txt"):
            print("\n[+] All dependencies installed successfully!")
        else:
            print("\n[!] Some dependencies failed to install. The tool might not work perfectly.")
    else:
        print("[!] requirements.txt not found!")

    print("\n" + "="*40)
    print("[+] Windows Setup Completed!")
    print("="*40 + "\n")

    # Automatically launch the tool
    print_status("Launching 0312-OSINT...")
    os.system(f"{sys.executable} main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Setup cancelled by user.")
        sys.exit(0)
