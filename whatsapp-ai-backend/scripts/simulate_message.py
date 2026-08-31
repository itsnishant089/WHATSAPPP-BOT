import os
import json
import hmac
import hashlib
import httpx
from dotenv import load_dotenv

load_dotenv()

def send_simulated_message(sender_phone: str, message_text: str):
    # This simulates the payload structure that Meta/WhatsApp sends to your webhook
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID_SIMULATED",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "BOT_PHONE",
                                "phone_number_id": "BOT_PHONE_ID"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Test User"},
                                    "wa_id": sender_phone
                                }
                            ],
                            "messages": [
                                {
                                    "from": sender_phone,
                                    "id": f"wamid.{os.urandom(8).hex()}",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": message_text}
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

    body = json.dumps(payload).encode('utf-8')
    secret = os.environ.get("META_APP_SECRET", "")
    
    if not secret:
        print("Error: META_APP_SECRET is not set in .env")
        return

    # Calculate HMAC signature required by the backend
    signature = hmac.new(secret.encode('utf-8'), body, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}"
    }

    url = "http://127.0.0.1:8000/webhook/whatsapp"
    print(f"Sending message '{message_text}' from {sender_phone} to {url}...")
    
    try:
        response = httpx.post(url, content=body, headers=headers, timeout=30.0)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    import sys
    
    sender = "9992507270"
    text = "Hello, what is LEET?"
    
    if len(sys.argv) > 1:
        text = sys.argv[1]
    if len(sys.argv) > 2:
        sender = sys.argv[2]
        
    send_simulated_message(sender, text)
