import json
import urllib.request
import urllib.error

from . import display as disp
from .report import ReportEngine

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

class UsernameSearch:
    def __init__(self):
        self.report = ReportEngine("output", "username_search")

    PLATFORMS = [
        # === CONFIRMED (API or reliable 404) ===
        {
            "name": "GitHub",
            "url": "https://github.com/{}",
            "type": "api",
            "api_url": "https://api.github.com/users/{}",
            "check_key": "login",
            "reliable": True,
        },
        {
            "name": "GitLab",
            "url": "https://gitlab.com/{}",
            "type": "api",
            "api_url": "https://gitlab.com/api/v4/users?username={}",
            "check_key": "array_not_empty",
            "reliable": True,
        },
        {
            "name": "HackerNews",
            "url": "https://news.ycombinator.com/user?id={}",
            "type": "html",
            "not_found": ["no such user"],
            "reliable": True,
        },
        {
            "name": "YouTube",
            "url": "https://www.youtube.com/@{}",
            "type": "html",
            "not_found": ["not found", "page not available", "this page isn't available"],
            "reliable": True,
        },
        {
            "name": "Pastebin",
            "url": "https://pastebin.com/u/{}",
            "type": "status404",
            "reliable": True,
        },
        {
            "name": "Keybase",
            "url": "https://keybase.io/{}",
            "type": "status404",
            "reliable": True,
        },
        {
            "name": "Behance",
            "url": "https://www.behance.net/{}",
            "type": "status404",
            "reliable": True,
        },
        {
            "name": "Dribbble",
            "url": "https://dribbble.com/{}",
            "type": "status404",
            "reliable": True,
        },
        {
            "name": "Flickr",
            "url": "https://www.flickr.com/people/{}",
            "type": "status404",
            "reliable": True,
        },
        {
            "name": "Twitch",
            "url": "https://www.twitch.tv/{}",
            "type": "status404",
            "reliable": False,
        },
        # === PARTIAL (may have false positives, marked accordingly) ===
        {
            "name": "Reddit",
            "url": "https://www.reddit.com/user/{}",
            "type": "html",
            "not_found": ["page not found", "sorry", "nobody", "no results", "doesn't exist"],
            "confirm": ["karma", "trophy", "reddit", "joined"],
            "reliable": False,
        },
        {
            "name": "VK",
            "url": "https://vk.com/{}",
            "type": "html",
            "not_found": ["page not found", "not found", "doesn't exist"],
            "confirm": ["vk.com", "profile", "friend"],
            "reliable": False,
        },
        {
            "name": "Instagram",
            "url": "https://www.instagram.com/{}/",
            "type": "note",
            "note": "use 'ig' command",
            "reliable": False,
        },
        {
            "name": "TikTok",
            "url": "https://www.tiktok.com/@{}",
            "type": "html",
            "not_found": ["couldn't find", "page not found", "not found", "no results"],
            "confirm": ["tiktok", "follower", "like", "video"],
            "reliable": False,
        },
        {
            "name": "X / Twitter",
            "url": "https://x.com/{}",
            "type": "html",
            "not_found": ["doesn't exist", "page not found", "this account", "no results", "not found", "sorry"],
            "confirm": ["x.com", "tweet", "follower", "following"],
            "reliable": False,
        },
        {
            "name": "Telegram",
            "url": "https://t.me/{}",
            "type": "html",
            "not_found": ["sorry, this page", "page not found", "doesn't exist"],
            "confirm": ["telegram", "you can contact", "if you have telegram"],
            "reliable": False,
        },
        {
            "name": "OnlyFans",
            "url": "https://onlyfans.com/{}",
            "type": "status_any",
            "reliable": False,
        },
        {
            "name": "Medium",
            "url": "https://medium.com/@{}",
            "type": "html",
            "not_found": ["page not found", "not found", "this page"],
            "reliable": False,
        },
        {
            "name": "SoundCloud",
            "url": "https://soundcloud.com/{}",
            "type": "html",
            "not_found": ["page not found", "not found", "oops", "doesn't exist"],
            "reliable": False,
        },
        {
            "name": "Steam",
            "url": "https://steamcommunity.com/id/{}",
            "type": "html",
            "not_found": ["the specified profile could not be found", "no profile"],
            "reliable": False,
        },
        {
            "name": "DeviantArt",
            "url": "https://www.deviantart.com/{}",
            "type": "status404",
            "reliable": True,
        },
        {
            "name": "Patreon",
            "url": "https://www.patreon.com/{}",
            "type": "html",
            "not_found": ["page not found", "not found", "doesn't exist"],
            "reliable": False,
        },
    ]

    def _check(self, platform, username):
        url = platform["url"].format(username)
        check_type = platform.get("type", "html")

        try:
            if check_type == "note":
                return None

            if check_type == "api":
                return self._check_api(platform, username)

            if check_type == "status404":
                return self._check_status(url, expected=404)

            if check_type == "status_any":
                return self._check_status(url, expected=None)

            if check_type == "html":
                return self._check_html(url, platform)

            return None

        except Exception:
            return None

    def _check_api(self, platform, username):
        api_url = platform["api_url"].format(username)
        req = urllib.request.Request(api_url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode("utf-8", errors="replace"))
            key = platform.get("check_key", "")
            if key == "array_not_empty":
                return len(data) > 0
            parts = key.split(".")
            val = data
            for p in parts:
                val = val.get(p) if isinstance(val, dict) else None
                if val is None:
                    return False
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            if e.code == 403:
                return None
            return None
        except (json.JSONDecodeError, Exception):
            return None

    def _check_status(self, url, expected=404):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                if expected is None:
                    return True
                if r.status == 200:
                    return True
                return False
        except urllib.error.HTTPError as e:
            if expected == 404:
                if e.code == 404:
                    return False
                return None
            if e.code == 404:
                return False
            return None
        except Exception:
            return None

    def _check_html(self, url, platform):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            try:
                with urllib.request.urlopen(req, timeout=8) as r:
                    raw = r.read()
                    try:
                        body = raw.decode("utf-8", errors="replace").lower()[:4000]
                    except:
                        return None
                    final_url = r.url.lower()
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return False
                if e.code == 429:
                    return None
                return None

            domain = url.split("/")[2].lower()
            if domain not in final_url:
                return False

            not_found = platform.get("not_found", [])
            for kw in not_found:
                if kw.lower() in body:
                    return False

            confirm = platform.get("confirm", [])
            if confirm:
                has_confirm = any(k.lower() in body for k in confirm)
                if not has_confirm:
                    return None

            return True

        except Exception:
            return None

    def search(self, username):
        disp.pheader(f"USERNAME SEARCH: {username}")

        results = {
            "username": username,
            "profiles": {},
            "suggested": {},
        }
        found_count = 0
        suggested_count = 0

        for platform in self.PLATFORMS:
            name = platform["name"]
            url = platform["url"].format(username)
            reliable = platform.get("reliable", False)
            check_type = platform.get("type", "html")

            exists = self._check(platform, username)

            if exists is True and reliable:
                results["profiles"][name] = {"url": url, "status": "found"}
                disp.pout(f"  [+] {name}: {url}\n", disp.GREEN)
                found_count += 1
            elif exists is True and not reliable:
                results["suggested"][name] = {"url": url, "status": "possible"}
                disp.pout(f"  [~] {name}: {url} (may exist)\n", disp.YELLOW)
                suggested_count += 1
            elif exists is None and check_type != "note":
                results["suggested"][name] = {"url": url, "status": "unable_to_verify"}
                disp.pout(f"  [~] {name}: {url} (unable to verify)\n", disp.YELLOW)
                suggested_count += 1
            elif check_type == "note":
                results["suggested"][name] = {"url": url, "status": "needs_login"}
                note = platform.get("note", "")
                disp.pout(f"  [~] {name}: {url} ({note})\n", disp.YELLOW)
                suggested_count += 1

        disp.psep()
        total = found_count + suggested_count
        disp.pout(f"  Found: {found_count} | Possible: {suggested_count} | Total: {total}/{len(self.PLATFORMS)}\n",
                  disp.GREEN if found_count else disp.YELLOW)

        if suggested_count:
            disp.pout(f"  [~] marked profiles need manual browser check\n", disp.YELLOW)

        self.report.add("username_search", results)
        return results
