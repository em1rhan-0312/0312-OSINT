import requests
from modules import display as disp

class ShodanOSINT:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def lookup_ip(self, ip):
        if not self.api_key:
            disp.perror("Shodan API Key not found in config! Please add it to credentials.ini")
            return

        url = f"https://api.shodan.io/shodan/host/{ip}?key={self.api_key}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                disp.pheader(f"SHODAN RESULTS FOR: {ip}")
                disp.pout(f" Organization: {data.get('org', 'N/A')}\n", disp.WHITE)
                disp.pout(f" Operating System: {data.get('os', 'N/A')}\n", disp.WHITE)
                
                ports = data.get('ports', [])
                disp.pout(f" Open Ports: {', '.join(map(str, ports))}\n", disp.GREEN)
                
                disp.pout("\n Services:\n", disp.YELLOW)
                for port, info in data.get('data', []):
                    if 'port' in info:
                        disp.pout(f"  - Port {info['port']}: {info.get('banner', 'No banner').strip()}\n", disp.WHITE)
            elif response.status_code == 404:
                disp.perror("No results found for this IP on Shodan.")
            else:
                disp.perror(f"Shodan API Error: {response.status_code}")
        except Exception as e:
            disp.perror(f"Connection error: {e}")

def run_shodan_lookup():
    from modules.config_loader import ConfigLoader
    cfg = ConfigLoader()
    api_key = cfg.get("shodan_api", "api")
    
    disp.pheader("SHODAN IP LOOKUP")
    ip = disp.pin("Enter IP address: ")
    if ip:
        shodan = ShodanOSINT(api_key)
        shodan.lookup_ip(ip)
