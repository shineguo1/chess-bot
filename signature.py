import nacl.signing
import nacl.encoding
import logging

logger = logging.getLogger(__name__)


class SignatureVerifier:
    def __init__(self, bot_secret: str):
        self.bot_secret = bot_secret
    
    def _expand_seed(self, input_bytes: bytes) -> bytes:
        seed = b''
        while len(seed) < 32:
            seed += input_bytes
        return seed[:32]
    
    def verify_signature(
        self, 
        signature: str, 
        timestamp: str, 
        body: str
    ) -> bool:
        try:
            seed = self._expand_seed(self.bot_secret.encode('utf-8'))
            private_key = nacl.signing.SigningKey(seed)
            public_key = private_key.verify_key
            
            signature_bytes = bytes.fromhex(signature)
            
            message = timestamp.encode('utf-8') + body.encode('utf-8')
            
            verify_key = nacl.signing.VerifyKey(bytes(public_key))
            verify_key.verify(message, signature_bytes)
            
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def generate_response_signature(
        self, 
        event_ts: str, 
        plain_token: str
    ) -> str:
        try:
            seed = self._expand_seed(self.bot_secret.encode('utf-8'))
            private_key = nacl.signing.SigningKey(seed)
            
            message = event_ts.encode('utf-8') + plain_token.encode('utf-8')
            signed = private_key.sign(message)
            
            return signed.signature.hex()
        except Exception as e:
            logger.error(f"Failed to generate response signature: {e}")
            raise
