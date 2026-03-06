import pytest
import json
from signature import SignatureVerifier
from models import WebhookPayload, ValidationRequest, C2CMessageEvent, GroupAtMessageEvent, Author


class TestSignatureVerifier:
    def test_expand_seed(self):
        verifier = SignatureVerifier("test_secret")
        seed = verifier._expand_seed(b"test")
        assert len(seed) == 32
        
    def test_expand_seed_long(self):
        verifier = SignatureVerifier("test_secret")
        seed = verifier._expand_seed(b"this_is_a_very_long_secret_key_that_exceeds_32_bytes")
        assert len(seed) == 32
    
    def test_generate_and_verify_signature(self):
        verifier = SignatureVerifier("DG5g3B4j9X2KOErG")
        
        event_ts = "1725442341"
        plain_token = "Arq0D5A61EgUu4OxUvOp"
        
        signature = verifier.generate_response_signature(event_ts, plain_token)
        
        assert len(signature) == 128
        assert isinstance(signature, str)


class TestModels:
    def test_webhook_payload_validation(self):
        data = {
            "id": "test_id",
            "op": 13,
            "d": {
                "plain_token": "test_token",
                "event_ts": "1234567890"
            }
        }
        payload = WebhookPayload(**data)
        assert payload.op == 13
        assert payload.d["plain_token"] == "test_token"
    
    def test_c2c_message_event(self):
        data = {
            "id": "msg_123",
            "author": {
                "user_openid": "ABC123"
            },
            "content": "/insight",
            "timestamp": "2023-11-06T13:37:18+08:00"
        }
        event = C2CMessageEvent(**data)
        assert event.content == "/insight"
        assert event.author.user_openid == "ABC123"
    
    def test_group_at_message_event(self):
        data = {
            "id": "msg_456",
            "author": {
                "member_openid": "MEMBER123"
            },
            "content": " /insight",
            "group_openid": "GROUP123",
            "timestamp": "2023-11-06T13:37:18+08:00"
        }
        event = GroupAtMessageEvent(**data)
        assert event.group_openid == "GROUP123"
        assert event.content.strip() == "/insight"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
