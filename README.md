# 0312-OSINT

Multi-Platform OSINT Framework — Instagram | Phone | Email | Username | IP | Domain | DDoS | SMS

---

## Image

<img width="1115" height="628" alt="image" src="https://github.com/user-attachments/assets/62ef7890-35ee-462d-b97f-c3d1c46a7a17" />

## English

### Installation

```bash
git clone https://github.com/em1rhan-0312/0312-OSINT.git
cd 0312-OSINT
pip install -r requirements.txt
```

### Configuration

Edit `config/credentials.ini`:

```ini
[Credentials]
instagram_username =           # Instagram login (optional)
instagram_password =           # Instagram login (optional)
hikerapi_token =               # https://hikerapi.com — 100 free requests
abstractapi_key =              # https://abstractapi.com — phone/email
hunterio_key =                 # https://hunter.io — email
numverify_key =                # https://numverify.com — phone
ipinfo_key = cbbc0cdfa88a63   # https://ipinfo.io — IP (free)
shodan_key =                   # https://shodan.io — domain/IP
```

### Interactive Mode

```bash
python main.py
```

Starts interactive mode with a numbered menu. Type a number (1-9) or a command name.

```
  [1] Instagram OSINT
  [2] Phone Number Lookup
  [3] Email Lookup
  [4] Username Search (25+ platforms)
  [5] IP / Domain Lookup
  [6] DDoS Attack Menu
  [7] SMS Bomber Menu
  [8] Help / All Commands
  [9] Clear Screen
  [0] Exit
```

### CLI Usage

```bash
python main.py ig username           # Instagram info
python main.py phone +905551234567   # Phone lookup
python main.py email user@site.com   # Email lookup
python main.py username john         # Username search
python main.py ip 8.8.8.8           # IP lookup
python main.py domain example.com    # Domain lookup
python main.py ddos                  # DDoS interactive menu
python main.py ddos http://target.com GET 100 30  # Direct DDoS
python main.py ddos-list             # List DDoS methods
python main.py sms                   # SMS bomber interactive menu
python main.py sms 905551234567 5    # Direct SMS bomb
python main.py sms-list              # List SMS services
python main.py menu                  # Show numbered main menu
```

### Commands

#### Instagram (login required)
| Command | Description |
|---------|-------------|
| `ig` / `info` | Target profile info |
| `followers` | Get followers |
| `following` | Get following |
| `analysis` | Follow + post analysis |
| `photos` | Download photos |
| `stories` | Download stories |
| `hashtags` | Hashtag analysis |
| `locations` | Location extraction |
| `comments` | Extract comments |
| `mutual` | Mutual followers |
| `tagged` | Tagged info |
| `igemail` | Scrape emails from followers |
| `igphone` | Scrape phones from followers |
| `propic` | Download profile picture |
| `report` | Generate HTML+JSON report |

#### Instagram (no login)
| Command | Description |
|---------|-------------|
| `scrape` | Public profile scrape (limited) |

#### DDoS Module
Interactive menu with Layer7 (GET, POST, HEAD, NULL, COOKIE, PPS, BYPASS, SLOW, DYN, BOT, STRESS) and Layer4 (TCP, UDP, SYN) methods + Tools submenu (CFIP, DNS, PING, CHECK, DSTAT).

| Command | Description |
|---------|-------------|
| `ddos` | Interactive DDoS menu (opens menu if no args) |
| `ddos <url> <method> <threads> <duration>` | Direct attack |
| `ddos-list` | List all available attack methods |

#### SMS Bomber
Interactive menu for Turkish phone numbers. Supports 41+ services (Trendyol, Hepsiburada, Sahibinden, etc.) with Normal and Turbo modes.

| Command | Description |
|---------|-------------|
| `sms` | Interactive SMS bomber menu (opens menu if no args) |
| `sms <phone> <count>` | Direct bombing |
| `sms-list` | List available SMS services |

#### Other Modules
| Command | Description |
|---------|-------------|
| `phone` | Phone number lookup (numverify/abstractapi + local carrier detection) |
| `email` | Email lookup (hunter.io + gravatar) |
| `username` | Search username on 25+ platforms |
| `ip` | IP geolocation + DNS |
| `domain` | Domain WHOIS + DNS |
| `web` | IP/Domain combined lookup |
| `menu` | Show numbered main menu |

### Notes
- Instagram module **requires login** (API or HikerAPI) for most features.
- `hikerapi_token` is required for Instagram features.
- Phone module uses numverify + local prefix matching for carrier info.
- Yellow-marked platforms in username search use page source detection, may have false positives.
- DDoS and SMS modules are for educational/testing purposes only.

---

## Türkçe

### Kurulum

```bash
git clone https://github.com/em1rhan-0312/0312-OSINT.git
cd 0312-OSINT
pip install -r requirements.txt
```

### Yapılandırma

`config/credentials.ini` dosyasını düzenleyin:

```ini
[Credentials]
instagram_username =           # Instagram giriş (opsiyonel)
instagram_password =           # Instagram giriş (opsiyonel)
hikerapi_token =               # https://hikerapi.com — 100 ücretsiz istek
abstractapi_key =              # https://abstractapi.com — telefon/email
hunterio_key =                 # https://hunter.io — email
numverify_key =                # https://numverify.com — telefon
ipinfo_key = cbbc0cdfa88a63   # https://ipinfo.io — IP (ücretsiz)
shodan_key =                   # https://shodan.io — domain/IP
```

### Interaktif Mod

```bash
python main.py
```

Numaralı menü ile interaktif mod başlar. Menüden sayı seçebilir veya komut yazabilirsiniz.

```
  [1] Instagram OSINT
  [2] Telefon Sorgulama
  [3] Email Sorgulama
  [4] Kullanıcı Adı Arama (25+ platform)
  [5] IP / Domain Sorgulama
  [6] DDoS Saldırı Menüsü
  [7] SMS Bombardıman Menüsü
  [8] Yardım / Tüm Komutlar
  [9] Ekranı Temizle
  [0] Çıkış
```

### Kullanım

```bash
python main.py ig kullanici_adi    # Instagram bilgileri
python main.py phone +905551234567 # Telefon sorgu
python main.py email mail@site.com # Email sorgu
python main.py username john       # Kullanıcı adı sorgu
python main.py ip 8.8.8.8         # IP sorgu
python main.py domain site.com     # Domain sorgu
python main.py ddos                # DDoS interaktif menü
python main.py ddos http://hedef.com GET 100 30  # Direkt DDoS
python main.py ddos-list           # DDoS metod listesi
python main.py sms                 # SMS interaktif menü
python main.py sms 905551234567 5  # Direkt SMS bombalama
python main.py sms-list            # SMS servis listesi
python main.py menu                # Numaralı ana menü
```

### Komutlar

#### Instagram (giriş gerektirir)
| Komut | Açıklama |
|-------|----------|
| `ig` / `info` | Hedef profil bilgileri |
| `followers` | Takipçi listesi |
| `following` | Takip edilenler |
| `analysis` | Takip analizi + gönderi analizi |
| `photos` | Fotoğraf indirme |
| `stories` | Hikaye indirme |
| `hashtags` | Hashtag analizi |
| `locations` | Konum bilgileri |
| `comments` | Yorum çekme |
| `mutual` | Ortak takipçiler |
| `tagged` | Etiketlenme bilgileri |
| `igemail` | Takipçilerden email kazıma |
| `igphone` | Takipçilerden telefon kazıma |
| `propic` | Profil resmi indirme |
| `report` | HTML+JSON rapor oluşturma |

#### Instagram (giriş gerektirmez)
| Komut | Açıklama |
|-------|----------|
| `scrape` | Genel profil kazıma (sınırlı) |

#### DDoS Modülü
Interaktif menü ile Layer7 (GET, POST, HEAD, NULL, COOKIE, PPS, BYPASS, SLOW, DYN, BOT, STRESS) ve Layer4 (TCP, UDP, SYN) metodları + Tools alt menüsü (CFIP, DNS, PING, CHECK, DSTAT).

| Komut | Açıklama |
|-------|----------|
| `ddos` | Interaktif DDoS menüsü (argsız açılır) |
| `ddos <url> <method> <threads> <sure>` | Direkt saldırı |
| `ddos-list` | Tüm metodları listele |

#### SMS Bombardımanı
Türkiye telefon numaraları için interaktif menü. 41+ servis desteği (Trendyol, Hepsiburada, Sahibinden, vb.) Normal ve Turbo modları.

| Komut | Açıklama |
|-------|----------|
| `sms` | Interaktif SMS menüsü (argsız açılır) |
| `sms <telefon> <adet>` | Direkt bombalama |
| `sms-list` | SMS servislerini listele |

#### Diğer Modüller
| Komut | Açıklama |
|-------|----------|
| `phone` | Telefon numarası sorgulama (numverify/abstractapi + yerel operatör tespiti) |
| `email` | Email sorgulama (hunter.io + gravatar) |
| `username` | 25+ platformda kullanıcı adı arama |
| `ip` | IP konum + DNS sorgulama |
| `domain` | Domain WHOIS + DNS sorgulama |
| `web` | IP/Domain birleşik sorgulama |
| `menu` | Numaralı ana menüyü göster |

### Platformlar (Username Search)

- Yeşil `[+]` — API/404 ile doğrulanmış: Instagram, Twitter/X, GitHub, Reddit, TikTok, Pinterest, Snapchat, Telegram, Steam
- Sarı `[~]` — Manuel kontrol gerekli: OnlyFans, Discord, Facebook, YouTube, LinkedIn, Twitch, Tumblr, VK, Flickr, Medium, Roblox, Fiverr, SoundCloud, Badoo

### Notlar

- Instagram modülü çoğu özellik için **giriş yapmayı gerektirir** (API veya HikerAPI).
- `hikerapi_token` olmadan Instagram özellikleri çalışmaz.
- Telefon modülü operatör bilgisi için numverify + yerel prefix eşleştirmesi kullanır.
- Username search'te sarı işaretli platformlar sayfa kaynağına göre tespit edilir, yanlış pozitif olabilir.
- DDoS ve SMS modülleri yalnızca eğitim/test amaçlıdır.
