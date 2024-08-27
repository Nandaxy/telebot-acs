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
      print("code:",res.status_code)
      
      

   
      status = "🟢 Online"

      
      hasil = f'*---Status Perangkat---*\nStatus : {status}\nMerek : {data[0]["_deviceId"]["_Manufacturer"]}\nSN : `{data[0]["_deviceId"]["_SerialNumber"]}`\nSinyal : {data[0]["VirtualParameters"]["Signal"]["_value"]}\nWaktu Aktif : {data[0]["VirtualParameters"]["upt"]["_value"]}'
    else:
      print("Not Found")
      hasil = f'Perangkat Tidak Ditemukan'
  
    
    return hasil
  except Exception as e:
    print("errrrrr", e)
    return "Ada yang salah, Coba lagi"

def cek_sn():
    print("oke")

def acs(data):
    try:
        print(data)
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
        return "error"