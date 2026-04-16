import json
from src.http_client import post


def set_wan(modem_ip, connect):
    """Connect or disconnect WAN. Returns True on success."""
    goform_id = "CONNECT_NETWORK" if connect else "DISCONNECT_NETWORK"
    data = f"isTest=false&notCallback=true&goformId={goform_id}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"
