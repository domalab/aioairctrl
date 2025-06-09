"""Tests for the CoAP client module."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from philips_airctrl.coap.client import Client


class TestClient:
    """Test cases for CoAP Client."""

    def test_init(self):
        """Test client initialization."""
        client = Client("192.168.1.100", 5683)
        assert client.host == "192.168.1.100"
        assert client.port == 5683
        assert client._client_context is None
        assert client._encryption_context is None

    def test_init_default_port(self):
        """Test client initialization with default port."""
        client = Client("192.168.1.100")
        assert client.host == "192.168.1.100"
        assert client.port == 5683

    @pytest.mark.asyncio
    async def test_create_factory_method(self):
        """Test the create factory method."""
        with patch.object(Client, '_init', new_callable=AsyncMock) as mock_init:
            client = await Client.create("192.168.1.100", 5684)
            assert isinstance(client, Client)
            assert client.host == "192.168.1.100"
            assert client.port == 5684
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown(self):
        """Test client shutdown."""
        client = Client("192.168.1.100")
        mock_context = AsyncMock()
        client._client_context = mock_context
        
        await client.shutdown()
        mock_context.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_no_context(self):
        """Test client shutdown when no context exists."""
        client = Client("192.168.1.100")
        # Should not raise an exception
        await client.shutdown()

    @pytest.mark.asyncio
    async def test_sync(self):
        """Test the sync operation."""
        client = Client("192.168.1.100")
        
        # Mock the client context and response
        mock_context = MagicMock()
        mock_response = MagicMock()
        mock_response.payload.decode.return_value = "ABCD1234"

        # Create a proper mock requester with async response attribute
        mock_requester = MagicMock()
        # The response attribute should be awaitable and return the mock_response
        async def mock_response_coro():
            return mock_response
        mock_requester.response = mock_response_coro()
        mock_context.request.return_value = mock_requester
        
        # Mock the encryption context
        mock_encryption = MagicMock()
        
        client._client_context = mock_context
        client._encryption_context = mock_encryption
        
        with patch('os.urandom') as mock_urandom:
            mock_urandom.return_value = b'\x12\x34\x56\x78'
            
            await client._sync()
            
            # Verify the request was made correctly
            mock_context.request.assert_called_once()
            call_args = mock_context.request.call_args[0][0]
            # Check that the request was made with correct payload
            assert call_args.payload == b'12345678'
            
            # Verify encryption context was updated
            mock_encryption.set_client_key.assert_called_once_with("ABCD1234")

    @pytest.mark.asyncio
    async def test_get_status(self):
        """Test getting device status."""
        client = Client("192.168.1.100")
        
        # Mock the client context and response
        mock_context = MagicMock()
        mock_response = MagicMock()
        mock_response.payload.decode.return_value = "encrypted_payload"
        mock_response.opt.max_age = 120

        # Create a proper mock requester with async response attribute
        mock_requester = MagicMock()
        # The response attribute should be awaitable and return the mock_response
        async def mock_response_coro():
            return mock_response
        mock_requester.response = mock_response_coro()
        mock_context.request.return_value = mock_requester
        
        # Mock the encryption context
        mock_encryption = MagicMock()
        decrypted_payload = '{"state": {"reported": {"power": true, "mode": "auto"}}}'
        mock_encryption.decrypt.return_value = decrypted_payload
        
        client._client_context = mock_context
        client._encryption_context = mock_encryption
        
        status, max_age = await client.get_status()
        
        # Verify the request was made correctly
        mock_context.request.assert_called_once()
        call_args = mock_context.request.call_args[0][0]
        # Check that observe was set
        assert call_args.opt.observe == 0
        
        # Verify decryption was called
        mock_encryption.decrypt.assert_called_once_with("encrypted_payload")
        
        # Verify returned values
        assert status == {"power": True, "mode": "auto"}
        assert max_age == 120

    @pytest.mark.asyncio
    async def test_get_status_no_max_age(self):
        """Test getting device status when max_age is not available."""
        client = Client("192.168.1.100")
        
        # Mock the client context and response
        mock_context = MagicMock()
        mock_response = MagicMock()
        mock_response.payload.decode.return_value = "encrypted_payload"
        # Simulate AttributeError when accessing max_age
        mock_opt = MagicMock()
        del mock_opt.max_age  # Remove the attribute to trigger AttributeError
        mock_response.opt = mock_opt

        # Create a proper mock requester with async response attribute
        mock_requester = MagicMock()
        # The response attribute should be awaitable and return the mock_response
        async def mock_response_coro():
            return mock_response
        mock_requester.response = mock_response_coro()
        mock_context.request.return_value = mock_requester
        
        # Mock the encryption context
        mock_encryption = MagicMock()
        decrypted_payload = '{"state": {"reported": {"power": true}}}'
        mock_encryption.decrypt.return_value = decrypted_payload
        
        client._client_context = mock_context
        client._encryption_context = mock_encryption
        
        status, max_age = await client.get_status()
        
        # Should default to 60 when max_age is not available
        assert status == {"power": True}
        assert max_age == 60

    @pytest.mark.asyncio
    async def test_set_control_value(self):
        """Test setting a single control value."""
        client = Client("192.168.1.100")
        
        with patch.object(client, 'set_control_values', new_callable=AsyncMock) as mock_set_values:
            mock_set_values.return_value = True
            
            result = await client.set_control_value("power", True)
            
            mock_set_values.assert_called_once_with(
                data={"power": True}, 
                retry_count=5, 
                resync=True
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_set_control_values_success(self):
        """Test setting multiple control values successfully."""
        client = Client("192.168.1.100")
        
        # Mock the client context and response
        mock_context = MagicMock()
        mock_response = MagicMock()
        mock_response.payload = b'{"status": "success"}'

        # Create a proper mock requester with async response attribute
        mock_requester = MagicMock()
        # The response attribute should be awaitable and return the mock_response
        async def mock_response_coro():
            return mock_response
        mock_requester.response = mock_response_coro()
        mock_context.request.return_value = mock_requester
        
        # Mock the encryption context
        mock_encryption = MagicMock()
        mock_encryption.encrypt.return_value = "encrypted_payload"
        
        client._client_context = mock_context
        client._encryption_context = mock_encryption
        
        data = {"power": True, "mode": "auto"}
        result = await client.set_control_values(data)
        
        # Verify the request was made correctly
        mock_context.request.assert_called_once()
        call_args = mock_context.request.call_args[0][0]
        # Check that the payload was encrypted
        assert call_args.payload == b"encrypted_payload"
        
        # Verify encryption was called with correct payload
        mock_encryption.encrypt.assert_called_once()
        encrypted_call_args = mock_encryption.encrypt.call_args[0][0]
        payload_data = json.loads(encrypted_call_args)
        expected_data = {
            "state": {
                "desired": {
                    "CommandType": "app",
                    "DeviceId": "",
                    "EnduserId": "",
                    "power": True,
                    "mode": "auto"
                }
            }
        }
        assert payload_data == expected_data
        
        assert result is True
