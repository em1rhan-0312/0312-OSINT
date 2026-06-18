import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Update all 0312-OSINT references in py files
for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith((".py", ".bat", ".md", ".txt", ".html")):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            new_content = content
            if "0312-OSINT" in content:
                new_content = content.replace("0312-OSINT", "0312-OSINT")
            if "0312osint" in content:
                new_content = new_content.replace("0312osint", "0312osint")
            if "0312-OSINT" in content:
                new_content = new_content.replace("0312-OSINT", "0312-OSINT")
            if new_content != content:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new_content)
                print(f"Updated: {path}")

# Update main.py with new ASCII art
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_art = r"""  _________    ___.   .__            _________                   .___
 /   _____/____\_ |__ |__| ____     /   _____/ ____   ____    __| _
 \_____  \__  \ | __ \|  |/  _ \    \_____  \ /  _ \ /    \  / __ |
 /        \/ __ \| \_\ \  (  <_> )   /        (  <_> )   |  \/ /_/ |
/_______  (____  /___  /__|\____/   /_______  \____/|___|  /\____ |
        \/     \/    \/                     \/           \/      \/"""

new_art = r"""   _____  ___  ___  ___       _____  ___ ___ _  _ ___
  / __\ \/ / |/ / |/ / |     |_   _|_ _/ __| \| |_ _|
  \__ \>  <| ' <| ' <| |__     | |  | |\__ \ .` || |
  |___/_/\_\_|\_\_|\_\____|    |_| |___|___/_|\_|___|"""

content = content.replace(old_art, new_art)

old_banner = """+====================================================================+
|       0312-OSINT v2.0 - Multi-Platform OSINT Framework              |
|       Instagram | Phone | Email | Username | IP | Domain           |
+====================================================================+"""

new_banner = """+====================================================================+
|       0312-OSINT v2.0 - Multi-Platform OSINT Framework             |
|       Instagram | Phone | Email | Username | IP | Domain           |
+====================================================================+"""

content = content.replace(old_banner, new_banner)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated main.py with new ASCII art and banner")
print("Done!")
