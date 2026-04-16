import base64
import json
from src.http_client import post


def login(modem_ip, password):
    """Login to modem. Returns True on success."""
    encoded = base64.b64encode(password.encode()).decode()
    data = f"isTest=false&goformId=LOGIN&password={encoded}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "3"


def logout(modem_ip):
    """Logout from modem. Returns True on success."""
    data = "isTest=false&goformId=LOGOUT"
    result = post(modem_ip, data)
    # Note: modem firmware has a typo — "sucess" not "success"
    return json.loads(result).get("result") == "sucess"
