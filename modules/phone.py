import json
import urllib.request
import urllib.parse
import re

from . import config_loader as cfg
from . import display as disp
from .report import ReportEngine

COUNTRY_CODES = {
    "1": {"name": "US/CA", "len": 10},
    "7": {"name": "Russia", "len": 10},
    "20": {"name": "Egypt", "len": 10},
    "27": {"name": "South Africa", "len": 9},
    "30": {"name": "Greece", "len": 10},
    "31": {"name": "Netherlands", "len": 9},
    "32": {"name": "Belgium", "len": 9},
    "33": {"name": "France", "len": 9},
    "34": {"name": "Spain", "len": 9},
    "36": {"name": "Hungary", "len": 9},
    "39": {"name": "Italy", "len": 10},
    "40": {"name": "Romania", "len": 9},
    "41": {"name": "Switzerland", "len": 9},
    "43": {"name": "Austria", "len": 10},
    "44": {"name": "UK", "len": 10},
    "45": {"name": "Denmark", "len": 8},
    "46": {"name": "Sweden", "len": 9},
    "47": {"name": "Norway", "len": 8},
    "48": {"name": "Poland", "len": 9},
    "49": {"name": "Germany", "len": 10},
    "51": {"name": "Peru", "len": 9},
    "52": {"name": "Mexico", "len": 10},
    "53": {"name": "Cuba", "len": 8},
    "54": {"name": "Argentina", "len": 10},
    "55": {"name": "Brazil", "len": 10},
    "56": {"name": "Chile", "len": 9},
    "57": {"name": "Colombia", "len": 10},
    "58": {"name": "Venezuela", "len": 10},
    "60": {"name": "Malaysia", "len": 9},
    "61": {"name": "Australia", "len": 9},
    "62": {"name": "Indonesia", "len": 10},
    "63": {"name": "Philippines", "len": 10},
    "64": {"name": "New Zealand", "len": 9},
    "65": {"name": "Singapore", "len": 8},
    "66": {"name": "Thailand", "len": 9},
    "81": {"name": "Japan", "len": 10},
    "82": {"name": "South Korea", "len": 9},
    "84": {"name": "Vietnam", "len": 9},
    "86": {"name": "China", "len": 11},
    "90": {"name": "Turkey", "len": 10},
    "91": {"name": "India", "len": 10},
    "92": {"name": "Pakistan", "len": 10},
    "93": {"name": "Afghanistan", "len": 9},
    "94": {"name": "Sri Lanka", "len": 9},
    "95": {"name": "Myanmar", "len": 9},
    "98": {"name": "Iran", "len": 10},
    "212": {"name": "Morocco", "len": 9},
    "213": {"name": "Algeria", "len": 9},
    "216": {"name": "Tunisia", "len": 8},
    "218": {"name": "Libya", "len": 9},
    "220": {"name": "Gambia", "len": 7},
    "221": {"name": "Senegal", "len": 7},
    "222": {"name": "Mauritania", "len": 7},
    "223": {"name": "Mali", "len": 7},
    "224": {"name": "Guinea", "len": 8},
    "225": {"name": "Ivory Coast", "len": 8},
    "226": {"name": "Burkina Faso", "len": 8},
    "227": {"name": "Niger", "len": 8},
    "228": {"name": "Togo", "len": 8},
    "229": {"name": "Benin", "len": 8},
    "230": {"name": "Mauritius", "len": 7},
    "231": {"name": "Liberia", "len": 7},
    "232": {"name": "Sierra Leone", "len": 7},
    "233": {"name": "Ghana", "len": 9},
    "234": {"name": "Nigeria", "len": 10},
    "235": {"name": "Chad", "len": 8},
    "236": {"name": "Central Africa", "len": 8},
    "237": {"name": "Cameroon", "len": 8},
    "238": {"name": "Cape Verde", "len": 7},
    "239": {"name": "Sao Tome", "len": 7},
    "240": {"name": "Equatorial Guinea", "len": 7},
    "241": {"name": "Gabon", "len": 8},
    "242": {"name": "Congo", "len": 8},
    "243": {"name": "DRC", "len": 9},
    "244": {"name": "Angola", "len": 9},
    "245": {"name": "Guinea-Bissau", "len": 7},
    "246": {"name": "Diego Garcia", "len": 7},
    "247": {"name": "Ascension", "len": 4},
    "248": {"name": "Seychelles", "len": 6},
    "249": {"name": "Sudan", "len": 9},
    "250": {"name": "Rwanda", "len": 8},
    "251": {"name": "Ethiopia", "len": 9},
    "252": {"name": "Somalia", "len": 8},
    "253": {"name": "Djibouti", "len": 8},
    "254": {"name": "Kenya", "len": 9},
    "255": {"name": "Tanzania", "len": 9},
    "256": {"name": "Uganda", "len": 9},
    "257": {"name": "Burundi", "len": 8},
    "258": {"name": "Mozambique", "len": 9},
    "260": {"name": "Zambia", "len": 9},
    "261": {"name": "Madagascar", "len": 9},
    "262": {"name": "Reunion", "len": 9},
    "263": {"name": "Zimbabwe", "len": 9},
    "264": {"name": "Namibia", "len": 9},
    "265": {"name": "Malawi", "len": 8},
    "266": {"name": "Lesotho", "len": 8},
    "267": {"name": "Botswana", "len": 8},
    "268": {"name": "Swaziland", "len": 7},
    "269": {"name": "Comoros", "len": 7},
    "351": {"name": "Portugal", "len": 9},
    "352": {"name": "Luxembourg", "len": 8},
    "353": {"name": "Ireland", "len": 9},
    "354": {"name": "Iceland", "len": 7},
    "355": {"name": "Albania", "len": 9},
    "356": {"name": "Malta", "len": 8},
    "357": {"name": "Cyprus", "len": 8},
    "358": {"name": "Finland", "len": 9},
    "359": {"name": "Bulgaria", "len": 9},
    "370": {"name": "Lithuania", "len": 8},
    "371": {"name": "Latvia", "len": 8},
    "372": {"name": "Estonia", "len": 8},
    "373": {"name": "Moldova", "len": 8},
    "374": {"name": "Armenia", "len": 8},
    "375": {"name": "Belarus", "len": 9},
    "376": {"name": "Andorra", "len": 6},
    "377": {"name": "Monaco", "len": 8},
    "378": {"name": "San Marino", "len": 8},
    "379": {"name": "Vatican", "len": 8},
    "380": {"name": "Ukraine", "len": 9},
    "381": {"name": "Serbia", "len": 9},
    "382": {"name": "Montenegro", "len": 8},
    "385": {"name": "Croatia", "len": 9},
    "386": {"name": "Slovenia", "len": 9},
    "387": {"name": "Bosnia", "len": 8},
    "389": {"name": "North Macedonia", "len": 8},
    "420": {"name": "Czech", "len": 9},
    "421": {"name": "Slovakia", "len": 9},
    "423": {"name": "Liechtenstein", "len": 7},
    "501": {"name": "Belize", "len": 7},
    "502": {"name": "Guatemala", "len": 8},
    "503": {"name": "El Salvador", "len": 8},
    "504": {"name": "Honduras", "len": 8},
    "505": {"name": "Nicaragua", "len": 8},
    "506": {"name": "Costa Rica", "len": 8},
    "507": {"name": "Panama", "len": 8},
    "509": {"name": "Haiti", "len": 8},
    "591": {"name": "Bolivia", "len": 8},
    "592": {"name": "Guyana", "len": 7},
    "593": {"name": "Ecuador", "len": 8},
    "594": {"name": "French Guiana", "len": 9},
    "595": {"name": "Paraguay", "len": 9},
    "596": {"name": "Martinique", "len": 9},
    "597": {"name": "Suriname", "len": 7},
    "598": {"name": "Uruguay", "len": 8},
    "599": {"name": "Dutch Caribbean", "len": 7},
    "670": {"name": "East Timor", "len": 7},
    "672": {"name": "Antarctic", "len": 6},
    "673": {"name": "Brunei", "len": 7},
    "674": {"name": "Nauru", "len": 7},
    "675": {"name": "Papua NG", "len": 8},
    "676": {"name": "Tonga", "len": 5},
    "677": {"name": "Solomon Is", "len": 5},
    "678": {"name": "Vanuatu", "len": 5},
    "679": {"name": "Fiji", "len": 7},
    "680": {"name": "Palau", "len": 7},
    "681": {"name": "Wallis", "len": 6},
    "682": {"name": "Cook Is", "len": 5},
    "683": {"name": "Niue", "len": 4},
    "685": {"name": "Samoa", "len": 6},
    "686": {"name": "Kiribati", "len": 5},
    "687": {"name": "New Caledonia", "len": 6},
    "688": {"name": "Tuvalu", "len": 5},
    "689": {"name": "French Polynesia", "len": 6},
    "690": {"name": "Tokelau", "len": 4},
    "691": {"name": "Micronesia", "len": 7},
    "692": {"name": "Marshall Is", "len": 7},
    "850": {"name": "North Korea", "len": 8},
    "852": {"name": "Hong Kong", "len": 8},
    "853": {"name": "Macau", "len": 8},
    "855": {"name": "Cambodia", "len": 9},
    "856": {"name": "Laos", "len": 9},
    "880": {"name": "Bangladesh", "len": 10},
    "886": {"name": "Taiwan", "len": 9},
    "960": {"name": "Maldives", "len": 7},
    "961": {"name": "Lebanon", "len": 8},
    "962": {"name": "Jordan", "len": 9},
    "963": {"name": "Syria", "len": 9},
    "964": {"name": "Iraq", "len": 10},
    "965": {"name": "Kuwait", "len": 8},
    "966": {"name": "Saudi Arabia", "len": 9},
    "967": {"name": "Yemen", "len": 9},
    "968": {"name": "Oman", "len": 8},
    "970": {"name": "Palestine", "len": 9},
    "971": {"name": "UAE", "len": 9},
    "972": {"name": "Israel", "len": 9},
    "973": {"name": "Bahrain", "len": 8},
    "974": {"name": "Qatar", "len": 8},
    "975": {"name": "Bhutan", "len": 8},
    "976": {"name": "Mongolia", "len": 8},
    "977": {"name": "Nepal", "len": 9},
    "992": {"name": "Tajikistan", "len": 9},
    "993": {"name": "Turkmenistan", "len": 8},
    "994": {"name": "Azerbaijan", "len": 9},
    "995": {"name": "Georgia", "len": 9},
    "996": {"name": "Kyrgyzstan", "len": 9},
    "998": {"name": "Uzbekistan", "len": 9},
}

# Some well-known carriers per country
CARRIER_HINTS = {
    "90": {"name": "Turkey", "prefixes": {
        "530": "Turkcell", "531": "Turkcell", "532": "Turkcell", "533": "Turkcell", "534": "Turkcell",
        "535": "Turkcell", "536": "Turkcell", "537": "Turkcell", "538": "Turkcell", "539": "Turkcell",
        "540": "Vodafone", "541": "Vodafone", "542": "Vodafone", "543": "Vodafone", "544": "Vodafone",
        "545": "Vodafone", "546": "Vodafone", "547": "Vodafone", "548": "Vodafone", "549": "Vodafone",
        "550": "Turk Telekom", "551": "Turk Telekom", "552": "Turk Telekom", "553": "Turk Telekom",
        "554": "Turk Telekom", "555": "Turk Telekom", "556": "Turk Telekom", "557": "Turk Telekom",
        "558": "Turk Telekom", "559": "Turk Telekom",
        "561": "Turkcell", "562": "Turkcell", "563": "Turkcell", "564": "Turkcell", "565": "Turkcell",
        "566": "Vodafone", "567": "Vodafone", "568": "Vodafone", "569": "Turk Telekom",
    }},
    "44": {"name": "UK", "prefixes": {
        "7700": "EE", "7711": "EE", "7722": "EE", "7733": "EE", "7744": "EE",
        "7755": "Vodafone", "7766": "Vodafone", "7777": "Vodafone", "7788": "Vodafone",
        "7799": "O2", "7800": "O2", "7801": "O2", "7802": "O2",
        "7900": "Three", "7901": "Three", "7902": "Three",
    }},
    "49": {"name": "Germany", "prefixes": {
        "151": "T-Mobile", "152": "Vodafone", "155": "O2", "157": "E-Plus", "159": "O2",
        "160": "T-Mobile", "162": "Vodafone", "163": "T-Mobile", "170": "T-Mobile",
        "171": "T-Mobile", "172": "T-Mobile", "173": "T-Mobile", "174": "T-Mobile",
        "175": "T-Mobile", "176": "O2", "177": "O2", "178": "O2", "179": "O2",
    }},
}

def detect_country(phone):
    phone = re.sub(r'[^\d+]', '', phone)
    phone = phone.lstrip("+")
    for length in range(5, 1, -1):
        cc = phone[:length]
        if cc in COUNTRY_CODES:
            info = COUNTRY_CODES[cc]
            rest = phone[length:]
            return {
                "country_code": f"+{cc}",
                "country_name": info["name"],
                "national_number": rest,
                "expected_length": info["len"],
            }
    return None

def detect_carrier(phone):
    phone = re.sub(r'[^\d+]', '', phone)
    phone = phone.lstrip("+")
    for cc_len in range(5, 1, -1):
        cc = phone[:cc_len]
        if cc in CARRIER_HINTS:
            rest = phone[cc_len:]
            carrier_info = CARRIER_HINTS[cc]
            for prefix in sorted(carrier_info["prefixes"].keys(), key=len, reverse=True):
                if rest.startswith(prefix):
                    return carrier_info["prefixes"][prefix]
    return None

class PhoneOSINT:
    def __init__(self):
        self.report = ReportEngine("output", "phone_lookup")

    def lookup(self, phone_number):
        disp.pheader(f"PHONE LOOKUP: {phone_number}")

        original = phone_number.strip()
        phone_number = re.sub(r'[\s\-\(\)]', '', phone_number)

        info = detect_country(phone_number)
        carrier = detect_carrier(phone_number)

        results = {
            "phone": original,
            "parsed": {},
            "sources": {}
        }

        if info:
            results["parsed"] = info
            if carrier:
                info["possible_carrier"] = carrier

            disp.pout(f"  [LOCAL DETECTION]\n", disp.BLUE, bold=True)
            disp.pout(f"    Country: {info['country_name']} ({info['country_code']})\n")
            disp.pout(f"    National: {info['national_number']}\n")
            if carrier:
                disp.pout(f"    Possible Carrier: {carrier}\n", disp.GREEN)
            if len(info['national_number']) != info['expected_length']:
                disp.pout(f"    [!] Number length: {len(info['national_number'])} (expected {info['expected_length']})\n", disp.YELLOW)

        self._check_numverify(phone_number, results)
        self._check_abstractapi(phone_number, results)

        disp.psep()
        disp.pout(f"  Phone: {original}\n", disp.CYAN, bold=True)

        info = results.get("parsed", {})
        if info:
            disp.pout("  [Local Detection]\n", disp.BLUE, bold=True)
            for k, v in info.items():
                key = k.replace("_", " ").title()
                disp.pout(f"    {key}: {v}\n")

        for source, data in results["sources"].items():
            disp.pout(f"  [{source}]\n", disp.BLUE, bold=True)
            for k, v in data.items():
                if v:
                    key = k.replace("_", " ").title()
                    color = disp.GREEN if k == "valid" and v else disp.RED if k == "valid" else disp.WHITE
                    disp.pout(f"    {key}: {v}\n", color)

        self.report.add("phone_lookup", results)
        return results

    def _check_numverify(self, phone, results):
        key = cfg.get_api_key("numverify_key")
        if not key:
            disp.pout("  [*] numverify: no API key\n", disp.YELLOW)
            return

        try:
            url = f"https://apilayer.net/api/validate?access_key={key}&number={phone}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())

            if data.get("valid"):
                entry = {"valid": True}
                for k in ["country_name", "country_code", "carrier", "line_type", "location"]:
                    v = data.get(k)
                    if v:
                        entry[k.replace("_", " ").title()] = v
                results["sources"]["numverify"] = entry
                country = data.get("country_name", "")
                carrier = data.get("carrier", "")
                extra = f" - {carrier}" if carrier else ""
                disp.pout(f"  [+] numverify: {country}{extra}\n", disp.GREEN)
            else:
                results["sources"]["numverify"] = {"valid": False}
                disp.pout(f"  [-] numverify: invalid number\n", disp.RED)
        except Exception as e:
            disp.pout(f"  [!] numverify error: {e}\n", disp.RED)

    def _check_abstractapi(self, phone, results):
        key = cfg.get_api_key("abstractapi_key")
        if not key:
            return

        try:
            url = f"https://phonevalidation.abstractapi.com/v1/?api_key={key}&phone={phone}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())

            if data.get("valid"):
                entry = {"valid": True}
                for k in ["country", "location", "carrier", "line_type"]:
                    v = data.get(k)
                    if isinstance(v, dict):
                        v = v.get("name", "")
                    if v:
                        entry[k.replace("_", " ").title()] = v
                results["sources"]["abstractapi"] = entry
                country = data.get("country", {})
                if isinstance(country, dict):
                    country = country.get("name", "")
                carrier = data.get("carrier", "")
                extra = f" - {carrier}" if carrier else ""
                disp.pout(f"  [+] abstractapi: {country}{extra}\n", disp.GREEN)
        except Exception:
            pass
