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
