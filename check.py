import os, requests, hashlib
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://tramits.gencat.cat/ca/tramits/tramits-temes/Prestacio-datencio-social-a-les-persones-amb-discapacitat-PUA?moda=1"
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Secrets
CONTROL_CHAT_ID = os.getenv("TELEGRAM_GROUP_ID")
ALERT_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS").split(",")

# Rpi logs
rpi_value = os.getenv("RPI")
RPI = True if rpi_value and rpi_value.lower() == "true" else False
print(RPI)
# Has per comparar 
BASELINE_HASH = "97d1286704811923721a61098ccd545e93a4d8395dc2f3165add97542aca4f53"

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def log_message(msg: str):
    prefix = "[LOG RPI]" if RPI else "[LOG GH]"
    print(f"{prefix} {timestamp()} {msg}")

def send_alert(chat_id, msg):
    prefix = "[RPI]" if RPI else "[GH]"
    full_msg = f"{prefix} {timestamp()} {msg}"
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": chat_id.strip(), "text": full_msg}
    )

def main():
    now = datetime.now()
    log_message("Iniciant Workflow...")

    html = requests.get(URL).text
    soup = BeautifulSoup(html, "html.parser")

    banner = soup.find("div", {"class": "banner-tramits-xl__info"})
    if banner:
        current_hash = hashlib.sha256(banner.get_text().encode("utf-8")).hexdigest()
        if current_hash != BASELINE_HASH:
            log_message("El bloc d’informació ha canviat, és possible que les PUA estiguin EN TERMINI!")
            send_alert(CONTROL_CHAT_ID, "⚠️ El bloc d’informació ha canviat, és possible que les PUA estiguin EN TERMINI!")
            for uid in ALERT_CHAT_IDS:
                send_alert(uid, "⚠️ ALERTA DIRECTA: El bloc d’informació ha canviat, és possible que les PUA estiguin EN TERMINI!")
    else:
        log_message("No s’ha trobat el div esperat. Avisar a Francesc.")
        send_alert(CONTROL_CHAT_ID, "ℹ️ No s’ha trobat el div esperat. Avisar a Francesc.")

    # Grup sempre rep notificació de l’estat
    if "En termini" in html:
        log_message("El tràmit PUA està EN TERMINI!")
        send_alert(CONTROL_CHAT_ID, "🔔⚠️ ALERTA: El tràmit PUA està EN TERMINI!")
        for uid in ALERT_CHAT_IDS:
            send_alert(uid, "🔔⚠️ ALERTA DIRECTA: El tràmit PUA està EN TERMINI!")
    else:
        log_message("El tràmit PUA NO està EN TERMINI!")
        send_alert(CONTROL_CHAT_ID, "ℹ️ El tràmit no està en termini.")


if __name__ == "__main__":
    main()
