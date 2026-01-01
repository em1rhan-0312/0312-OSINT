import os
import sys
import configparser

INI_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "credentials.ini")

_config = None

def _load():
    global _config
    if _config is not None:
        return _config
    _config = configparser.ConfigParser(interpolation=None)
    try:
        read_ok = _config.read(INI_PATH, encoding="utf-8")
        if not read_ok:
            print(f"[!] Config file not found at {INI_PATH}")
            sys.exit(1)
    except Exception as e:
        print(f"[!] Config error: {e}")
        sys.exit(1)
    return _config

def get(section, key, default=""):
    cfg = _load()
    try:
        val = cfg[section].get(key, default)
        return val if val else default
    except (KeyError, configparser.NoSectionError):
        return default

def get_instagram_credentials():
    u = get("Credentials", "instagram_username")
    p = get("Credentials", "instagram_password")
    return u, p

def get_hiker_token():
    return get("Credentials", "hikerapi_token") or os.getenv("HIKERAPI_TOKEN")

def get_api_key(name):
    return get("Credentials", name) or os.getenv(name.upper())
