import requests
from config import API_URL, SSIDKE
from urllib.parse import quote
from datetime import datetime, timedelta
from pytz import timezone

def postKeApi(device_id, payload):
    url = f'{API_URL}/devices/{device_id}/tasks?connection_request'
    r = requests.post(url, json=payload)
    return r.status_code
  
def refresh_parameter(sn, nama_parameter=None):
  try:
    id = quote(sn)
    payload = {"name": "refreshObject", "objectName": nama_parameter }
    #payload = {"name": "refreshObject", "objectName": ["Device", "Device.DeviceInfo"] }
    postKeApi(id, payload)
  except:
    print("error pada function refresh")

def cek_perangkat(sn):
    try:
        id = quote(sn)
        refresh_parameter(sn, "Device")
        #refresh_parameter(sn, "_lastInform")
        res = requests.get(f'{API_URL}/devices/?query=%7B%22_id%22%3A%22{id}%22%7D')
        data = res.json()
        if data:
            status = "🟢 Online"
            terakhirAktif = data[0]["_lastInform"] 
            terakhirAktif_dt = datetime.fromisoformat(terakhirAktif[:-1]) 
            sekarang = datetime.utcnow()
            selisih_waktu = sekarang - terakhirAktif_dt
            if selisih_waktu > timedelta(minutes=5):
                status = "🔴 Offline"

            wib = timezone('Asia/Jakarta')
            terakhirAktif_wib = terakhirAktif_dt.astimezone(wib)
            terakhirAktif_wib_str = terakhirAktif_wib.strftime("%H:%M:%S %d-%m-%Y")                            
            totalClient = cek_client(sn, True, data)

            hasil = (
                f'*---Status Perangkat---*\n\n'
                f'Status : *{status}*\n'
                f'ID Perangkat: `{data[0]["_id"]}`\n'
                f'Merek : {data[0]["_deviceId"]["_Manufacturer"]}\n'
                f'Tipe: {data[0]["_deviceId"]["_ProductClass"]}\n'
                f"Total Client: {totalClient} Perangkat\n"
                f'Info Terakhir : {terakhirAktif_wib_str}\n'
            )
            return hasil
        else:
            return "❌ *Perangkat tidak Ditemukan*\n_Pastikan Serial Number benar!_"
    except Exception as e:
        print("errrrrr", e)
        return "Ada yang salah, Coba lagi"
    
def cek_client(sn, callback=False, data=None):
  try:
    if not data:
        refresh_parameter(sn, "Device")
        refresh_parameter(sn, "InternetGatewayDevice.LANDevice")
        id = quote(sn)
        url = f'{API_URL}/devices/?query=%7B%22_id%22%3A%22{id}%22%7D'
        res = requests.get(url)
        data = res.json()   
    if len(data) == 0:
      if callback:
        return 0
      return "❌ *Perangkat tidak Ditemukan*\n_Pastikan Serial Number benar!_"
  
    if data[0]["_deviceId"]["_Manufacturer"] == "MikroTik":
      clients = data[0]["Device"]["Hosts"]["Host"]
      total = len(clients)
      if callback: 
        return total - 3
      hasil = "*---Perangkat yang terhubung---*\n\n*Total*: " + str(total - 3) + " perangkat\n\n"
      for index, client in enumerate(clients.items(), 1):
        key, client_info = client
        if key.isdigit():
          device_name = client_info["HostName"]["_value"]
          ip_address = client_info["IPAddress"]["_value"]
          hasil += f"{index}. *{device_name}*\n   IP Address: `{ip_address}`\n"
    # SELAIN MIKOTIK
    else:
      clients = data[0]["InternetGatewayDevice"]["LANDevice"]["1"]["Hosts"]["Host"]
      total = len(clients)
      if callback:
        return total - 3
      hasil = "*---Perangkat yang terhubung---*\n\n*Total*: " + str(total - 3) + " perangkat\n\n"
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
      return "Error ada yang salah, Coba lagi" 

def acs(data):
    try:
        key = data["key"]
        sn = quote(data["sn"])
        if key == "US":
            payload = {
                "name": "setParameterValues",
                "parameterValues": [
                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.SSID", data["ssid"], "xsd:string"],
                    [f"Device.WiFi.SSID.1.SSID", data["ssid"], "xsd:string"],
                ]
            }
            res = postKeApi(sn, payload)
            return res
        elif key == "UP":
            payload = {
                "name": "setParameterValues",
                "parameterValues": [
                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.PreSharedKey.1.PreSharedKey", data["password"], "xsd:string"],
                    [f"Device.WiFi.AccessPoint.1.Security.KeyPassphrase", data["password"], "xsd:string"]
                ]
            }
            res = postKeApi(sn, payload)
            return res
        else:
            payload = {
                "name": "setParameterValues",
                "parameterValues": [
                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.SSID", data["ssid"], "xsd:string"],
                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.PreSharedKey.1.PreSharedKey", data["password"], "xsd:string"],
                    [f"Device.WiFi.SSID.1.SSID", data["ssid"], "xsd:string"],
                    [f"Device.WiFi.AccessPoint.1.Security.KeyPassphrase", data["password"], "xsd:string"]
                ]
            }
            res = postKeApi(sn, payload)
            return res
    except Exception as e:
        print("error pada function acs", e)
        return 500