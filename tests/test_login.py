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
