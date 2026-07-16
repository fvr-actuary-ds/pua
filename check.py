import os, requests, hashlib
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://tramits.gencat.cat/ca/tramits/tramits-temes/Prestacio-datencio-social-a-les-persones-amb-discapacitat-PUA?moda=1"
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Secrets
CONTROL_CHAT_ID = os.getenv("TELEGRAM_GROUP_ID")
ALERT_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS").split(",")

BASELINE_HASH = "97d1286704811923721a61098ccd545e93a4d8395dc2f3165add97542aca4f53"

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def send_alert(chat_id, msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": chat_id.strip(), "text": f"{timestamp()} {msg}"}
    )

def main():
    now = datetime.now()
    print(f"ℹ[LOG] Workflow executat a {now.strftime('%Y-%m-%d %H:%M:%S')} CEST")

    html = requests.get(URL).text
    soup = BeautifulSoup(html, "html.parser")

    banner = soup.find("div", {"class": "banner-tramits-xl__info"})
    if banner:
        current_hash = hashlib.sha256(banner.get_text().encode("utf-8")).hexdigest()
        if current_hash != BASELINE_HASH:
            print("[LOG] El bloc d’informació ha canviat, és possible que les PUA estiguin EN TERMINI!")
            send_alert(CONTROL_CHAT_ID, "⚠️ El bloc d’informació ha canviat, és possible que les PUA estiguin EN TERMINI!")
            for uid in ALERT_CHAT_IDS:
                send_alert(uid, "⚠️ ALERTA DIRECTA: El bloc d’informació ha canviat, és possible que les PUA estiguin EN TERMINI!")
    else:
        print("ℹ[LOG] No s’ha trobat el div esperat. Avisar a Francesc.")
        send_alert(CONTROL_CHAT_ID, "ℹ️ No s’ha trobat el div esperat. Avisar a Francesc.")

    # Grup sempre rep notificació de l’estat
    if "En termini" in html:
        print("[LOG] El tràmit PUA està EN TERMINI!")
        send_alert(CONTROL_CHAT_ID, "🔔⚠️ ALERTA: El tràmit PUA està EN TERMINI!")
        for uid in ALERT_CHAT_IDS:
            send_alert(uid, "🔔⚠️ ALERTA DIRECTA: El tràmit PUA està EN TERMINI!")
    else:
        print("[LOG] El tràmit PUA NO està en termini.")
        send_alert(CONTROL_CHAT_ID, "ℹ️ El tràmit no està en termini.")


if __name__ == "__main__":
    main()
