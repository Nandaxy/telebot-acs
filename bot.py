import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
from config import TELEGRAM_TOKEN
from logger import logger
from usp import list_device, handle_wifi
from acs import acs, cek_perangkat, cek_client, reboot_perangkat

bot = telebot.TeleBot(TELEGRAM_TOKEN)
acs_state = {}
monitoring_stop_event = threading.Event()

# /start 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"Pesan /start dari {message.from_user.first_name} - {message.from_user.username}({message.chat.id})")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Ubah Nama Wifi", "Ubah Password")
    markup.add("Ubah Nama WiFi dan Password", "Cek Status Perangkat")
    markup.add("Cek Client", "Reboot Perangkat")
    bot.reply_to(message, "Selamat datang di Bot ACS. Silakan pilih menu:", reply_markup=markup)

# fuction untuk lankah selanjutnya
def fun_step(message, step_key, next_step, prompt):
    chat_id = message.chat.id
    input_value = message.text.strip()
    if len(input_value) >= 1:
        acs_state[chat_id][step_key] = input_value
        acs_state[chat_id]["step"] = next_step
        bot.reply_to(message, prompt)
    else:
        bot.reply_to(message, "Input tidak valid.")

# mulai
@bot.message_handler(func=lambda message: message.text in ["Ubah Nama Wifi", "Ubah Password", "Ubah Nama WiFi dan Password", "Cek Status Perangkat", "Cek Client"])
def start_process(message):
    chat_id = message.chat.id
    if chat_id in acs_state:
        del acs_state[chat_id]
    if message.text == "Ubah Nama Wifi":
        step_type = "input_sn_ssid"
        key = "US"
    elif message.text == "Ubah Password":
        step_type = "input_sn_pw"
        key = "UP"
    elif message.text == "Ubah Nama WiFi dan Password":
        step_type = "input_sn_ssid_pw"
        key = "USP"
    elif message.text == "Cek Client":
        step_type = "input_sn"
        key = "CC"
    else:
      step_type = "input_sn"
      key = "CS"
    acs_state[chat_id] = {"step": step_type, "key": key}
    # print(acs_state)
    bot.reply_to(message, "Silahkan Masukan Serial Number:")

@bot.message_handler(func=lambda message: acs_state.get(message.chat.id, {}).get("step") in ["input_sn_ssid", "input_sn_pw", "input_sn_ssid_pw", "input_sn"])
def serial_number(message):
    step = acs_state[message.chat.id]["step"]
    key = acs_state[message.chat.id]["key"]
    if key == "CS":
      result = cek_perangkat(message.text.strip())
      bot.reply_to(message, result, parse_mode="Markdown",)
      acs_state.pop(message.chat.id, None)
      return
    elif key == "CC":
      pesan_loading = bot.reply_to(message, "Sedang memproses...")
      result = cek_client(message.text.strip())
      bot.edit_message_text(result, message.chat.id, pesan_loading.message_id, parse_mode="Markdown")
      acs_state.pop(message.chat.id, None)
      return
    next_step = "input_ssid" if step != "input_sn_pw" else "input_pw"
    prompt = "Silahkan Masukan Nama Wifi, min 1 karakter:" if step != "input_sn_pw" else "Silahkan Masukan Password WiFi, min 8 karakter:"
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
                bot.reply_to(message, "❌ Perankat tidak ditemukan, Patikan Serial Number anda benar!")
            else:
                bot.reply_to(message, f"❌ Gagal mengubah  SSID dan Password, Coba lain kali")
            acs_state.pop(message.chat.id, None) 
        elif key != "USP":
            
            data = acs_state[message.chat.id]
            result = acs(data)
            # print("code", result)
            
            if result == 200:
               bot.reply_to(message, f"*{input_key}* berhasil diubah menjadi: *{input_value}*.", parse_mode="Markdown")
            elif result == 404:
                bot.reply_to(message, "❌ Perangkat tidak ditemukan, Patikan Serial Number anda benar!")
            else:
                bot.reply_to(message, f"❌ Gagal mengubah {input_key}, Coba lain kali")
            acs_state.pop(message.chat.id, None)
    else:
        if input_key == "Password":
            bot.reply_to(message, f"Silahkan Masukan Password WiFi, min 8 karakter:")
        else:
            bot.reply_to(message, f"{input_key} tidak valid.")
            
# function reboot perangkat 
@bot.message_handler(func=lambda message: message.text == "Reboot Perangkat") 
def start_reboot(message): 
    chat_id = message.chat.id 
    if chat_id in acs_state: 
        del acs_state[chat_id] 
    acs_state[chat_id] = {"step": "reboot"} 
    bot.reply_to(message, "Silahkan Masukan Serial Number:") 
 
# eksekusi rebbot 
@bot.message_handler(func=lambda message: acs_state.get(message.chat.id, {}).get("step") in ["reboot"]) 
def execute_reboot(message): 
    sn = message.text.strip() 
    res = reboot_perangkat(sn) 
    if res == 200: 
        bot.reply_to(message, "Perangkat Berhasil di Reboot") 
    else: 
        bot.reply_to(message, "Gagal Mereboot Perangakat") 
 
# ------------------------ Kode lama --------------------
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
bot.infinity_polling()