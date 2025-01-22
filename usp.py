import requests
import re
from urllib.parse import quote
from telebot import TeleBot
from config import API_URL, SSIDKE


def postKeApi(device_id, payload):
    url = f'{API_URL}/devices/{device_id}/tasks?connection_request'
    response = requests.post(url, json=payload)
    return response.status_code

# def list_device(bot: TeleBot, message):
#     response = requests.get(f'{API_URL}/devices')
#     if response.status_code == 200:
#         devices = [
#             f"{index+1}. {device.get('_deviceId', {}).get('_Manufacturer', 'Unknown Manufacturer').split()[0]} {device.get('_deviceId', {}).get('_ProductClass', 'Unknown')}"
#             for index, device in enumerate(response.json())
#         ]
#         bot.reply_to(message, f'Perangkat Yang Terhubung:\n\n' + '\n'.join(devices))
#     else:
#         bot.reply_to(message, f'Gagal mengambil data dari API. Status: {response.status_code}')

def handle_wifi(bot: TeleBot, message):
    text = message.text.strip()

    prefiks = {
        'US': r'^US\.(\S+)\.(.*)$',
        'UP': r'^UP\.(\S+)\.(.*)$',
        'USP': r'^USP\.(\S+)\.(.*)\.(.*)$'
    }

    for key, pattern in prefiks.items():
        match = re.match(pattern, text)
        if match:
            device_id = quote(match.group(1))
            if key == 'US':
                wifi_name = match.group(2)
                payload = {"name": "setParameterValues", "parameterValues": [[f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.SSID", wifi_name, "xsd:string"]]}
                status = postKeApi(device_id, payload)
                msg = f'Nama WiFi berhasil diubah menjadi: *{wifi_name}*' if status in [200, 202] else f'Gagal Mengubah SSID WiFi.'
            elif key == 'UP':
                password = match.group(2)
                if len(password) < 8:
                    bot.reply_to(message, '❌ Password minimal 8 karakter')
                    return
                payload = {"name": "setParameterValues", "parameterValues": [[f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.PreSharedKey.1.PreSharedKey", password, "xsd:string"]]}
                status = postKeApi(device_id, payload)
                msg = f'Password WiFi berhasil diubah menjadi: *{password}*' if status in [200, 202] else f'Gagal Mengubah Password WiFi.'
            elif key == 'USP':
                wifi_name, password = match.group(2), match.group(3)
                if len(password) < 8:
                    bot.reply_to(message, '❌ Password minimal 8 karakter')
                    return
                payload = {
                    "name": "setParameterValues",
                    "parameterValues": [
                        [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.SSID", wifi_name, "xsd:string"],
                        [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.PreSharedKey.1.PreSharedKey", password, "xsd:string"]
                    ]
                }
                status = postKeApi(device_id, payload)
                msg = f'SSID dan Password berhasil diubah dengan SSID: *{wifi_name}* dan Password: *{password}*' if status in [200, 202] else f'Gagal mengubah SSID dan password WiFi.'
            bot.reply_to(message, msg)
            return
