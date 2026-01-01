import requests
from modules import display as disp

class DirectoryBruter:
    def __init__(self):
        self.common_paths = [
            "admin", "administrator", "login", "config", "settings",
            "backup", "db", "database", "phpmyadmin", "wp-admin",
            "wp-content", "uploads", ".env", ".git", ".htaccess",
            "api", "v1", "v2", "test", "dev", "staging", "secret"
        ]

    def brute_force(self, target_url):
        if not target_url.startswith("http"):
            target_url = "http://" + target_url
        
        target_url = target_url.rstrip("/")
        disp.pinfo(f"Scanning: {target_url}\n")
        
        found_dirs = []
        
        for path in self.common_paths:
            url = f"{target_url}/{path}"
            try:
                # Using a timeout to avoid hanging
                response = requests.get(url, timeout=3, allow_redirects=False)
                if response.status_code == 200:
                    disp.pok(f"Found: {url} (200 OK)")
                    found_dirs.append(url)
                elif response.status_code == 403:
                    disp.pout(f"Forbidden: {url} (403)\n", disp.YELLOW)
                    found_dirs.append(url)
                elif response.status_code == 301 or response.status_code == 302:
                    disp.pout(f"Redirect: {url} ({response.status_code})\n", disp.MAGENTA)
            except requests.exceptions.RequestException:
                pass
        
        if not found_dirs:
            disp.perror("No common directories found.")
        else:
            disp.pheader("SCAN RESULTS")
            for d in found_dirs:
                disp.pout(f"{d}\n", disp.GREEN)

def run_dir_bruter():
    disp.pheader("DIRECTORY BRUTE-FORCER")
    url = disp.pin("Enter target URL (e.g., example.com): ")
    bruter = DirectoryBruter()
    bruter.brute_force(url)
