# ZTE API and Hack — Python Rewrite Design

**Date:** 2026-04-16  
**Status:** Approved

## Overview

Rewrite the existing PHP CLI tool for controlling ZTE modems into Python. The goal is a clean, improved port — same functionality, better output, better config handling.

## File Structure

```
ZTE_API_and_Hack/
├── zte.py              # CLI entry point (replaces index.php)
├── .env                # modem_ip + password (gitignored)
├── .env.example        # template committed to git
├── requirements.txt    # colorama, python-dotenv, requests
└── src/
    ├── __init__.py
    ├── http_client.py  # replaces Curl.php (uses requests library)
    ├── hex_util.py     # replaces Hex.php
    ├── login.py        # replaces Login.php
    ├── sms.py          # replaces Sms.php
    ├── wifi.py         # replaces Wifi.php
    ├── wan.py          # replaces Wan.php
    └── hack.py         # replaces Hack.php
```

`Json.php` is not ported — Python's built-in `json` module is used directly everywhere.

## Dependencies

- `requests` — HTTP client (replaces PHP curl extension)
- `python-dotenv` — loads `.env` file
- `colorama` — cross-platform colored terminal output (required for Windows)

## Credentials & Config

`.env` file (user edits once, never committed to git):
```ini
MODEM_IP=192.168.0.1
PASSWORD=admin
```

`.env.example` is committed as a template.

Priority for credential resolution: **CLI args > `.env` > error and exit.**

## CLI Interface

```
python zte.py [--ip IP] [--password PASS] <command> [args]

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
```

Running with no arguments or an unknown command prints the help table and exits.

`--ip` and `--password` must come before the command when provided.

## Output & Error Handling

All output uses `colorama` colors — no raw `var_dump` or JSON blobs:

| Color  | Meaning    | Examples |
|--------|------------|---------|
| Green  | Success    | `✓ WiFi enabled.`, `✓ SMS sent to +1234567890.`, `✓ Message #5 deleted.` |
| Red    | Error      | `✗ Login failed.`, `✗ Could not connect to modem.` |
| Cyan   | Info/data  | SMS list entries: `[#5] +1234 | 25/03/2026 14:30 | Hello world` |
| Yellow | Warning    | `⚠ No messages found.`, `⚠ No messages to delete.` |

**SMS list (`ls`):** One message per line with ID, phone number, date, and decoded content.

**Hack commands:** Each step (factory backdoor, nvram exploit, TFTP fetch) prints its own status line as it executes.

**Errors:** Connection failures and unexpected API responses are caught and printed in red. No Python tracebacks shown to the user.

## Module Responsibilities

### `src/http_client.py`
Wraps `requests` for GET and POST to the modem. Sets the required `Referer` and `Host` headers. Returns the raw response text or raises a connection error.

### `src/hex_util.py`
- `hex_encode(text)` — encodes UTF-8 text to 4-char hex codepoints (for sending SMS body)
- `hex_decode(hex_str)` — decodes 4-char hex codepoints back to UTF-8 text (for reading SMS body)

### `src/login.py`
`login(modem_ip, password)` and `logout(modem_ip)` — POST to `goform_set_cmd_process` with `LOGIN`/`LOGOUT` goformId. Password is base64-encoded before sending.

### `src/sms.py`
- `list_sms(modem_ip)` — GET SMS list, strip control characters, decode hex content, return list of dicts
- `send_sms(modem_ip, phone, message)` — hex-encode message, POST to send; SMS timestamp derived from system local timezone
- `delete_sms(modem_ip, id_or_star)` — delete by ID or fetch all IDs and delete each

### `src/wifi.py`
`set_wifi(modem_ip, enable: bool)` — POST `SET_WIFI_INFO` with `wifiEnabled=1` or `0`.

### `src/wan.py`
`set_wan(modem_ip, connect: bool)` — POST `CONNECT_NETWORK` or `DISCONNECT_NETWORK` goformId.

### `src/hack.py`
- `factory_backdoor(modem_ip, password)` — POST `CHANGE_MODE` change_mode=2
- `exploits_nvram(modem_ip)` — POST `URL_FILTER_ADD` with telnetd injection payload
- `tftp_telnetd(modem_ip, tftp_ip)` — POST `URL_FILTER_ADD` with zte_debug.sh payload
- `tftp_telnetd_direct(modem_ip, tftp_ip)` — POST `URL_FILTER_ADD` with raw busybox tftp payload

### `zte.py`
- Loads `.env` with `python-dotenv`
- Parses `--ip` / `--password` CLI overrides
- Dispatches to the appropriate module function based on command
- Handles all colored output (modules return data/status, `zte.py` prints it)

## Behavior Preserved from PHP Version

- Stateless login-per-command (no session caching)
- Default TFTP IP: `192.168.0.22`
- SMS timestamp uses the system's local timezone (via Python's `datetime` with `astimezone()`)
- Password base64-encoded before sending to modem
- SMS message body hex-encoded as UCS-2LE codepoints
