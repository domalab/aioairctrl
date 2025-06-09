"""Tests for the encryption module."""
import pytest
from aioairctrl.coap.encryption import EncryptionContext, DigestMismatchException


class TestEncryptionContext:
    """Test cases for EncryptionContext."""

    def test_init(self):
        """Test initialization of EncryptionContext."""
        ctx = EncryptionContext()
        assert ctx._client_key is None

    def test_set_client_key(self):
        """Test setting client key."""
        ctx = EncryptionContext()
        test_key = "12345678"
        ctx.set_client_key(test_key)
        assert ctx._client_key == test_key

    def test_increment_client_key(self):
        """Test client key incrementation."""
        ctx = EncryptionContext()
        ctx.set_client_key("00000001")
        ctx._increment_client_key()
        assert ctx._client_key == "00000002"

    def test_increment_client_key_overflow(self):
        """Test client key incrementation with overflow."""
        ctx = EncryptionContext()
        ctx.set_client_key("FFFFFFFF")
        ctx._increment_client_key()
        assert ctx._client_key == "00000000"

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption roundtrip."""
        ctx = EncryptionContext()
        ctx.set_client_key("12345678")
        
        original_payload = '{"test": "data", "number": 42}'
        encrypted = ctx.encrypt(original_payload)
        
        # Encrypted payload should be different from original
        assert encrypted != original_payload
        assert len(encrypted) > len(original_payload)
        
        # Decrypt should return original payload
        decrypted = ctx.decrypt(encrypted)
        assert decrypted == original_payload

    def test_encrypt_increments_key(self):
        """Test that encryption increments the client key."""
        ctx = EncryptionContext()
        ctx.set_client_key("00000001")
        
        original_key = ctx._client_key
        ctx.encrypt("test data")
        
        assert ctx._client_key != original_key
        assert ctx._client_key == "00000002"

    def test_decrypt_invalid_digest(self):
        """Test decryption with invalid digest raises exception."""
        ctx = EncryptionContext()
        ctx.set_client_key("12345678")
        
        # Create a valid encrypted payload
        encrypted = ctx.encrypt("test data")
        
        # Corrupt the digest (last 64 characters)
        corrupted = encrypted[:-64] + "0" * 64
        
        with pytest.raises(DigestMismatchException):
            ctx.decrypt(corrupted)

    def test_decrypt_malformed_payload(self):
        """Test decryption with malformed payload."""
        ctx = EncryptionContext()
        
        # Too short payload
        with pytest.raises(Exception):
            ctx.decrypt("short")
        
        # Invalid hex characters
        with pytest.raises(Exception):
            ctx.decrypt("ZZZZZZZZ" + "A" * 64 + "B" * 64)

    def test_multiple_encryptions_different_results(self):
        """Test that multiple encryptions of same data produce different results."""
        ctx = EncryptionContext()
        ctx.set_client_key("12345678")
        
        payload = "same data"
        encrypted1 = ctx.encrypt(payload)
        encrypted2 = ctx.encrypt(payload)
        
        # Results should be different due to key incrementation
        assert encrypted1 != encrypted2
        
        # But both should decrypt to the same original payload
        assert ctx.decrypt(encrypted1) == payload
        assert ctx.decrypt(encrypted2) == payload

    def test_secret_key_constant(self):
        """Test that SECRET_KEY is the expected constant."""
        assert EncryptionContext.SECRET_KEY == "JiangPan"

    def test_encryption_format(self):
        """Test the format of encrypted payload."""
        ctx = EncryptionContext()
        ctx.set_client_key("ABCDEF12")
        
        encrypted = ctx.encrypt("test")
        
        # Should start with the incremented key (ABCDEF13)
        assert encrypted.startswith("ABCDEF13")
        
        # Should be hex string
        assert all(c in "0123456789ABCDEF" for c in encrypted)
        
        # Should have correct length: 8 (key) + variable (ciphertext) + 64 (digest)
        assert len(encrypted) >= 8 + 64
        assert (len(encrypted) - 8 - 64) % 2 == 0  # Ciphertext should be even length (hex)
