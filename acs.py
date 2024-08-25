# Parameter SSID Mikrotik = Device.WiFi.SSID.1.SSID
# Parameter Password Mikrotik = Device.WiFi.AccessPoint.1.Security.KeyPassphrase
# Onu SSID = InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.SSID
# onu Pw =  InternetGatewayDevice.LANDevice.1.WLANConfiguration.{SSIDKE}.PreSharedKey.1.PreSharedKey
import requests
from config import API_URL, SSIDKE
from logger import logger
from urllib.parse import quote

def postKeApi(device_id, payload):
    url = f'{API_URL}/devices/{device_id}/tasks?connection_request'
    r = requests.post(url, json=payload)
    return r.status_code


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
                    [f"Device.WiFi.SSID.{SSIDKE}.SSID", data["ssid"], "xsd:string"]
                ]
            }
            res = postKeApi(sn, payload)
            return res
        
        elif key == "UP":
            payload = {
                "name": "setParameterValues",
                "parameterValues": [
                    [f"Device.WiFi.AccessPoint.{SSIDKE}.Security.KeyPassphrase", data["password"], "xsd:string"]
                ]
            }
            res = postKeApi(sn, payload)
            return res
        
        else:
            payload = {
                "name": "setParameterValues",
                "parameterValues": [
                    [f"Device.WiFi.SSID.{SSIDKE}.SSID", data["ssid"], "xsd:string"],
                    [f"Device.WiFi.AccessPoint.{SSIDKE}.Security.KeyPassphrase", data["password"], "xsd:string"]
                ]
            }
            res = postKeApi(sn, payload)
            return res
            
    except Exception as e:
        print(f"Error : {e}")
        return "error"