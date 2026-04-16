import json
from src.http_client import post


def set_wifi(modem_ip, enable):
    """Enable or disable WiFi. Returns True on success."""
    value = 1 if enable else 0
    data = f"goformId=SET_WIFI_INFO&isTest=false&m_ssid_enable=0&wifiEnabled={value}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"
