"""Tests for the CLI module."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aioairctrl.cli import parse_args, async_main


class TestCLI:
    """Test cases for CLI functionality."""

    def test_parse_args_status(self):
        """Test parsing status command arguments."""
        args = parse_args(["-H", "192.168.1.100", "status"])
        assert args.host == "192.168.1.100"
        assert args.port == 5683
        assert args.command == "status"
        assert args.debug is False
        assert args.json is False

    def test_parse_args_status_with_options(self):
        """Test parsing status command with options."""
        args = parse_args(["-H", "192.168.1.100", "-P", "1234", "-D", "status", "-J"])
        assert args.host == "192.168.1.100"
        assert args.port == 1234
        assert args.command == "status"
        assert args.debug is True
        assert args.json is True

    def test_parse_args_status_observe(self):
        """Test parsing status-observe command."""
        args = parse_args(["-H", "192.168.1.100", "status-observe", "--json"])
        assert args.host == "192.168.1.100"
        assert args.command == "status-observe"
        assert args.json is True

    def test_parse_args_set_single_value(self):
        """Test parsing set command with single value."""
        args = parse_args(["-H", "192.168.1.100", "set", "power=true"])
        assert args.host == "192.168.1.100"
        assert args.command == "set"
        assert args.values == ["power=true"]
        assert args.value_as_int is False

    def test_parse_args_set_multiple_values(self):
        """Test parsing set command with multiple values."""
        args = parse_args(["-H", "192.168.1.100", "set", "power=true", "mode=auto", "speed=3"])
        assert args.host == "192.168.1.100"
        assert args.command == "set"
        assert args.values == ["power=true", "mode=auto", "speed=3"]

    def test_parse_args_set_with_int_flag(self):
        """Test parsing set command with integer flag."""
        args = parse_args(["-H", "192.168.1.100", "set", "--int", "speed=3"])
        assert args.host == "192.168.1.100"
        assert args.command == "set"
        assert args.values == ["speed=3"]
        assert args.value_as_int is True

    def test_parse_args_missing_host(self):
        """Test that missing host raises SystemExit."""
        with pytest.raises(SystemExit):
            parse_args(["status"])

    def test_parse_args_missing_command(self):
        """Test that missing command raises SystemExit."""
        with pytest.raises(SystemExit):
            parse_args(["-H", "192.168.1.100"])

    @pytest.mark.asyncio
    async def test_async_main_status(self):
        """Test async_main with status command."""
        mock_client = AsyncMock()
        mock_client.get_status.return_value = ({"power": True}, 60)
        
        with patch('aioairctrl.cli.parse_args') as mock_parse_args, \
             patch('aioairctrl.cli.CoAPClient.create', return_value=mock_client) as mock_create, \
             patch('builtins.print') as mock_print:
            
            mock_args = MagicMock()
            mock_args.host = "192.168.1.100"
            mock_args.port = 5683
            mock_args.debug = False
            mock_args.command = "status"
            mock_args.json = False
            mock_parse_args.return_value = mock_args
            
            await async_main()
            
            mock_create.assert_called_once_with(host="192.168.1.100", port=5683)
            mock_client.get_status.assert_called_once()
            mock_client.shutdown.assert_called_once()
            
            # Check that print was called with status and max_age
            assert mock_print.call_count == 2
            mock_print.assert_any_call({"power": True})
            mock_print.assert_any_call("max_age = 60")

    @pytest.mark.asyncio
    async def test_async_main_status_json(self):
        """Test async_main with status command and JSON output."""
        mock_client = AsyncMock()
        mock_client.get_status.return_value = ({"power": True}, 60)
        
        with patch('aioairctrl.cli.parse_args') as mock_parse_args, \
             patch('aioairctrl.cli.CoAPClient.create', return_value=mock_client) as mock_create, \
             patch('builtins.print') as mock_print:
            
            mock_args = MagicMock()
            mock_args.host = "192.168.1.100"
            mock_args.port = 5683
            mock_args.debug = False
            mock_args.command = "status"
            mock_args.json = True
            mock_parse_args.return_value = mock_args
            
            await async_main()
            
            mock_create.assert_called_once_with(host="192.168.1.100", port=5683)
            mock_client.get_status.assert_called_once()
            mock_client.shutdown.assert_called_once()
            
            # Check that print was called with JSON output
            mock_print.assert_called_once_with('{"power": true}')

    @pytest.mark.asyncio
    async def test_async_main_set_values(self):
        """Test async_main with set command."""
        mock_client = AsyncMock()
        mock_client.set_control_values.return_value = True
        
        with patch('aioairctrl.cli.parse_args') as mock_parse_args, \
             patch('aioairctrl.cli.CoAPClient.create', return_value=mock_client) as mock_create:
            
            mock_args = MagicMock()
            mock_args.host = "192.168.1.100"
            mock_args.port = 5683
            mock_args.debug = False
            mock_args.command = "set"
            mock_args.values = ["power=true", "mode=auto", "speed=3"]
            mock_args.value_as_int = False
            mock_parse_args.return_value = mock_args
            
            await async_main()
            
            mock_create.assert_called_once_with(host="192.168.1.100", port=5683)
            mock_client.set_control_values.assert_called_once_with(
                data={"power": True, "mode": "auto", "speed": "3"}
            )
            mock_client.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_main_set_values_as_int(self):
        """Test async_main with set command and integer conversion."""
        mock_client = AsyncMock()
        mock_client.set_control_values.return_value = True
        
        with patch('aioairctrl.cli.parse_args') as mock_parse_args, \
             patch('aioairctrl.cli.CoAPClient.create', return_value=mock_client) as mock_create:
            
            mock_args = MagicMock()
            mock_args.host = "192.168.1.100"
            mock_args.port = 5683
            mock_args.debug = False
            mock_args.command = "set"
            mock_args.values = ["speed=3", "level=5"]
            mock_args.value_as_int = True
            mock_parse_args.return_value = mock_args
            
            await async_main()
            
            mock_create.assert_called_once_with(host="192.168.1.100", port=5683)
            mock_client.set_control_values.assert_called_once_with(
                data={"speed": 3, "level": 5}
            )
            mock_client.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_main_set_boolean_values(self):
        """Test async_main with set command and boolean conversion."""
        mock_client = AsyncMock()
        mock_client.set_control_values.return_value = True
        
        with patch('aioairctrl.cli.parse_args') as mock_parse_args, \
             patch('aioairctrl.cli.CoAPClient.create', return_value=mock_client) as mock_create:
            
            mock_args = MagicMock()
            mock_args.host = "192.168.1.100"
            mock_args.port = 5683
            mock_args.debug = False
            mock_args.command = "set"
            mock_args.values = ["power=true", "auto=false"]
            mock_args.value_as_int = False
            mock_parse_args.return_value = mock_args
            
            await async_main()
            
            mock_create.assert_called_once_with(host="192.168.1.100", port=5683)
            mock_client.set_control_values.assert_called_once_with(
                data={"power": True, "auto": False}
            )
            mock_client.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_main_keyboard_interrupt(self):
        """Test async_main handles KeyboardInterrupt gracefully."""
        mock_client = AsyncMock()
        mock_client.get_status.side_effect = KeyboardInterrupt()
        
        with patch('aioairctrl.cli.parse_args') as mock_parse_args, \
             patch('aioairctrl.cli.CoAPClient.create', return_value=mock_client) as mock_create:
            
            mock_args = MagicMock()
            mock_args.host = "192.168.1.100"
            mock_args.port = 5683
            mock_args.debug = False
            mock_args.command = "status"
            mock_args.json = False
            mock_parse_args.return_value = mock_args
            
            # Should not raise an exception
            await async_main()
            
            mock_create.assert_called_once_with(host="192.168.1.100", port=5683)
            mock_client.shutdown.assert_called_once()
