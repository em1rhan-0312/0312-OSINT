# 0312-OSINT 

Multi-Platform OSINT Framework — Instagram | Phone | Email | Username | IP | Domain

---

## English

### Installation

```bash
git clone https://github.com/yourusername/0312-OSINT.git
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

### Usage

```bash
python main.py                    # Interactive mode
python main.py ig username        # Instagram info
python main.py phone +905551234567 # Phone lookup
python main.py email user@site.com # Email lookup
python main.py username john      # Username search (25+ platforms)
python main.py ip 8.8.8.8        # IP lookup
python main.py domain example.com # Domain lookup
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

#### Other Modules
| Command | Description |
|---------|-------------|
| `phone` | Phone number lookup (numverify/abstractapi + local carrier detection) |
| `email` | Email lookup (hunter.io + gravatar) |
| `username` | Search username on 25+ platforms |
| `ip` | IP geolocation + DNS |
| `domain` | Domain WHOIS + DNS |
| `web` | IP/Domain combined lookup |

### Notes
- Instagram module **requires login** (API or HikerAPI) for most features.
- `hikerapi_token` is required for Instagram features.
- Phone module uses numverify + local prefix matching for carrier info.
- Yellow-marked platforms in username search use page source detection, may have false positives.

---

## Türkçe

### Kurulum

```bash
git clone https://github.com/yourusername/0312-OSINT.git
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

### Kullanım

```bash
python main.py                    # Interactive mod
python main.py ig kullanici_adi   # Instagram bilgileri
python main.py phone +905551234567 # Telefon sorgu
python main.py email mail@site.com # Email sorgu
python main.py username john      # Kullanıcı adı sorgu (25+ platform)
python main.py ip 8.8.8.8        # IP sorgu
python main.py domain site.com    # Domain sorgu
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

#### Diğer Modüller
| Komut | Açıklama |
|-------|----------|
| `phone` | Telefon numarası sorgulama (numverify/abstractapi + yerel operatör tespiti) |
| `email` | Email sorgulama (hunter.io + gravatar) |
| `username` | 25+ platformda kullanıcı adı arama |
| `ip` | IP konum + DNS sorgulama |
| `domain` | Domain WHOIS + DNS sorgulama |
| `web` | IP/Domain birleşik sorgulama |

### Platformlar (Username Search)

- Yeşil `[+]` — API/404 ile doğrulanmış: Instagram, Twitter/X, GitHub, Reddit, TikTok, Pinterest, Snapchat, Telegram, Steam
- Sarı `[~]` — Manuel kontrol gerekli: OnlyFans, Discord, Facebook, YouTube, LinkedIn, Twitch, Tumblr, VK, Flickr, Medium, Roblox, Fiverr, SoundCloud, Badoo

### Notlar

- Instagram modülü çoğu özellik için **giriş yapmayı gerektirir** (API veya HikerAPI).
- `hikerapi_token` olmadan Instagram özellikleri çalışmaz.
- Telefon modülü operatör bilgisi için numverify + yerel prefix eşleştirmesi kullanır.
- Username search'te sarı işaretli platformlar sayfa kaynağına göre tespit edilir, yanlış pozitif olabilir.
