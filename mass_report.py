import subprocess
import time
import random
import os
import sys
import json
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ==================== CONFIGURATION ====================
CONFIG = {
    "adb_coords": {
        "menu": (950, 80),
        "report": (500, 400),
        "confirm": (500, 700)
    },
    "delay_between_reports": [3, 7],
    "max_workers": 3,
    "use_selenium": True,
    "use_adb": True,
    "headless": False
}

# ==================== COULEURS ====================
CYAN = '\033[96m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
PURPLE = '\033[95m'
BLUE = '\033[94m'
RESET = '\033[0m'

# ==================== FONCTIONS ADB ====================
def adb_tap(x, y, device=None):
    cmd = ["adb"]
    if device:
        cmd.extend(["-s", device])
    cmd.extend(["shell", "input", "tap", str(x), str(y)])
    subprocess.run(cmd, capture_output=True)

def adb_back(device=None):
    cmd = ["adb"]
    if device:
        cmd.extend(["-s", device])
    cmd.extend(["shell", "input", "keyevent", "KEYCODE_BACK"])
    subprocess.run(cmd, capture_output=True)

def adb_home(device=None):
    cmd = ["adb"]
    if device:
        cmd.extend(["-s", device])
    cmd.extend(["shell", "input", "keyevent", "KEYCODE_HOME"])
    subprocess.run(cmd, capture_output=True)

def get_adb_devices():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    devices = []
    for line in result.stdout.split('\n')[1:]:
        if 'device' in line and 'emulator' not in line:
            devices.append(line.split('\t')[0])
    return devices

# ==================== FONCTIONS SIGNALEMENT ====================
def report_via_adb(phone_number, device=None):
    try:
        coords = CONFIG["adb_coords"]
        subprocess.run([
            "adb", "-s", device,
            "shell", "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", f"whatsapp://send?phone={phone_number}"
        ] if device else [
            "adb", "shell", "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", f"whatsapp://send?phone={phone_number}"
        ], capture_output=True)
        time.sleep(random.uniform(2, 4))
        adb_tap(coords["menu"][0], coords["menu"][1], device)
        time.sleep(random.uniform(0.5, 1.5))
        adb_tap(coords["report"][0], coords["report"][1], device)
        time.sleep(random.uniform(0.5, 1.5))
        adb_tap(coords["confirm"][0], coords["confirm"][1], device)
        time.sleep(random.uniform(1, 2))
        adb_back(device)
        adb_home(device)
        return True
    except Exception as e:
        print(f"{RED}❌ Erreur ADB : {e}{RESET}")
        return False

def report_via_selenium(phone_number, driver):
    try:
        driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")
        time.sleep(random.uniform(3, 5))
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@role="button"][@aria-label="Menu"]'))
        )
        menu.click()
        time.sleep(random.uniform(0.5, 1))
        report_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[text()="Signaler"]'))
        )
        report_btn.click()
        time.sleep(random.uniform(0.5, 1))
        confirm_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Signaler"]'))
        )
        confirm_btn.click()
        time.sleep(random.uniform(1, 2))
        return True
    except Exception as e:
        print(f"{RED}❌ Erreur Selenium : {e}{RESET}")
        return False

# ==================== WORKER ====================
def report_worker(phone_number, count, device=None, driver=None):
    success = 0
    for i in range(count):
        if CONFIG["use_adb"] and device:
            result = report_via_adb(phone_number, device)
        elif CONFIG["use_selenium"] and driver:
            result = report_via_selenium(phone_number, driver)
        else:
            print(f"{RED}❌ Aucune méthode disponible !{RESET}")
            break
        if result:
            success += 1
            print(f"{GREEN}✅ [{i+1}/{count}] Signalement envoyé à {phone_number}{RESET}")
        else:
            print(f"{RED}❌ [{i+1}/{count}] Échec du signalement{RESET}")
        delay = random.uniform(*CONFIG["delay_between_reports"])
        time.sleep(delay)
    return success

# ==================== BANNIÈRE ====================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(f"""
    ╔══════════════════════════════════════════╗
    ║  ███████╗ ██████╗ ██████╗ ██╗██╗   ██╗ ██████╗
    ║  ╚══██╔══╝██╔═══██╗██╔══██╗██║██║   ██║██╔═══██╗
    ║     ██║   ██║   ██║██████╔╝██║██║   ██║██║   ██║
    ║     ██║   ██║   ██║██╔══██╗██║██║   ██║██║   ██║
    ║     ██║   ╚██████╔╝██║  ██║██║╚██████╔╝╚██████╔╝
    ║     ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝  ╚═════╝ 
    ║                                                 
    ║{YELLOW}        MASS REPORT - ZORIUS V2{RESET}
    ║{RED}         ⚠️  USAGE ÉDUCATIF UNIQUEMENT  ⚠️{RESET}
    ╚══════════════════════════════════════════╝
    """)

# ==================== MAIN ====================
def setup_selenium():
    options = Options()
    if CONFIG["headless"]:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    return driver

def main():
    print_banner()
    print(f"{CYAN}📱 1. Entrez le numéro de la cible (sans le +) :{RESET}")
    phone = input(f"{PURPLE}➜ Numéro : {RESET}").strip()
    phone = ''.join(filter(str.isdigit, phone))
    print(f"\n{CYAN}💥 2. Combien de signalements voulez-vous envoyer ?{RESET}")
    count = int(input(f"{PURPLE}➜ Nombre : {RESET}"))
    print(f"\n{CYAN}🔧 3. Combien de threads parallèles ? (défaut : 3){RESET}")
    workers = int(input(f"{PURPLE}➜ Threads : {RESET}") or 3)
    CONFIG["max_workers"] = workers
    print(f"\n{CYAN}📡 4. Choisissez la méthode de signalement :{RESET}")
    print("   1. ADB (Android connecté en USB) - RECOMMANDÉ")
    print("   2. Selenium (WhatsApp Web) - NÉCESSITE SCAN QR")
    print("   3. Hybride (les deux)")
    method = input(f"{PURPLE}➜ Choix (1-3) : {RESET}")
    CONFIG["use_adb"] = method in ["1", "3"]
    CONFIG["use_selenium"] = method in ["2", "3"]
    devices = []
    if CONFIG["use_adb"]:
        print(f"\n{YELLOW}🔍 Recherche des devices ADB...{RESET}")
        devices = get_adb_devices()
        if not devices:
            print(f"{RED}❌ Aucun device ADB trouvé !{RESET}")
            CONFIG["use_adb"] = False
        else:
            print(f"{GREEN}✅ Device(s) trouvé(s) : {devices}{RESET}")
    drivers = []
    if CONFIG["use_selenium"]:
        print(f"\n{YELLOW}🌐 Préparation de Selenium...{RESET}")
        for i in range(workers):
            try:
                driver = setup_selenium()
                drivers.append(driver)
                driver.get("https://web.whatsapp.com")
                print(f"{YELLOW}⏳ Worker {i+1} : Scannez le QR code avec WhatsApp{RESET}")
                time.sleep(3)
            except Exception as e:
                print(f"{RED}❌ Erreur Selenium : {e}{RESET}")
                CONFIG["use_selenium"] = False
    print(f"\n{RED}⚠️  ATTENTION : Vous allez envoyer {count} signalements à {phone}{RESET}")
    confirm = input(f"{PURPLE}➜ Continuer ? (o/N) : {RESET}").lower()
    if confirm != 'o':
        print(f"{RED}❌ Opération annulée.{RESET}")
        for driver in drivers:
            try: driver.quit()
            except: pass
        return
    print(f"\n{GREEN}🚀 Lancement du signalement massif...{RESET}")
    count_per_worker = count // workers
    remainder = count % workers
    threads = []
    for i in range(workers):
        c = count_per_worker + (1 if i < remainder else 0)
        device = devices[i % len(devices)] if CONFIG["use_adb"] and devices else None
        driver = drivers[i] if CONFIG["use_selenium"] and i < len(drivers) else None
        t = Thread(target=report_worker, args=(phone, c, device, driver))
        t.daemon = True
        t.start()
        threads.append(t)
        time.sleep(0.5)
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print(f"\n{RED}⚠️ Arrêt demandé par l'utilisateur{RESET}")
    for driver in drivers:
        try:
            driver.quit()
        except:
            pass
    print(f"\n{GREEN}✅ Opération terminée.{RESET}")

if __name__ == "__main__":
    main()