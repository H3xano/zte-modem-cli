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
