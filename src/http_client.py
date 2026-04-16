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
