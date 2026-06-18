import json
import sys
import os
import time
import urllib.request
import datetime
import ssl
from pathlib import Path

ssl._create_default_https_context = ssl._create_unverified_context

from prettytable import PrettyTable
from geopy.geocoders import Nominatim

from . import config_loader as cfg
from . import display as disp
from .report import ReportEngine

BS4_AVAILABLE = False
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BeautifulSoup = None

REQUESTS_AVAILABLE = False
try:
    import requests as req_lib
    REQUESTS_AVAILABLE = True
except ImportError:
    req_lib = None

INSTAGRAM_API_AVAILABLE = False
HIKERAPI_AVAILABLE = False

try:
    from instagram_private_api import Client as IGClient
    from instagram_private_api import (
        ClientCookieExpiredError,
        ClientLoginRequiredError,
        ClientError,
        ClientThrottledError,
    )
    INSTAGRAM_API_AVAILABLE = True
except ImportError:
    IGClient = None

try:
    from hikerapi import Client as HikerClient
    from hikerapi import __version__ as hk_ver
    HIKERAPI_AVAILABLE = True
except ImportError:
    HikerClient = None


class InstagramOSINT:
    def __init__(self):
        self.api = None
        self.api_type = None
        self.target = ""
        self.target_id = None
        self.is_private = False
        self.user_data = {}
        self.output_dir = "output"
        self.report = None

    def login(self):
        hiker_token = cfg.get_hiker_token()
        if hiker_token and HIKERAPI_AVAILABLE:
            disp.pout("\n[*] Connecting via HikerAPI...\n", disp.CYAN)
            try:
                self.api = HikerClient(token=hiker_token)
                self.api_type = "hiker"
                disp.pok("HikerAPI connected successfully")
                return True
            except Exception as e:
                disp.perror(f"HikerAPI connection failed: {e}")

        ig_user, ig_pass = cfg.get_instagram_credentials()
        if ig_user and ig_pass and INSTAGRAM_API_AVAILABLE:
            disp.pout("\n[*] Logging into Instagram...\n", disp.CYAN)
            try:
                settings_file = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "config", "settings.json"
                )
                try:
                    with open(settings_file) as f:
                        cached = json.load(f)
                    self.api = IGClient(
                        username=ig_user, password=ig_pass,
                        settings=cached,
                        on_login=lambda x: self._save_settings(x, settings_file)
                    )
                except (FileNotFoundError, json.JSONDecodeError):
                    self.api = IGClient(
                        auto_patch=True, authenticate=True,
                        username=ig_user, password=ig_pass,
                        on_login=lambda x: self._save_settings(x, settings_file)
                    )
                self.api_type = "instagram"
                disp.pok(f"Logged in as {self.api.username}")
                return True
            except Exception as e:
                disp.perror(f"Instagram login failed: {e}")
                return False
        else:
            if not HIKERAPI_AVAILABLE and not INSTAGRAM_API_AVAILABLE:
                disp.perror("Missing API libraries. Install with: pip install hikerapi instagram-private-api")
            else:
                disp.perror("No valid API credentials found. Configure config/credentials.ini")
            return False

    def _save_settings(self, api, path):
        with open(path, "w") as f:
            json.dump(api.settings, f, default=self._json_default)

    def _json_default(self, obj):
        if isinstance(obj, bytes):
            return {"__class__": "bytes", "__value__": obj.hex()}
        raise TypeError(f"Not serializable: {obj}")

    def _get_username_from_json(self, obj):
        if isinstance(obj, dict) and "__class__" in obj and obj["__class__"] == "bytes":
            return bytes.fromhex(obj["__value__"])
        return obj

    def set_target(self, username):
        self.target = username
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", username
        )
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.report = ReportEngine(self.output_dir, username)

        if self.api_type == "hiker":
            try:
                data = self.api.user_by_username_v2(username)
                if "user" in data:
                    self.user_data = data["user"]
                elif "user" in data.get("response", {}):
                    self.user_data = data["response"]["user"]
                else:
                    self.user_data = data
                self.target_id = self.user_data.get("pk") or self.user_data.get("id")
                self.is_private = self.user_data.get("is_private", False)
                disp.pok(f"Target set: {username} [ID: {self.target_id}]")
                if self.is_private:
                    disp.pout(" [PRIVATE PROFILE]\n", disp.BLUE)
                return True
            except Exception as e:
                disp.perror(f"Failed to resolve user: {e}")
                return False
        else:
            try:
                content = self.api.username_info(username)
                u = content["user"]
                self.user_data = u
                self.target_id = u["pk"]
                self.is_private = u["is_private"]
                disp.pok(f"Target set: {username} [ID: {self.target_id}]")
                if self.is_private:
                    disp.pout(" [PRIVATE PROFILE]\n", disp.BLUE)
                return True
            except ClientError as e:
                disp.perror(f"User not found: {username}")
                return False

    def _check_private(self):
        if self.is_private:
            disp.perror("Cannot execute: user has private profile")
            return True
        return False

    def _get_feed(self, limit=-1):
        data = []
        if self.api_type == "hiker":
            next_page = ""
            while True:
                try:
                    disp.pout("@", disp.CYAN)
                    result = self.api.user_medias_v2(self.target_id, page_id=next_page)
                    items = result.get("response", {}).get("items", [])
                    data.extend(items)
                    next_page = result.get("next_page_id")
                    if limit > 0 and len(data) >= limit:
                        break
                    if not next_page:
                        break
                except Exception as e:
                    disp.perror(f"Feed error: {e}")
                    break
        else:
            result = self.api.user_feed(str(self.target_id))
            data.extend(result.get("items", []))
            next_id = result.get("next_max_id")
            while next_id:
                results = self.api.user_feed(str(self.target_id), max_id=next_id)
                data.extend(results.get("items", []))
                next_id = results.get("next_max_id")
        return data

    def get_info(self):
        if self.api_type == "hiker":
            d = self.user_data
        else:
            try:
                ep = f"users/{self.target_id}/full_detail_info/"
                content = self.api._call_api(ep)
                d = content["user_detail"]["user"]
            except ClientError as e:
                disp.perror(f"Error fetching info: {e}")
                return

        info = {}
        disp.pheader("TARGET INFORMATION")

        fields = [
            ("ID", "pk", disp.GREEN),
            ("Full Name", "full_name", disp.RED),
            ("Username", "username", disp.YELLOW),
            ("Biography", "biography", disp.CYAN),
            ("Followers", "follower_count", disp.BLUE),
            ("Following", "following_count", disp.GREEN),
            ("Media Count", "media_count", disp.CYAN),
            ("Verified", "is_verified", disp.MAGENTA),
            ("Business", "is_business", disp.RED),
            ("Private", "is_private", disp.YELLOW),
            ("Category", "category", disp.CYAN),
            ("Email", "public_email", disp.BLUE),
            ("WhatsApp", "whatsapp_number", disp.GREEN),
            ("City", "city_name", disp.YELLOW),
            ("Address", "address_street", disp.RED),
            ("Phone", "contact_phone_number", disp.CYAN),
            ("FB Page", "connected_fb_page", disp.MAGENTA),
            ("Profile Pic", "hd_profile_pic_url_info", disp.GREEN),
        ]

        for label, key, color in fields:
            val = d.get(key)
            if val:
                if key == "hd_profile_pic_url_info":
                    val = val.get("url", "")
                if key == "is_verified" or key == "is_business" or key == "is_private":
                    val = "Yes" if val else "No"
                disp.pout(f"  [{label}] ", color, bold=True)
                disp.pout(f"{val}\n")
                info[label.lower().replace(" ", "_")] = val

        self.report.add("target_info", info)
        return info

    def get_followers(self):
        if self._check_private():
            return
        disp.pheader("FOLLOWERS")
        disp.pout("[*] Fetching followers", disp.CYAN)

        users = []
        if self.api_type == "hiker":
            next_page = ""
            while True:
                disp.pout("@", disp.CYAN)
                result = self.api.user_followers_v2(self.target_id, page_id=next_page)
                items = result.get("response", {}).get("users", [])
                for u in items:
                    users.append({
                        "id": u.get("pk"),
                        "username": u.get("username"),
                        "full_name": u.get("full_name"),
                        "is_private": u.get("is_private"),
                        "is_verified": u.get("is_verified"),
                    })
                next_page = result.get("next_page_id")
                if not next_page:
                    break
        else:
            rank = IGClient.generate_uuid()
            data = self.api.user_followers(str(self.target_id), rank_token=rank)
            for u in data.get("users", []):
                users.append({"id": u["pk"], "username": u["username"], "full_name": u["full_name"]})
            next_id = data.get("next_max_id")
            while next_id:
                results = self.api.user_followers(str(self.target_id), rank_token=rank, max_id=next_id)
                for u in results.get("users", []):
                    users.append({"id": u["pk"], "username": u["username"], "full_name": u["full_name"]})
                next_id = results.get("next_max_id")

        disp.pout(f"\n[+] Total followers: {len(users)}\n", disp.GREEN)
        t = PrettyTable(["#", "ID", "Username", "Full Name"])
        t.align = "l"
        for i, u in enumerate(users[:50], 1):
            t.add_row([i, u["id"], u["username"], u["full_name"]])
        print(t)
        if len(users) > 50:
            disp.pout(f"  ... and {len(users) - 50} more\n", disp.YELLOW)

        self.report.add("followers", users)
        return users

    def get_following(self):
        if self._check_private():
            return
        disp.pheader("FOLLOWING")
        disp.pout("[*] Fetching following", disp.CYAN)

        users = []
        if self.api_type == "hiker":
            next_page = ""
            while True:
                disp.pout("@", disp.CYAN)
                result = self.api.user_following_v2(self.target_id, page_id=next_page)
                items = result.get("response", {}).get("users", [])
                for u in items:
                    users.append({
                        "id": u.get("pk"),
                        "username": u.get("username"),
                        "full_name": u.get("full_name"),
                        "is_private": u.get("is_private"),
                        "is_verified": u.get("is_verified"),
                    })
                next_page = result.get("next_page_id")
                if not next_page:
                    break
        else:
            rank = IGClient.generate_uuid()
            data = self.api.user_following(str(self.target_id), rank_token=rank)
            for u in data.get("users", []):
                users.append({"id": u["pk"], "username": u["username"], "full_name": u["full_name"]})
            next_id = data.get("next_max_id")
            while next_id:
                results = self.api.user_following(str(self.target_id), rank_token=rank, max_id=next_id)
                for u in results.get("users", []):
                    users.append({"id": u["pk"], "username": u["username"], "full_name": u["full_name"]})
                next_id = results.get("next_max_id")

        disp.pout(f"\n[+] Total following: {len(users)}\n", disp.GREEN)
        t = PrettyTable(["#", "ID", "Username", "Full Name"])
        t.align = "l"
        for i, u in enumerate(users[:50], 1):
            t.add_row([i, u["id"], u["username"], u["full_name"]])
        print(t)
        if len(users) > 50:
            disp.pout(f"  ... and {len(users) - 50} more\n", disp.YELLOW)

        self.report.add("following", users)
        return users

    def get_follow_analysis(self):
        followers = self.get_followers()
        following = self.get_following()
        if not followers or not following:
            return

        f_ids = {u["id"] for u in followers}
        fg_ids = {u["id"] for u in following}

        not_following_back = [u for u in following if u["id"] not in f_ids]
        not_followed_back = [u for u in followers if u["id"] not in fg_ids]
        mutual = [u for u in followers if u["id"] in fg_ids]

        disp.pheader("FOLLOW ANALYSIS")
        disp.pout(f"  Mutual Followers: {len(mutual)}\n", disp.GREEN)
        disp.pout(f"  Not Following Back: {len(not_following_back)}\n", disp.RED)
        disp.pout(f"  Not Followed Back: {len(not_followed_back)}\n", disp.YELLOW)

        if not_following_back:
            disp.pout("\n[!] Users who don't follow back:\n", disp.RED)
            t = PrettyTable(["#", "Username", "Full Name"])
            t.align = "l"
            for i, u in enumerate(not_following_back[:30], 1):
                t.add_row([i, u["username"], u.get("full_name", "")])
            print(t)

        self.report.add("mutual_followers", mutual)
        self.report.add("not_following_back", not_following_back)
        return {"mutual": mutual, "not_following_back": not_following_back, "not_followed_back": not_followed_back}

    def get_posts_analysis(self):
        if self._check_private():
            return
        disp.pheader("POST ANALYSIS")
        disp.pout("[*] Analyzing posts", disp.CYAN)

        data = self._get_feed()
        if not data:
            disp.perror("No posts found")
            return

        total_likes = 0
        total_comments = 0
        photos = 0
        videos = 0
        carousels = 0
        likes_list = []
        comments_list = []
        caption_words = {}
        hashtags = {}
        hours = {}

        for post in data:
            lc = post.get("like_count", 0)
            cc = post.get("comment_count", 0)
            total_likes += lc
            total_comments += cc
            likes_list.append(lc)
            comments_list.append(cc)

            mt = post.get("media_type", 0)
            if mt == 1:
                photos += 1
            elif mt == 2:
                videos += 1
            elif mt == 8:
                carousels += 1

            caption = post.get("caption")
            if caption and caption.get("text"):
                words = caption["text"].split()
                for w in words:
                    if w.startswith("#"):
                        hashtags[w.lower()] = hashtags.get(w.lower(), 0) + 1
                    else:
                        cw = w.lower().strip(".,!?;:")
                        if len(cw) > 3:
                            caption_words[cw] = caption_words.get(cw, 0) + 1

            ts = post.get("taken_at")
            if ts:
                dt = datetime.datetime.fromtimestamp(ts)
                h = dt.hour
                hours[h] = hours.get(h, 0) + 1

        n = len(data)
        avg_likes = total_likes // n if n else 0
        avg_comments = total_comments // n if n else 0
        max_likes = max(likes_list) if likes_list else 0
        min_likes = min(likes_list) if likes_list else 0

        disp.pout(f"  Total Posts Analyzed: {n}\n", disp.GREEN)
        disp.pout(f"  Photos: {photos} | Videos: {videos} | Carousels: {carousels}\n")
        disp.pout(f"  Total Likes: {total_likes} | Avg: {avg_likes} | Max: {max_likes} | Min: {min_likes}\n", disp.MAGENTA)
        disp.pout(f"  Total Comments: {total_comments} | Avg: {avg_comments}\n", disp.CYAN)

        if hashtags:
            disp.pout("\n[#] Top Hashtags:\n", disp.YELLOW)
            sorted_h = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:15]
            for tag, count in sorted_h:
                disp.pout(f"    {tag}: {count}\n")

        if hours:
            best_hour = max(hours, key=hours.get)
            disp.pout(f"\n[+] Best time to post: ~{best_hour}:00 ({hours[best_hour]} posts)\n", disp.GREEN)

        analysis = {
            "total_posts": n,
            "photos": photos,
            "videos": videos,
            "carousels": carousels,
            "total_likes": total_likes,
            "avg_likes": avg_likes,
            "total_comments": total_comments,
            "avg_comments": avg_comments,
            "top_hashtags": dict(sorted_h[:20]) if hashtags else {},
        }
        self.report.add("post_analysis", analysis)
        return analysis

    def get_emails(self, target_type="followers"):
        if self._check_private():
            return
        users = self.get_followers() if target_type == "followers" else self.get_following()
        if not users:
            return

        disp.pheader(f"EMAIL LOOKUP - {target_type.upper()}")
        disp.pout(f"[*] Scanning {len(users)} users for emails (this may take a while)...\n", disp.CYAN)

        results = []
        limit = disp.pin("How many users to scan (default 20): ", disp.YELLOW)
        try:
            limit = int(limit) if limit else 20
        except ValueError:
            limit = 20

        for i, u in enumerate(users[:limit]):
            disp.pout(f"\r  Scanning {i+1}/{limit}...", disp.CYAN)
            try:
                if self.api_type == "hiker":
                    info = self.api.user_by_id_v2(u["id"])
                    user_info = info.get("user", {})
                else:
                    info = self.api.user_info(str(u["id"]))
                    user_info = info.get("user", {})
                email = user_info.get("public_email")
                if email:
                    u["email"] = email
                    results.append(u)
                    disp.pout(f"\n[+] {u['username']}: {email}\n", disp.GREEN)
            except Exception:
                continue
            time.sleep(0.5)

        disp.pout(f"\n[+] Found {len(results)} emails\n", disp.GREEN)
        if results:
            t = PrettyTable(["Username", "Full Name", "Email"])
            t.align = "l"
            for r in results:
                t.add_row([r["username"], r.get("full_name", ""), r.get("email", "")])
            print(t)

        self.report.add(f"{target_type}_emails", results)
        return results

    def get_phone_numbers(self, target_type="followers"):
        if self._check_private():
            return
        users = self.get_followers() if target_type == "followers" else self.get_following()
        if not users:
            return

        disp.pheader(f"PHONE LOOKUP - {target_type.upper()}")
        disp.pout(f"[*] Scanning {len(users)} users for phone numbers...\n", disp.CYAN)

        results = []
        limit = disp.pin("How many users to scan (default 20): ", disp.YELLOW)
        try:
            limit = int(limit) if limit else 20
        except ValueError:
            limit = 20

        for i, u in enumerate(users[:limit]):
            disp.pout(f"\r  Scanning {i+1}/{limit}...", disp.CYAN)
            try:
                if self.api_type == "hiker":
                    info = self.api.user_by_id_v2(u["id"])
                    user_info = info.get("user", {})
                else:
                    info = self.api.user_info(str(u["id"]))
                    user_info = info.get("user", {})
                phone = user_info.get("contact_phone_number")
                if phone:
                    u["phone"] = phone
                    results.append(u)
                    disp.pout(f"\n[+] {u['username']}: {phone}\n", disp.GREEN)
            except Exception:
                continue
            time.sleep(0.5)

        disp.pout(f"\n[+] Found {len(results)} phone numbers\n", disp.GREEN)
        if results:
            t = PrettyTable(["Username", "Full Name", "Phone"])
            t.align = "l"
            for r in results:
                t.add_row([r["username"], r.get("full_name", ""), r.get("phone", "")])
            print(t)

        self.report.add(f"{target_type}_phones", results)
        return results

    def get_hashtags(self):
        if self._check_private():
            return
        disp.pheader("HASHTAG ANALYSIS")
        disp.pout("[*] Extracting hashtags from posts", disp.CYAN)

        data = self._get_feed()
        hashtags = {}
        for post in data:
            caption = post.get("caption")
            if caption and caption.get("text"):
                for word in caption["text"].split():
                    if word.startswith("#"):
                        h = word.lower()
                        hashtags[h] = hashtags.get(h, 0) + 1

        if hashtags:
            sorted_h = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)
            t = PrettyTable(["Count", "Hashtag"])
            t.align = "l"
            for h, c in sorted_h:
                t.add_row([c, h])
            print(t)
        else:
            disp.perror("No hashtags found")

        self.report.add("hashtags", hashtags)
        return hashtags

    def get_locations(self):
        if self._check_private():
            return
        disp.pheader("LOCATIONS")
        disp.pout("[*] Extracting locations from posts", disp.CYAN)

        data = self._get_feed()
        locs = {}
        for post in data:
            loc = post.get("location")
            if loc and loc.get("lat") and loc.get("lng"):
                key = f"{loc['lat']},{loc['lng']}"
                if key not in locs:
                    locs[key] = {
                        "lat": loc["lat"],
                        "lng": loc["lng"],
                        "name": loc.get("name", ""),
                        "count": 0,
                    }
                locs[key]["count"] += 1

        if locs:
            geolocator = Nominatim(user_agent="0312osint")
            t = PrettyTable(["#", "Name", "Address", "Count"])
            t.align = "l"
            for i, (key, info) in enumerate(locs.items(), 1):
                try:
                    addr = geolocator.reverse(f"{info['lat']}, {info['lng']}")
                    address = addr.address
                except:
                    address = f"{info['lat']}, {info['lng']}"
                t.add_row([i, info["name"], address, info["count"]])
            print(t)
        else:
            disp.perror("No locations found")

        self.report.add("locations", locs)
        return locs

    def get_stories(self):
        if self._check_private():
            return
        disp.pheader("STORIES")
        disp.pout("[*] Downloading stories", disp.CYAN)

        try:
            if self.api_type == "hiker":
                data = self.api.user_stories_v2(self.target_id)
                items = []
                if data.get("reel"):
                    items = data["reel"].get("items", [])
            else:
                data = self.api.user_reel_media(str(self.target_id))
                items = data.get("items", [])

            if not items:
                disp.perror("No stories available")
                return

            count = 0
            for item in items:
                story_id = item["id"]
                if item.get("media_type") == 1:
                    url = item["image_versions2"]["candidates"][0]["url"]
                    ext = ".jpg"
                else:
                    url = item["video_versions"][0]["url"]
                    ext = ".mp4"
                path = os.path.join(self.output_dir, f"story_{story_id}{ext}")
                urllib.request.urlretrieve(url, path)
                count += 1
                disp.pout(f"\r  Downloaded {count} stories", disp.GREEN)

            disp.pout(f"\n[+] Downloaded {count} stories to {self.output_dir}\n", disp.GREEN)
            self.report.add("stories_downloaded", count)
            return count
        except Exception as e:
            disp.perror(f"Story download failed: {e}")

    def get_photos(self):
        if self._check_private():
            return
        disp.pheader("PHOTOS")
        limit_str = disp.pin("How many photos to download (default all): ", disp.YELLOW)
        try:
            limit = int(limit_str) if limit_str else -1
        except ValueError:
            limit = -1

        disp.pout("[*] Downloading photos", disp.CYAN)
        data = self._get_feed(limit=limit)
        count = 0
        for item in data:
            if "image_versions2" in item:
                url = item["image_versions2"]["candidates"][0]["url"]
                path = os.path.join(self.output_dir, f"photo_{item['id']}.jpg")
                urllib.request.urlretrieve(url, path)
                count += 1
                disp.pout(f"\r  Downloaded {count} photos", disp.GREEN)
            elif "carousel_media" in item:
                for media in item["carousel_media"]:
                    if "image_versions2" in media:
                        url = media["image_versions2"]["candidates"][0]["url"]
                        path = os.path.join(self.output_dir, f"photo_{media['id']}.jpg")
                        urllib.request.urlretrieve(url, path)
                        count += 1
                        disp.pout(f"\r  Downloaded {count} photos", disp.GREEN)

        disp.pout(f"\n[+] Downloaded {count} photos to {self.output_dir}\n", disp.GREEN)
        self.report.add("photos_downloaded", count)
        return count

    def get_comments(self):
        if self._check_private():
            return
        disp.pheader("COMMENTS")
        disp.pout("[*] Fetching comments", disp.CYAN)

        data = self._get_feed()
        all_comments = []
        for post in data:
            post_id = post.get("id") or post.get("pk")
            if not post_id:
                continue
            try:
                if self.api_type == "hiker":
                    result = self.api.media_comments_v2(post_id)
                    comments = result.get("response", {}).get("comments", [])
                else:
                    result = self.api.media_comments(str(post_id))
                    comments = result.get("comments", [])
                    next_id = result.get("next_max_id")
                    while next_id:
                        more = self.api.media_comments(str(post_id), max_id=next_id)
                        comments.extend(more.get("comments", []))
                        next_id = more.get("next_max_id")
                for c in comments:
                    user = c.get("user", {})
                    all_comments.append({
                        "post_id": post_id,
                        "user_id": user.get("pk") or c.get("user_id"),
                        "username": user.get("username", ""),
                        "text": c.get("text", ""),
                    })
            except Exception as e:
                continue

        disp.pout(f"\n[+] Total comments: {len(all_comments)}\n", disp.GREEN)
        if all_comments:
            t = PrettyTable(["Post ID", "Username", "Comment"])
            t.align["Post ID"] = "l"
            t.align["Username"] = "l"
            t.align["Comment"] = "l"
            for c in all_comments[:30]:
                t.add_row([c["post_id"], c["username"], c["text"][:80]])
            print(t)
            if len(all_comments) > 30:
                disp.pout(f"  ... and {len(all_comments) - 30} more\n", disp.YELLOW)

        self.report.add("comments", all_comments)
        return all_comments

    def get_mutual_followers_with(self):
        other = disp.pin("Compare with username: ", disp.YELLOW)
        if not other:
            return

        disp.pout(f"[*] Analyzing mutual followers with {other}...\n", disp.CYAN)
        other_ig = InstagramOSINT()
        other_ig.api = self.api
        other_ig.api_type = self.api_type
        if not other_ig.set_target(other):
            return

        my_followers = self.get_followers()
        their_followers = other_ig.get_followers()
        if not my_followers or not their_followers:
            return

        my_ids = {u["id"] for u in my_followers}
        their_ids = {u["id"] for u in their_followers}
        mutual = [u for u in my_followers if u["id"] in their_ids]

        disp.pheader("MUTUAL FOLLOWERS")
        disp.pout(f"  {self.target}'s followers: {len(my_followers)}\n")
        disp.pout(f"  {other}'s followers: {len(their_followers)}\n")
        disp.pout(f"  Mutual: {len(mutual)}\n", disp.GREEN)

        if mutual:
            t = PrettyTable(["#", "Username", "Full Name"])
            t.align = "l"
            for i, u in enumerate(mutual[:30], 1):
                t.add_row([i, u["username"], u.get("full_name", "")])
            print(t)

        self.report.add(f"mutual_with_{other}", mutual)
        return mutual

    def get_profile_pic(self):
        disp.pheader("PROFILE PICTURE")
        d = self.user_data
        url = None
        if "hd_profile_pic_url_info" in d:
            url = d["hd_profile_pic_url_info"]["url"]
        elif "hd_profile_pic_versions" in d and d["hd_profile_pic_versions"]:
            url = d["hd_profile_pic_versions"][-1]["url"]

        if url:
            path = os.path.join(self.output_dir, f"{self.target}_propic.jpg")
            urllib.request.urlretrieve(url, path)
            disp.pok(f"Saved to {path}")
        else:
            disp.perror("No profile picture URL found")

    def get_tagged(self):
        disp.pheader("TAGGED MEDIA")
        disp.pout("[*] Fetching tagged media", disp.CYAN)

        posts = []
        try:
            if self.api_type == "hiker":
                next_page = ""
                while True:
                    disp.pout("@", disp.CYAN)
                    r = self.api.user_tag_medias_v2(self.target_id, page_id=next_page)
                    items = r.get("response", {}).get("items", [])
                    posts.extend(items)
                    next_page = r.get("next_page_id")
                    if not next_page:
                        break
            else:
                r = self.api.usertag_feed(self.target_id)
                posts.extend(r.get("items", []))
                next_id = r.get("next_max_id")
                while next_id:
                    more = self.api.user_feed(str(self.target_id), max_id=next_id)
                    posts.extend(more.get("items", []))
                    next_id = more.get("next_max_id")
        except Exception as e:
            disp.perror(f"Error: {e}")
            return

        users = {}
        for post in posts:
            u = post.get("user", {})
            pk = u.get("pk")
            if pk:
                if pk not in users:
                    users[pk] = {"id": pk, "username": u.get("username"), "full_name": u.get("full_name"), "count": 0}
                users[pk]["count"] += 1

        sorted_users = sorted(users.values(), key=lambda x: x["count"], reverse=True)
        disp.pout(f"\n[+] Found {len(sorted_users)} users who tagged {self.target}\n", disp.GREEN)

        if sorted_users:
            t = PrettyTable(["Count", "Username", "Full Name"])
            t.align = "l"
            for u in sorted_users[:30]:
                t.add_row([u["count"], u["username"], u["full_name"]])
            print(t)

        self.report.add("tagged_by", sorted_users)
        return sorted_users

    def generate_report(self):
        path = self.report.save_html()
        csv_path = self.report.save_json()
        disp.pok(f"HTML report: {path}")
        disp.pok(f"JSON report: {csv_path}")
        return path


class ScraperOSINT:
    def __init__(self):
        self.target = ""
        self.profile_data = {}
        self.user_data = {}
        self.is_private = False
        self.output_dir = ""
        self.report = None

    def _random_ua(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        ]
        import random
        return random.choice(agents)

    def set_target(self, username):
        self.target = username
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", username
        )
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.report = ReportEngine(self.output_dir, username)

        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            disp.perror("Missing dependencies: pip install requests beautifulsoup4")
            return False

        disp.pout(f"[*] Scraping public profile: {username}\n", disp.CYAN)

        try:
            url = f"https://www.instagram.com/{username}/"
            r = req_lib.get(url, headers={"User-Agent": self._random_ua()}, timeout=15)
            if r.status_code != 200:
                disp.perror(f"Instagram returned status {r.status_code}")
                return False

            soup = BeautifulSoup(r.text, "html.parser")
            meta_desc = soup.find_all("meta", attrs={"property": "og:description"})
            ld_json = soup.find("script", attrs={"type": "application/ld+json"})

            if not meta_desc or not ld_json:
                disp.perror("Instagram now requires login for API access")
                disp.pout("\n  Instagram scraper needs a logged-in session.\n", disp.YELLOW)
                disp.pout("  Options:\n", disp.YELLOW)
                disp.pout(f"    1. Use 'ig {username}' command (needs HikerAPI or Instagram credentials in config/credentials.ini)\n", disp.CYAN)
                disp.pout(f"    2. Add hikerapi_token to config/credentials.ini for instant access\n", disp.CYAN)
                return False

            text = meta_desc[0].get("content", "").split()
            desc_data = json.loads(ld_json.get_text())

            self.user_data = {
                "username": username,
                "full_name": desc_data.get("name", ""),
                "url": desc_data.get("mainEntityofPage", {}).get("@id", url),
                "followers": text[0] if len(text) > 0 else "?",
                "following": text[2] if len(text) > 2 else "?",
                "posts": text[4] if len(text) > 4 else "?",
            }

            scripts = soup.find_all("script", attrs={"type": "text/javascript"})
            profile_meta = None
            for script in scripts:
                t = script.get_text()
                if "window.__INITIAL_STATE__" in t or "window._sharedData" in t:
                    start_key = "window.__INITIAL_STATE__" if "window.__INITIAL_STATE__" in t else "window._sharedData"
                    start = t.index(start_key) + len(start_key) + 1
                    raw = t[start:].strip(";").strip()
                    if raw.startswith("="):
                        raw = raw[1:]
                    try:
                        profile_meta = json.loads(raw)
                    except:
                        continue
                    break

            if profile_meta:
                try:
                    user = profile_meta["entry_data"]["ProfilePage"][0]["graphql"]["user"]
                    self.profile_data = user
                    self.user_data.update({
                        "pk": user.get("id"),
                        "biography": user.get("biography", ""),
                        "profile_pic_url": user.get("profile_pic_url_hd", ""),
                        "is_private": user.get("is_private", False),
                        "is_verified": user.get("is_verified", False),
                        "is_business": user.get("is_business_account", False),
                        "business_category": user.get("business_category_name", ""),
                        "external_url": user.get("external_url", ""),
                        "connected_fb": user.get("connected_fb_page", ""),
                        "joined_recently": user.get("is_joined_recently", False),
                        "followers_count": user.get("edge_followed_by", {}).get("count", text[0]),
                        "following_count": user.get("edge_follow", {}).get("count", text[2]),
                        "media_count": user.get("edge_owner_to_timeline_media", {}).get("count", text[4]),
                    })
                    self.is_private = user.get("is_private", False)
                except (KeyError, IndexError, TypeError):
                    pass

            disp.pok(f"Target: {username}")
            if self.user_data.get("is_private"):
                disp.pout(" [PRIVATE PROFILE]\n", disp.BLUE)
            else:
                disp.pout("\n")
            return True

        except req_lib.exceptions.Timeout:
            disp.perror("Request timed out")
            return False
        except req_lib.exceptions.ConnectionError:
            disp.perror("Connection error")
            return False
        except Exception as e:
            disp.perror(f"Scrape failed: {e}")
            return False

    def get_info(self):
        disp.pheader("TARGET INFORMATION")
        d = self.user_data

        fields = [
            ("Username", "username"),
            ("Full Name", "full_name"),
            ("Biography", "biography"),
            ("Followers", "followers"),
            ("Following", "following"),
            ("Posts", "posts"),
            ("Verified", "is_verified"),
            ("Private", "is_private"),
            ("Business", "is_business"),
            ("Business Category", "business_category"),
            ("External URL", "external_url"),
            ("Connected FB", "connected_fb"),
            ("Joined Recently", "joined_recently"),
            ("Profile Pic", "profile_pic_url"),
        ]

        for label, key in fields:
            val = d.get(key)
            if val:
                color = disp.GREEN if val is True else disp.RED if val is False else disp.WHITE
                if isinstance(val, bool):
                    val = "Yes" if val else "No"
                if key == "profile_pic_url":
                    disp.pout(f"  [{label}] ", disp.CYAN, bold=True)
                    disp.pout(f"{str(val)[:80]}...\n")
                else:
                    disp.pout(f"  [{label}] ", disp.CYAN, bold=True)
                    disp.pout(f"{val}\n", color)

        self.report.add("scraped_info", self.user_data)
        return self.user_data

    def get_posts(self, limit=None):
        if self.is_private:
            disp.perror("Private profile")
            return

        if not self.profile_data:
            disp.perror("No post data available")
            return

        disp.pheader("POSTS")
        try:
            edges = self.profile_data.get("edge_owner_to_timeline_media", {}).get("edges", [])
            if not edges:
                disp.perror("No posts found")
                return

            if limit is None:
                limit_str = disp.pin("How many posts (default all): ", disp.YELLOW)
                try:
                    limit = int(limit_str) if limit_str else len(edges)
                except ValueError:
                    limit = len(edges)

            posts = []
            for i, edge in enumerate(edges[:limit]):
                node = edge.get("node", {})
                caption = ""
                cap_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                if cap_edges:
                    caption = cap_edges[0].get("node", {}).get("text", "")

                post = {
                    "id": node.get("id"),
                    "shortcode": node.get("shortcode"),
                    "caption": caption[:200],
                    "likes": node.get("edge_liked_by", {}).get("count", 0),
                    "comments": node.get("edge_media_to_comment", {}).get("count", 0),
                    "taken_at": node.get("taken_at_timestamp", ""),
                    "url": f"https://www.instagram.com/p/{node.get('shortcode')}/",
                }
                posts.append(post)

            t = PrettyTable(["#", "Likes", "Comments", "Caption"])
            t.align = "l"
            for i, p in enumerate(posts, 1):
                t.add_row([i, p["likes"], p["comments"], p["caption"][:50]])
            print(t)

            self.report.add("scraped_posts", posts)
            return posts

        except Exception as e:
            disp.perror(f"Error: {e}")

    def download_profile_pic(self):
        url = self.user_data.get("profile_pic_url")
        if not url:
            disp.perror("No profile picture URL")
            return

        path = os.path.join(self.output_dir, f"{self.target}_propic.jpg")
        try:
            r = req_lib.get(url, headers={"User-Agent": self._random_ua()}, timeout=10)
            with open(path, "wb") as f:
                f.write(r.content)
            disp.pok(f"Saved to {path}")
        except Exception as e:
            disp.perror(f"Download failed: {e}")

    def generate_report(self):
        path = self.report.save_html()
        disp.pok(f"HTML report: {path}")
        return path
