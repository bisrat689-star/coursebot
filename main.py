# --- AGORATUBE TELEGRAM BOT (FINAL, WITH RESPONSE LOGGING) ---
import os
import requests
from flask import Flask, request

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

WELCOME_MESSAGE = """
Hello! Welcome to the AgoraTube AI Website Course.

To get instant access, please follow these simple payment steps:

**Course Price:** 2,000 ETB

**Payment Options:**

**1. CBE (Commercial Bank of Ethiopia):**
   - **Account Name:** Bisrat Tadesse
   - **Account Number:** 1000539889102

**2. Telebirr:**
   - **Account Number:** +251930551468

After you have made the payment, please send a screenshot of the transaction to this chat.

Once I confirm the payment, I will send you the private invitation link to the course group.

Thank you!
"""

# --- WEB SERVER SETUP ---
app = Flask(__name__)

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def respond():
    try:
        update = request.get_json()

        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user = message.get('from', {})
            
            # --- HANDLE PHOTOS ---
            if 'photo' in message:
                print("--> Photo received. Preparing to forward.")
                photo_file_id = message['photo'][-1]['file_id']
                
                caption = f"New payment proof received!\n\n"
                caption += f"From: {user.get('first_name', '')}"
                if user.get('last_name'):
                    caption += f" {user.get('last_name')}"
                if user.get('username'):
                    caption += f" (@{user.get('username')})"
                
                forward_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
                forward_payload = {
                    'chat_id': ADMIN_CHAT_ID,
                    'photo': photo_file_id,
                    'caption': caption
                }
                # Send the photo and get the response from Telegram
                response = requests.post(forward_url, json=forward_payload)
                # Print the response to the log for debugging
                print(f"--> Telegram API response for forwarding: {response.json()}")
                
                reply_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                reply_payload = {
                    'chat_id': chat_id,
                    'text': "Thank you! Your proof has been submitted for review. You will receive the group link shortly after confirmation."
                }
                requests.post(reply_url, json=reply_payload)

            # --- HANDLE TEXT MESSAGES ---
            elif 'text' in message:
                text = message['text']
                if text == "/start":
                    reply_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                    reply_payload = {
                        'chat_id': chat_id,
                        'text': WELCOME_MESSAGE,
                        'parse_mode': 'Markdown'
                    }
                    requests.post(reply_url, json=reply_payload)

    except Exception as e:
        print(f"--> An error occurred: {e}")

    return 'ok'

@app.route('/')
def index():
    return 'Server is running!'
