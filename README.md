# aioairctrl-ha

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration%20Ready-blue.svg)](https://www.home-assistant.io/)

An enhanced async Python library and command-line utilities for controlling Philips air purifiers using encrypted CoAP (Constrained Application Protocol). This fork adds comprehensive **Home Assistant integration support**, **automatic device discovery**, and **user-friendly setup tools**.

## ⚠️ **Important: Enhanced Fork Notice**

> **This is NOT the original aioairctrl package!** This is an enhanced fork specifically designed for Home Assistant integration.
>
> - **❌ DO NOT install from PyPI** (`pip install aioairctrl`) - you'll get the original version without Home Assistant features
> - **✅ MUST install from source** (see installation instructions below) to get device discovery, setup wizard, and HA integration
> - **🏠 Designed for Home Assistant users** who need comprehensive device information and easy integration setup

## Features

- **🔍 Automatic Device Discovery** - Find Philips air purifiers on your network automatically
- **🏠 Home Assistant Integration** - Ready-to-use configurations for Home Assistant
- **📊 Comprehensive Device Analysis** - Extract 70+ data points with capability detection
- **🧙‍♂️ Interactive Setup Wizard** - User-friendly guided setup for non-technical users
- **📁 Multiple Export Formats** - JSON and YAML output for easy integration
- **⚡ Async/await support** - Built with modern Python async patterns
- **🔐 Encrypted communication** - Secure CoAP communication with AES encryption
- **🖥️ Command-line interface** - Easy-to-use CLI for quick operations
- **📚 Library API** - Integrate air purifier control into your applications
- **📡 Device status monitoring** - Real-time status updates and observation
- **🧪 Comprehensive testing** - Well-tested with 75+ test coverage

## Supported Devices

This library has been tested with:
- Philips AC4220/12 Air Purifier
- Other Philips air purifiers using CoAP protocol

## Installation

> **⚠️ Important**: This enhanced version with Home Assistant integration features is **only available from source**. The original `aioairctrl` package on PyPI does not include device discovery, setup wizard, or Home Assistant integration capabilities.

### Install from Source (Required)

```bash
# Clone the enhanced Home Assistant fork
git clone https://github.com/domalab/aioairctrl.git
cd aioairctrl

# Install with all dependencies
pip install -e .

# Or install with development tools
pip install -e ".[dev]"
```

### Verify Installation

After installation, verify you have the enhanced version with Home Assistant features:

```bash
# This command should be available (not in original package)
aioairctrl discover --help

# Check for Home Assistant integration features
aioairctrl setup --help
```

### Package Comparison

| Feature | Original aioairctrl (PyPI) | This Enhanced Fork |
|---------|---------------------------|-------------------|
| Basic device control | ✅ | ✅ |
| Device discovery | ❌ | ✅ |
| Home Assistant integration | ❌ | ✅ |
| Interactive setup wizard | ❌ | ✅ |
| JSON/YAML export | ❌ | ✅ |
| Comprehensive device analysis | ❌ | ✅ |

### Future PyPI Release

This enhanced version may be published to PyPI in the future under a different name (e.g., `aioairctrl-ha` or `aioairctrl-enhanced`) to avoid conflicts with the original package.

### Dependencies

The enhanced package automatically installs these dependencies:

- **Core functionality**: `pycryptodomex>=3.20.0`, `aiocoap>=0.4.7`
- **Device discovery**: `netifaces>=0.11.0` (network interface detection)
- **Output formatting**: `tabulate>=0.9.0` (pretty tables), `pyyaml>=6.0` (YAML export)
- **Interactive features**: `click>=8.0.0` (setup wizard)

## Quick Start

### 🔍 Device Discovery

Find all Philips air purifiers on your network:

```bash
# Discover all devices automatically
aioairctrl discover

# Scan specific network
aioairctrl discover -n 192.168.1.0/24

# Custom timeout
aioairctrl discover -t 10.0
```

**Example Output:**
```
🔍 Discovering Philips air purifiers on the network...

✅ Found 1 device(s):

+----------------+-----------+---------+------------+---------------+
| IP Address     | Model     | Name    | Firmware   | WiFi Signal   |
+================+===========+=========+============+===============+
| 192.168.20.151 | AC4220/12 | Bedroom | 0.2.1      | -52 dBm       |
+----------------+-----------+---------+------------+---------------+
```

### 🏠 Home Assistant Integration

#### Interactive Setup Wizard (Recommended)

For non-technical users, use the interactive setup wizard:

```bash
aioairctrl setup
```

This will:
1. 🔍 Discover devices on your network
2. 📊 Analyze device capabilities
3. 📁 Generate Home Assistant configuration files
4. 📋 Provide step-by-step integration instructions

#### Manual Device Analysis

Get comprehensive device information for Home Assistant integration:

```bash
# Get device info as JSON
aioairctrl device-info -H 192.168.1.100 --format json

# Export as YAML for Home Assistant
aioairctrl device-info -H 192.168.1.100 --format yaml

# Save to file
aioairctrl device-info -H 192.168.1.100 -o my_device.json
```

### 🎛️ Device Control

Basic device control commands:

```bash
# Get device status
aioairctrl status -H 192.168.1.100

# Get status in JSON format
aioairctrl status -H 192.168.1.100 --json

# Set device parameters
aioairctrl set -H 192.168.1.100 power=true mode=auto

# Monitor device status in real-time
aioairctrl status-observe -H 192.168.1.100
```

### Library Usage

```python
import asyncio
from aioairctrl import CoAPClient

async def main():
    # Connect to your air purifier
    client = await CoAPClient.create(host="192.168.1.100")

    try:
        # Get current status
        status, max_age = await client.get_status()
        print(f"Current status: {status}")
        print(f"Cache max age: {max_age} seconds")

        # Set power on and auto mode
        await client.set_control_values({
            "power": True,
            "mode": "auto"
        })

        # Monitor status changes
        async for status in client.observe_status():
            print(f"Status update: {status}")
            # Break after first update for demo
            break

    finally:
        await client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🏠 Home Assistant Integration

### Device Information Export

The `device-info` command provides comprehensive device analysis perfect for Home Assistant integration development:

```bash
aioairctrl device-info -H 192.168.1.100 --format json
```

**Sample Output Structure:**
```json
{
  "connection": {
    "host": "192.168.1.100",
    "protocol": "CoAP",
    "encryption": "AES-CBC"
  },
  "device": {
    "model_number": {"value": "AC4220/12", "description": "Model number"},
    "firmware_version": {"value": "0.2.1", "description": "Firmware version"}
  },
  "sensors": {
    "pm25_value": {"value": 12, "unit": "μg/m³", "device_class": "pm25"},
    "humidity_sensor": {"value": 45, "unit": "%", "device_class": "humidity"}
  },
  "controls": {
    "power": {"value": true, "type": "boolean"},
    "fan_speed": {"value": 2, "type": "integer"}
  },
  "capabilities": {
    "has_humidifier": true,
    "has_purifier": true,
    "has_pm25_sensor": true,
    "filter_types": ["main_filter", "hepa_filter"]
  },
  "home_assistant": {
    "platform": "philips_airpurifier",
    "host": "192.168.1.100",
    "model": "AC4220/12",
    "supported_features": ["fan_speed", "power", "humidity_target"],
    "sensors": [
      {"name": "PM2.5", "key": "D03224", "unit": "μg/m³", "device_class": "pm25"}
    ]
  }
}
```

### Contributing Device Information

Help expand Home Assistant support by contributing your device information:

1. **Discover your device:**
   ```bash
   aioairctrl discover
   ```

2. **Run the setup wizard:**
   ```bash
   aioairctrl setup
   ```

3. **Share your device data:**
   - Visit: https://github.com/domalab/ha-philips-airpurifier
   - Create a new issue titled "Device Support: [Your Model]"
   - Attach the generated JSON file from the setup wizard
   - Include any additional model-specific information

4. **Help test the integration:**
   - Install the Home Assistant integration
   - Test with your device using the generated configuration
   - Report any issues or missing features

### Generated Home Assistant Configuration

The tool automatically generates ready-to-use Home Assistant configurations:

```yaml
air_purifier:
  platform: philips_airpurifier
  host: 192.168.1.100
  name: "Living Room Air Purifier"
  model: "AC4220/12"
  unique_id: "philips_ac4220_livingroom"
  device_info:
    identifiers: ["96868ce0a7cb11ef9fbda30d1cde3e50"]
    manufacturer: "Philips"
    model: "AC4220/12"
    sw_version: "0.2.1"
  supported_features:
    - fan_speed
    - power
    - humidity_target
  sensors:
    - name: "PM2.5"
      key: "D03224"
      unit: "μg/m³"
      device_class: "pm25"
```

## API Reference

### CoAPClient

The main client class for interacting with Philips air purifiers.

#### Methods

- `CoAPClient.create(host, port=5683)` - Create and initialize a client
- `get_status()` - Get current device status
- `set_control_value(key, value)` - Set a single control parameter
- `set_control_values(data)` - Set multiple control parameters
- `observe_status()` - Async generator for real-time status updates
- `shutdown()` - Clean up resources

### New Modules

#### DeviceDiscovery

Network discovery for Philips air purifiers:

```python
from aioairctrl.discovery import DeviceDiscovery

discovery = DeviceDiscovery(timeout=5.0)
devices = await discovery.discover_devices()
```

#### DeviceInfoExtractor

Comprehensive device analysis:

```python
from aioairctrl.device_info import DeviceInfoExtractor

extractor = DeviceInfoExtractor("192.168.1.100")
device_info = await extractor.get_device_info()
json_output = extractor.export_json(device_info)
yaml_output = extractor.export_yaml(device_info)
```

#### SetupWizard

Interactive setup for Home Assistant integration:

```python
from aioairctrl.setup_wizard import SetupWizard

wizard = SetupWizard()
await wizard.run()
```

### Command Line Interface

```bash
# Device Discovery
aioairctrl discover [OPTIONS]
  -n, --network NETWORK    Specific network to scan (e.g., 192.168.1.0/24)
  -t, --timeout TIMEOUT    Discovery timeout in seconds (default: 5.0)

# Device Information
aioairctrl device-info -H HOST [OPTIONS]
  -H, --host HOST          Address of CoAP device (required)
  -P, --port PORT          Port of CoAP device (default: 5683)
  -f, --format FORMAT      Output format: json, yaml (default: json)
  -o, --output FILE        Output file (default: stdout)

# Interactive Setup
aioairctrl setup
  # No additional options - fully interactive

# Device Control
aioairctrl status -H HOST [OPTIONS]
  -H, --host HOST          Address of CoAP device (required)
  -P, --port PORT          Port of CoAP device (default: 5683)
  -J, --json               Output as JSON

aioairctrl status-observe -H HOST [OPTIONS]
  -H, --host HOST          Address of CoAP device (required)
  -P, --port PORT          Port of CoAP device (default: 5683)
  -J, --json               Output as JSON

aioairctrl set -H HOST [OPTIONS] K=V [K=V ...]
  -H, --host HOST          Address of CoAP device (required)
  -P, --port PORT          Port of CoAP device (default: 5683)
  -I, --int                Treat values as integers

# Global Options
  -D, --debug              Enable debug output
```

## 📊 Output Formats & Examples

### Device Discovery Output

```bash
$ aioairctrl discover
```

```
🔍 Discovering Philips air purifiers on the network...

Scanning networks: 192.168.1.0/24, 192.168.20.0/24

✅ Found 2 device(s):

+----------------+-----------+-------------+------------+---------------+
| IP Address     | Model     | Name        | Firmware   | WiFi Signal   |
+================+===========+=============+============+===============+
| 192.168.1.100  | AC2889/10 | Living Room | 1.0.3      | -45 dBm       |
| 192.168.20.151 | AC4220/12 | Bedroom     | 0.2.1      | -52 dBm       |
+----------------+-----------+-------------+------------+---------------+

💡 Use 'aioairctrl device-info -H <IP>' to get detailed information
💡 Use 'aioairctrl setup' for interactive Home Assistant setup
```

### Device Information JSON Export

```bash
$ aioairctrl device-info -H 192.168.1.100 --format json
```

Key sections of the JSON output:

```json
{
  "device": {
    "model_number": {"value": "AC4220/12", "type": "string"},
    "firmware_version": {"value": "0.2.1", "type": "string"},
    "serial_number": {"value": "688001001527", "type": "string"}
  },
  "sensors": {
    "pm25_value": {"value": 12, "unit": "μg/m³", "device_class": "pm25"},
    "humidity_sensor": {"value": 45, "unit": "%", "device_class": "humidity"},
    "air_quality_index": {"value": 2, "description": "Air quality index"}
  },
  "controls": {
    "power": {"value": true, "type": "boolean"},
    "fan_speed": {"value": 2, "type": "integer"},
    "auto_mode": {"value": true, "type": "boolean"}
  },
  "capabilities": {
    "has_humidifier": true,
    "has_purifier": true,
    "has_pm25_sensor": true,
    "has_humidity_sensor": true,
    "filter_types": ["main_filter", "hepa_filter"]
  }
}
```

### Home Assistant YAML Configuration

```bash
$ aioairctrl device-info -H 192.168.1.100 --format yaml
```

Generated configuration ready for Home Assistant:

```yaml
home_assistant:
  platform: philips_airpurifier
  host: 192.168.1.100
  name: Living Room Air Purifier
  model: AC4220/12
  unique_id: philips_ac4220_livingroom
  supported_features:
    - fan_speed
    - power
    - humidity_target
    - display_brightness
  sensors:
    - name: PM2.5
      key: D03224
      unit: μg/m³
      device_class: pm25
    - name: Humidity
      key: D03110
      unit: '%'
      device_class: humidity
    - name: Filter Life
      key: D03130
      unit: '%'
      device_class: battery
```

## Development

### Setting up Development Environment

```bash
git clone https://github.com/domalab/aioairctrl.git
cd aioairctrl

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aioairctrl

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

This project uses several tools to maintain code quality:

- **Black** - Code formatting
- **Flake8** - Linting
- **MyPy** - Type checking
- **Pytest** - Testing

```bash
# Format code
black aioairctrl tests

# Check linting
flake8 aioairctrl

# Type checking
mypy aioairctrl

# Run all quality checks
pre-commit run --all-files
```

## Protocol Details

This library communicates with Philips air purifiers using the CoAP (Constrained Application Protocol) with custom encryption:

- **Encryption**: AES-CBC with PKCS7 padding
- **Authentication**: SHA-256 HMAC
- **Key Exchange**: Custom sync protocol
- **Transport**: UDP on port 5683

## Troubleshooting

### Common Issues

1. **No devices found during discovery**:
   - Ensure your air purifier is connected to the same network
   - Check that the device is powered on and connected to WiFi
   - Try specifying a specific network: `aioairctrl discover -n 192.168.1.0/24`
   - Increase timeout: `aioairctrl discover -t 10.0`

2. **Connection refused**:
   - Verify the IP address is correct
   - Ensure the device is on the same network segment
   - Check firewall settings (UDP port 5683)

3. **Permission denied**:
   - Some systems require elevated privileges for network operations
   - Try running with `sudo` on Linux/macOS

4. **Timeout errors**:
   - Check network connectivity and firewall settings
   - Increase timeout values in discovery commands
   - Verify the device is not in sleep mode

5. **Setup wizard fails**:
   - Ensure you have write permissions to your home directory
   - Check that all dependencies are installed correctly
   - Run discovery manually first to verify device connectivity

### Debug Mode

Enable debug logging to see detailed protocol communication:

```bash
# For device control
aioairctrl status -H 192.168.1.100 -D

# For discovery (verbose network scanning)
aioairctrl discover -D

# For device analysis
aioairctrl device-info -H 192.168.1.100 -D
```

### Network Requirements

- **Protocol**: UDP CoAP on port 5683
- **Encryption**: AES-CBC with custom key exchange
- **Network**: Device and client must be on same network segment
- **Firewall**: Allow UDP traffic on port 5683

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. Follow the existing code style (Black formatting)
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original implementation by betaboon
- CoAP protocol implementation using [aiocoap](https://github.com/chrysn/aiocoap)
- Encryption using [pycryptodomex](https://github.com/Legrandin/pycryptodome)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.
