# Parameter SSID Mikrotik = Device.WiFi.SSID.1.SSID
# Parameter Password Mikrotik = Device.WiFi.AccessPoint.1.Security.KeyPassphrase
# Onu SSID = InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.SSID
# onu Pw =  InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.PreSharedKey.1.PreSharedKey
import requests
from config import API_URL, SSIDKE
from logger import logger
from urllib.parse import quote
from datetime import datetime, timedelta

def postKeApi(device_id, payload):
    url = f'{API_URL}/devices/{device_id}/tasks?connection_request'
    r = requests.post(url, json=payload)
    return r.status_code

def cek_perangkat(sn):
  try:
    id = quote(sn)
    res = requests.get(f'{API_URL}/devices/?query=%7B%22_id%22%3A%22{id}%22%7D')
    data = res.json()

    if data:
      # print("code:", res.status_code)
      status = "🟢 Online"
      julahClient = 0

      terakhirAktif = data[0]["_lastInform"]  # isi data : 2024-09-30T10:08:02.319Z
      terakhirAktif_dt = datetime.fromisoformat(terakhirAktif[:-1])
      sekarang = datetime.utcnow()  

      selisih_waktu = sekarang - terakhirAktif_dt

      if selisih_waktu > timedelta(minutes=10):
        status = "🔴 Offline"

      # print(status)

      hasil = f'*---Status Perangkat---*\n\nStatus : *{status}*\nID Prangkat: `{data[0]["_id"]}`\nMerek : {data[0]["_deviceId"]["_Manufacturer"]}\nTipe: {data[0]["_deviceId"]["_ProductClass"]}'

      return hasil
    else:
       return "Perangkat tidak ada"



  #   hasil = f'*---Status Perangkat---*\nStatus : {status}\nMerek : {data[0]["_deviceId"]["_Manufacturer"]}\nSN : `{data[0]["_deviceId"]["_SerialNumber"]}`\nSinyal : {data[0]["VirtualParameters"]["Signal"]["_value"]}\nWaktu Aktif : {data[0]["VirtualParameters"]["upt"]["_value"]}'
  #  else:
  #     hasil = f'Perangkat Tidak Ditemukan'
  #   return hasil

  except Exception as e:
    print("errrrrr", e)
    return "Ada yang salah, Coba lagi"

def cek_client(sn):
  try:
    id = quote(sn)
    url = f'{API_URL}/devices/?query=%7B%22_id%22%3A%22{id}%22%7D'
    # print(url)
    res = requests.get(url)
    data = res.json()

    if not data or len(data) == 0:
      return "Perangkat tidak Ditemukan"
               
    
    if data[0]["_deviceId"]["_Manufacturer"] == "MikroTik":
      clients = data[0]["Device"]["Hosts"]["Host"]
      hasil = "---Perangkat yang terhubung---\n\n"

      for index, client in enumerate(clients.items(), 1):
        key, client_info = client
        if key.isdigit():
          device_name = client_info["HostName"]["_value"]
          ip_address = client_info["IPAddress"]["_value"]
        
          hasil += f"{index}. *{device_name}*\n   IP Address: `{ip_address}`\n"
    # SELAIN MIKOTIK
    else:
      clients = data[0]["InternetGatewayDevice"]["LANDevice"]["1"]["Hosts"]["Host"]

      hasil = "---Perangkat yang terhubung---\n\n"
      for index, client in enumerate(clients.items(), 1):
        key, client_info = client
        if key.isdigit():
          device_name = client_info["HostName"]["_value"]
          ip_address = client_info["IPAddress"]["_value"]
          mac = client_info["MACAddress"]["_value"]
        
          hasil += f"{index}. *{device_name}*\n      IP Address: {ip_address}\n      Mac Address: `{mac}`\n\n"

    return hasil

  except Exception as e:
    print("errrrrr", e)
    return "Ada yang salah, Coba lagi"
     
def reboot_perangkat(sn): 
   try: 
      payload = {"name": "reboot"} 
      res = postKeApi(sn, payload)
      return res 
   except:  
      return "Error ada yang salah" 

def acs(data):
    try:
        # print(data)
        key = data["key"]
        sn = quote(data["sn"])
        # print(key)
        if key == "US":
            payload = {
                "name": "setParameterValues",
                "parameterValues": [
                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.SSID", data["ssid"], "xsd:string"]
                ]
            }
            res = postKeApi(sn, payload)
            return res
        
        elif key == "UP":
            payload = {
                "name": "setParameterValues",
                "parameterValues": [
                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.PreSharedKey.1.PreSharedKey", data["password"], "xsd:string"]
                ]
            }
            res = postKeApi(sn, payload)
            return res
        
        else:
            payload = {
                "name": "setParameterValues",
                "parameterValues": [
                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.SSID", data["ssid"], "xsd:string"],
                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.PreSharedKey.1.PreSharedKey", data["password"], "xsd:string"]
                ]
            }
            res = postKeApi(sn, payload)
            return res
            
    except Exception as e:
        print(f"Error : {e}")
        return "Error"