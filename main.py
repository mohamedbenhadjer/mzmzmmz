import telebot
import requests
from keep_alive import keep_alive
keep_alive()
# --- Configuration ---
BOT_TOKEN = '7290596696:AAGESr3fGHQNUbM_e8T9ohAnm9Hj-4wYuHo' 

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {} 


# --- Command Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "مرحبا بيك! 👋 إذا حاب تدي أنترنيت، دير /get_internet") 

@bot.message_handler(commands=['get_internet'])
def get_internet(message):
    bot.send_message(message.chat.id, "أدخل نيمرو تيليفون تاعك نتاع أوريدو (مثال: 05xxxxxxxx): 📱") 
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
        bot.send_message(chat_id, "شوف تيليفون تاعك، راهي جاتك ميساج فيها لكود، أدخلها هنا: 🔑")
        bot.register_next_step_handler(message, process_otp)
    else:
        bot.send_message(chat_id, "ما قدرتش نبعث لك الكود. 😕 شوف النيمرو مليح وعاود.")

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

        response = requests.post(url, headers=headers, json=payload)

        if 'EU1002' in response.text:
            bot.send_message(chat_id, "جابولك الأنترنيت! صحة! 🎉") 
        else:
            bot.send_message(chat_id, "عندك الأنترنيت بكري، ولا كاين مشكل. 🤔") 
    else:
        bot.send_message(chat_id, "الكود ماشي صحيح، عاود مرة أخرى. 🔄")

# --- Run the bot ---
bot.polling()
