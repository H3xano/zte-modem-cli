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
