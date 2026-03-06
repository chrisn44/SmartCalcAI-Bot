import asyncio
import requests

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"  # Your Telegram chat ID

async def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, json=data)
    print(f"Sent: {text} -> Status: {response.status_code}")

async def spam_test():
    # Send 15 messages rapidly
    for i in range(15):
        await send_message(f"/calc {i}+{i}")
        await asyncio.sleep(0.5)  # Half second delay

asyncio.run(spam_test())