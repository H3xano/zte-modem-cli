import json
import re
from datetime import datetime
from urllib.parse import quote

from src.http_client import get, post
from src.hex_util import hex_decode, hex_encode


def list_sms(modem_ip):
    """Return list of dicts with keys: id, number, date, content (decoded)."""
    params = (
        "?isTest=false&cmd=sms_data_total&page=0&data_per_page=500"
        "&mem_store=1&tags=10&order_by=order+by+id+desc"
    )
    raw = get(modem_ip, params)
    # ZTE modems embed null bytes and other C0 control characters in JSON responses,
    # which break json.loads. Strip them before parsing. SMS content is hex-encoded
    # in the response, so stripping these bytes does not corrupt message text.
    raw = re.sub(r"[\x00-\x1f]", "", raw)
    data = json.loads(raw)
    messages = []
    for group in data.get("messages", []):
        for msg in group:
            messages.append(
                {
                    "id": msg["id"],
                    "number": msg["number"],
                    "date": msg["date"],
                    "content": hex_decode(msg["content"]),
                }
            )
    return messages


def send_sms(modem_ip, phone, message):
    """Send an SMS. Returns True on success."""
    # Build timestamp from system local timezone
    now = datetime.now().astimezone()
    offset_seconds = int(now.utcoffset().total_seconds())
    offset_hours = offset_seconds // 3600
    # Note: sub-hour offsets (e.g. UTC+5:30) are truncated — matches PHP behavior.
    # The modem uses this only for display; practical impact is cosmetic.
    tz_str = f"+{offset_hours}" if offset_hours >= 0 else str(offset_hours)
    sms_time = now.strftime(f"%y;%m;%d;%H;%M;%S;{tz_str}")

    data = (
        f"isTest=false&goformId=SEND_SMS&notCallback=true"
        f"&Number={quote(phone)}"
        f"&sms_time={quote(sms_time)}"
        f"&MessageBody={hex_encode(message)}"
        f"&ID=-1&encode_type=UNICODE"
    )
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"


def delete_sms(modem_ip, id_or_star):
    """Delete message(s). Pass an ID string or '*' for all. Returns list of result dicts."""
    if id_or_star == "*":
        messages = list_sms(modem_ip)
        if not messages:
            return []
        return [_delete_one(modem_ip, msg["id"]) for msg in messages]
    return [_delete_one(modem_ip, id_or_star)]


def _delete_one(modem_ip, msg_id):
    data = f"isTest=false&goformId=DELETE_SMS&msg_id={msg_id}&notCallback=true"
    result = post(modem_ip, data)
    success = json.loads(result).get("result") == "success"
    return {"id": msg_id, "success": success}
