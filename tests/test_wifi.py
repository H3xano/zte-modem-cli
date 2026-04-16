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
