import requests
from modules import display as disp

class LeakSearch:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def check_leak(self, target):
        if not self.api_key:
            disp.perror("LeakCheck API Key not found! Please add it to credentials.ini")
            return

        # Using a generic example API structure (e.g., HaveIBeenPwned or similar)
        # Note: HIBP requires specific headers and registration
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{target}"
        headers = {
            "hibp-api-key": self.api_key,
            "user-agent": "0312-OSINT-Tool"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                leaks = response.json()
                disp.pheader(f"LEAK RESULTS FOR: {target}")
                for leak in leaks:
                    disp.pout(f" [+] Found in: {leak['Name']}\n", disp.RED)
                    disp.pout(f"     Date: {leak['BreachDate']}\n", disp.WHITE)
            elif response.status_code == 404:
                disp.pok("No leaks found for this target!")
            elif response.status_code == 401:
                disp.perror("Invalid API Key.")
            else:
                disp.perror(f"API Error: {response.status_code}")
        except Exception as e:
            disp.perror(f"Connection error: {e}")

def run_leak_search():
    from modules.config_loader import ConfigLoader
    cfg = ConfigLoader()
    api_key = cfg.get("hibp_api", "api")
    
    disp.pheader("LEAK DATABASE SEARCH")
    target = disp.pin("Enter Email or Username: ")
    if target:
        searcher = LeakSearch(api_key)
        searcher.check_leak(target)
