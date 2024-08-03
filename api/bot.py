import telebot
import requests
import os

BOT_TOKEN = '7290596696:AAGESr3fGHQNUbM_e8T9ohAnm9Hj-4wYuHo'
ADMIN_CHAT_ID = '1695092646'

if BOT_TOKEN is None or ADMIN_CHAT_ID is None:
    raise ValueError("BOT_TOKEN and ADMIN_CHAT_ID environment variables must be set.")

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}  # Consider using persistent storage for production
user_gigas_added = {}  # Consider using persistent storage for production

# --- Command Handlers ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "مرحبا بيك في بوت الأنترنيت المجاني! 👋\n\nباش تحصل على 1 جيڨا انترنت مجانا، لازم تكون مشترك في قناتنا.\n\nاشترك هنا 👇 ثم أرسل /get_internet\nhttps://t.me/med_info_official\n\nبعد الاشتراك، أرسل /get_internet وابعثلي رقم تيليفونك.")


@bot.message_handler(commands=['get_internet'])
def get_internet(message):
    bot.send_message(message.chat.id, "أدخل نيمرو تيليفون تاعك تاع أوريدو (مثال: 05xxxxxxxx): 📱")
    bot.register_next_step_handler(message, process_phone_number)

# --- Message Handlers ---
def process_phone_number(message):
    phone_number = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/4.9.3'
    }

    data = {
        'client_id': 'ibiza-app',
        'grant_type': 'password',
        'mobile-number': phone_number,
        'language': 'AR'
    }

    response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)

    if 'ROOGY' in response.text:
        user_data[user_id] = {'phone_number': phone_number}
        bot.send_message(chat_id, "شوف تيليفون تاعك، راهو جاك ميساج فيه لكود، اكتبوا هنا: 🔑")
        bot.register_next_step_handler(message, process_otp)
    else:
        bot.send_message(chat_id, "ما قدرتش نبعثلك الكود. 😕 شوف النومرو مليح وعاود.")

def process_otp(message):
    otp = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    phone_number = user_data[user_id]['phone_number']

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp'
    }

    data = {
        'client_id': 'ibiza-app',
        'otp': otp,
        'grant_type': 'password',
        'mobile-number': phone_number,
        'language': 'AR'
    }

    response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)

    if 'access_token' in response.json():
        access_token = response.json()['access_token']
        grant_internet(user_id, chat_id, access_token) 

        username = message.from_user.username or "No username"
        admin_message = f"New subscription:\nUsername: @{username}\nPhone Number: {phone_number}\nTotal Gigas Added: {user_gigas_added[user_id]}"
        bot.send_message(ADMIN_CHAT_ID, admin_message)
        bot.send_message(chat_id, f"تم اضافة لك {user_gigas_added[user_id]} جيغا 🎉")
    else:
        bot.send_message(chat_id, "الكود ماشي صحيح، عاود مرة أخرى. 🔄")

def grant_internet(user_id, chat_id, access_token):
    url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/mgm/info/apply'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'language': 'AR',
        'request-id': 'ef69f4c6-2ead-4b93-95df-106ef37feefd',
        'flavour-type': 'gms',
        'Content-Type': 'application/json'
    }
    payload = {
        'mgmValue': 'ABC'  
    }

    while True:
        response = requests.post(url, headers=headers, json=payload)
        if 'EU1002' in response.text:  # Success
            bot.send_message(chat_id, "بصحتك 1 جيغا  🎉")
            user_gigas_added[user_id] = user_gigas_added.get(user_id, 0) + 1
        else:
            break  

# --- Vercel Serverless Function Handler ---

def handler(request):
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_json())
        bot.process_new_updates([update])
        return 'ok'
    
    return "Method Not Allowed", 405

# --- Set Webhook on Startup ---

bot.remove_webhook()
time.sleep(0.1)

# Set webhook (replace with your Vercel URL)
webhook_url = 'https://your-vercel-project-url/api/bot'
bot.set_webhook(url=webhook_url)
