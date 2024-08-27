import telebot
from telebot import types
import threading
from config import TELEGRAM_TOKEN
from logger import logger
from usp import list_device, handle_wifi
from acs import acs, cek_perangkat

bot = telebot.TeleBot(TELEGRAM_TOKEN)

acs_state = {}

# Event to stop the monitoring thread
monitoring_stop_event = threading.Event()

# /start 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"Pesan /start dari {message.from_user.first_name} - {message.from_user.username}({message.chat.id})")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Ubah Nama Wifi")
    markup.add("Ubah Password")
    markup.add("Ubah Nama WiFi dan Password")
    markup.add("Cek Status Perangkat")
    bot.reply_to(message, "Selamat datang di Bot ACS. Silakan pilih menu:", reply_markup=markup)
    
# fuction lankah selanjutnya
def fun_step(message, step_key, next_step, prompt):
    chat_id = message.chat.id
    input_value = message.text.strip()
    
    if len(input_value) >= 1:
        acs_state[chat_id][step_key] = input_value
        acs_state[chat_id]["step"] = next_step
        # print(acs_state)
        bot.reply_to(message, prompt)
    else:
        bot.reply_to(message, "Input tidak valid.")
# mulai
@bot.message_handler(func=lambda message: message.text in ["Ubah Nama Wifi", "Ubah Password", "Ubah Nama WiFi dan Password", "Cek Status Perangkat"])
def start_process(message):
    chat_id = message.chat.id

    if chat_id in acs_state:
        del acs_state[chat_id]
        
    if message.text == "Ubah Nama Wifi":
        key = "US"
    elif message.text == "Ubah Password":
        key = "UP"
    elif message.text == "Ubah Nama WiFi dan Password":
        key = "USP"
    else:
        key = "CS"
    
    acs_state[chat_id] = {"step": "input_sn", "key": key}
    # print(acs_state)
    bot.reply_to(message, "Silahkan Masukan Serial Number:")

@bot.message_handler(func=lambda message: acs_state.get(message.chat.id, {}).get("step") in ["input_sn"])
def serial_number(message):
    key = acs_state[message.chat.id]["key"]
    
    if key == "CS":
      result = cek_perangkat(message.text.strip())
      bot.reply_to(message, result, parse_mode="Markdown")
      acs_state.pop(message.chat.id, None)
      return
    
    next_step = "input_ssid" if key != "UP" else "input_pw"
    prompt = "Silahkan Masukan Nama Wifi, min 1 karakter:" if key != "UP" else "Silahkan Masukan Password WiFi, min 8 karakter:"
    
    fun_step(message, "sn", next_step, prompt)

@bot.message_handler(func=lambda message: acs_state.get(message.chat.id, {}).get("step") in ["input_ssid", "input_pw"])
def final_input(message):
    step = acs_state[message.chat.id]["step"]
    key = acs_state[message.chat.id]["key"]
    
    if key == "USP" and step == "input_ssid":
        return fun_step(message, "ssid", "input_pw", "Silahkan Masukan Password WiFi, min 8 karakter:")
    
    input_key = "SSID" if step == "input_ssid" else "Password"
    input_value = message.text.strip()
    
    
    if len(input_value) >= (1 if step == "input_ssid" else 8):
        acs_state[message.chat.id][input_key.lower()] = input_value
        
        if key == "USP" and step == "input_pw":
            ssid = acs_state[message.chat.id]["ssid"]
            data = acs_state[message.chat.id]
            result = acs(data)
            
            if result == 200:
                bot.reply_to(message, f"SSID dan Password berhasil diubah. SSID: *{ssid}*, Password: *{input_value}*.", parse_mode="Markdown")
            elif result == 404:
                bot.reply_to(message, "❌ Gagal Mengubah. *Patikan Serial Number anda benar!*", parse_mode="Markdown")
            else:
                bot.reply_to(message, f"❌ Gagal mengubah  SSID dan Password, Coba lain kali")
            acs_state.pop(message.chat.id, None) 
            
        elif key != "USP":
            data = acs_state[message.chat.id]
            result = acs(data)
            print("code", result)
            
            if result == 200:
               bot.reply_to(message, f"*{input_key}* berhasil diubah menjadi: *{input_value}*.", parse_mode="Markdown")
            elif result == 404:
                bot.reply_to(message, "❌ Gagal Mengubah. *Patikan Serial Number anda benar!*", parse_mode="Markdown")
            else:
                bot.reply_to(message, f"❌ Gagal mengubah {input_key}, Coba lain kali")
            acs_state.pop(message.chat.id, None)
    else:
        if input_key == "Password":
            bot.reply_to(message, f"Silahkan Masukan Password WiFi, min 8 karakter:")
        else:
            bot.reply_to(message, f"{input_key} tidak valid.")      

# /list - List devices
@bot.message_handler(commands=['list'])
def list_devices_handler(message):
    list_device(bot, message)

# /help
@bot.message_handler(commands=['help'])
def help(message):
    help_text = (
        "Beberapa Perintah yang dapat digunakan:\n"
        "/start - Start\n"
        "/list - Menampilkan daftar perangkat yang terhubung\n"
        "US.(Serial Number).(wifi) - Mengubah SSID WiFi\n"
        "UP.(Serial Number).(password) - Mengubah password WiFi\n"
        "USP.(Serial Number).(wifi).(password) - Mengubah SSID dan password WiFi"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

# /info
@bot.message_handler(commands=['info'])
def infokan(message):
    bot.reply_to(message, f'Info Akun Anda:\nUsername: `{message.from_user.username}`\nChatID: `{message.chat.id}`', parse_mode='Markdown')
    
# WiFi setting berformat US,UP,USP
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_wifi_message(message):
    handle_wifi(bot, message)

# Start bot
print("Bot Jalan...")
bot.polling()