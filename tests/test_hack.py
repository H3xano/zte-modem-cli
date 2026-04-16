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
