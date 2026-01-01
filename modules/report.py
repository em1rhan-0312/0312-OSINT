import json
import csv
import os
from datetime import datetime

class ReportEngine:
    def __init__(self, output_dir, target=""):
        self.output_dir = output_dir
        self.target = target
        self.data = {}

    def add(self, key, value):
        self.data[key] = value

    def save_json(self, filename=None):
        if filename is None:
            filename = f"{self.target}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        return path

    def save_csv(self, key, filename=None):
        if filename is None:
            filename = f"{self.target}_{key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = os.path.join(self.output_dir, filename)
        items = self.data.get(key, [])
        if not items:
            return None
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)
        return path

    def save_html(self, filename=None):
        if filename is None:
            filename = f"{self.target}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path = os.path.join(self.output_dir, filename)

        rows_html = ""
        for k, v in self.data.items():
            val_str = str(v)[:2000]
            rows_html += f"<tr><td><strong>{k}</strong></td><td><pre>{val_str}</pre></td></tr>\n"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>0312-OSINT Report - {self.target}</title>
<style>
body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #e0e0e0; margin: 40px; }}
h1 {{ color: #00ff88; border-bottom: 2px solid #00ff88; padding-bottom: 10px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
th {{ background: #1a1a1a; color: #00ff88; }}
tr:hover {{ background: #1a1a1a; }}
pre {{ margin: 0; white-space: pre-wrap; word-break: break-all; }}
.footer {{ margin-top: 40px; color: #666; font-size: 12px; text-align: center; }}
</style>
</head>
<body>
<h1> 0312-OSINT OSINT Report</h1>
<p>Target: <strong>{self.target}</strong> | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<table>
<tr><th>Field</th><th>Value</th></tr>
{rows_html}
</table>
<div class="footer">0312-OSINT OSINT Framework</div>
</body>
</html>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path
