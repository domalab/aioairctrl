# philips-airctrl

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration%20Ready-blue.svg)](https://www.home-assistant.io/)

An enhanced async Python library and command-line utilities for controlling Philips air purifiers using encrypted CoAP (Constrained Application Protocol). This fork adds comprehensive **device discovery**, **technical data extraction**, and **developer tools** to help expand Home Assistant integration support for new air purifier models.

## 🎯 **What This Tool Does**

**✅ FOR DEVELOPERS**: Extract comprehensive technical data from Philips air purifiers to help add support for new models in Home Assistant integrations

**✅ FOR USERS**: Contribute device information to help developers expand device support

## Features

- **🔍 Automatic Device Discovery** - Find Philips air purifiers on your network automatically
- **📊 Comprehensive Device Analysis** - Extract 70+ data points with capability detection
- **🔧 Developer Data Collection** - Generate standardized device information for integration developers
- **🧙‍♂️ Interactive Setup Wizard** - User-friendly guided device information collection
- **📁 Multiple Export Formats** - JSON and YAML output for developer use
- **🤝 Community Contribution** - Easy device info sharing for Home Assistant integration projects
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

> **⚠️ Important**: This enhanced version with device discovery and data extraction features is **only available from source**. The original `aioairctrl` package on PyPI does not include device discovery or comprehensive device analysis capabilities.

### Install from Source (Required)

```bash
# Clone the enhanced device discovery fork
git clone https://github.com/domalab/philips-airctrl.git
cd philips-airctrl

# Install with all dependencies
pip install -e .

# Or install with development tools
pip install -e ".[dev]"
```

### Verify Installation

After installation, verify you have the enhanced version with device discovery features:

```bash
# This command should be available (not in original package)
philips-airctrl discover --help

# Check for device information extraction features
philips-airctrl device-info --help
```

### Package Comparison

| Feature | Original aioairctrl (PyPI) | This Enhanced Fork |
|---------|---------------------------|-------------------|
| Basic device control | ✅ | ✅ |
| Device discovery | ❌ | ✅ |
| Device data extraction | ❌ | ✅ |
| Interactive setup wizard | ❌ | ✅ |
| JSON/YAML export | ❌ | ✅ |
| Comprehensive device analysis | ❌ | ✅ |

### Future PyPI Release

This enhanced version may be published to PyPI in the future under a different name (e.g., `philips-airctrl-ha` or `philips-airctrl-enhanced`) to avoid conflicts with the original package.

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
philips-airctrl discover

# Scan specific network
philips-airctrl discover -n 192.168.1.0/24

# Custom timeout
philips-airctrl discover -t 10.0
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

### 🔧 Device Data Collection for Developers

#### Interactive Device Information Collection (Recommended)

Use the interactive wizard to collect comprehensive device information:

```bash
philips-airctrl setup
```

This will:
1. 🔍 Discover devices on your network
2. 📊 Analyze device capabilities and extract technical specifications
3. 📁 Generate standardized JSON/YAML reports for developers
4. 📋 Provide instructions for sharing data with integration developers

#### Manual Device Analysis

Extract comprehensive device information for integration development:

```bash
# Get device info as JSON for developers
philips-airctrl device-info -H 192.168.1.100 --format json

# Export as YAML for easier reading
philips-airctrl device-info -H 192.168.1.100 --format yaml

# Save to file for sharing with developers
philips-airctrl device-info -H 192.168.1.100 -o my_device_info.json
```

### 🎛️ Device Control

Basic device control commands:

```bash
# Get device status
philips-airctrl status -H 192.168.1.100

# Get status in JSON format
philips-airctrl status -H 192.168.1.100 --json

# Set device parameters
philips-airctrl set -H 192.168.1.100 power=true mode=auto

# Monitor device status in real-time
philips-airctrl status-observe -H 192.168.1.100
```

### Library Usage

```python
import asyncio
from philips_airctrl import CoAPClient

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

## 🔧 Developer Resources

### Device Information Export for Integration Development

The `device-info` command extracts comprehensive technical data that developers need to add support for new air purifier models in Home Assistant integrations:

```bash
philips-airctrl device-info -H 192.168.1.100 --format json
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

### How to Help Expand Device Support

**🎯 Purpose**: Help developers add support for your air purifier model in existing Home Assistant integrations

**👥 Target Audience**: Users who want to contribute device data to help developers

#### Step-by-Step Process:

1. **Discover your device:**
   ```bash
   philips-airctrl discover
   ```

2. **Extract device information:**
   ```bash
   philips-airctrl setup
   ```
   This generates a comprehensive technical report about your device.

3. **Share your device data with developers:**
   - **For Philips Air Purifier Integration**: Visit https://github.com/domalab/ha-philips-airpurifier
   - **For other integrations**: Check the integration's GitHub repository
   - Create a new issue titled "Device Support: [Your Model]"
   - Attach the generated JSON file from the setup wizard
   - Include your device model number and any unique features

4. **What happens next:**
   - Developers use your data to understand your device's capabilities
   - They add support for your model to the integration
   - You can test the updated integration once it's released

### Important Note About Configuration

**⚠️ This tool does NOT generate ready-to-use Home Assistant configurations!**

The JSON/YAML output contains technical device information that **developers** use to add support for your device model in existing Home Assistant integrations.

**What this tool provides:**
- Device capability analysis
- Sensor and control mapping
- Technical specifications
- Raw device data

**What you need to do:**
1. Share the generated data with integration developers
2. Wait for developers to add support for your model
3. Install/update the Home Assistant integration once support is added
4. Configure the integration through Home Assistant's UI

**For actual Home Assistant setup**, refer to the documentation of existing integrations like:
- [Philips Air Purifier Integration](https://github.com/domalab/ha-philips-airpurifier)
- [Home Assistant Core Philips Integration](https://www.home-assistant.io/integrations/philips_js/)

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
from philips_airctrl.discovery import DeviceDiscovery

discovery = DeviceDiscovery(timeout=5.0)
devices = await discovery.discover_devices()
```

#### DeviceInfoExtractor

Comprehensive device analysis:

```python
from philips_airctrl.device_info import DeviceInfoExtractor

extractor = DeviceInfoExtractor("192.168.1.100")
device_info = await extractor.get_device_info()
json_output = extractor.export_json(device_info)
yaml_output = extractor.export_yaml(device_info)
```

#### SetupWizard

Interactive device information collection for developers:

```python
from philips_airctrl.setup_wizard import SetupWizard

wizard = SetupWizard()
await wizard.run()
```

### Command Line Interface

```bash
# Device Discovery
philips-airctrl discover [OPTIONS]
  -n, --network NETWORK    Specific network to scan (e.g., 192.168.1.0/24)
  -t, --timeout TIMEOUT    Discovery timeout in seconds (default: 5.0)

# Device Information
philips-airctrl device-info -H HOST [OPTIONS]
  -H, --host HOST          Address of CoAP device (required)
  -P, --port PORT          Port of CoAP device (default: 5683)
  -f, --format FORMAT      Output format: json, yaml (default: json)
  -o, --output FILE        Output file (default: stdout)

# Interactive Device Data Collection
philips-airctrl setup
  # No additional options - fully interactive device information collection

# Device Control
philips-airctrl status -H HOST [OPTIONS]
  -H, --host HOST          Address of CoAP device (required)
  -P, --port PORT          Port of CoAP device (default: 5683)
  -J, --json               Output as JSON

philips-airctrl status-observe -H HOST [OPTIONS]
  -H, --host HOST          Address of CoAP device (required)
  -P, --port PORT          Port of CoAP device (default: 5683)
  -J, --json               Output as JSON

philips-airctrl set -H HOST [OPTIONS] K=V [K=V ...]
  -H, --host HOST          Address of CoAP device (required)
  -P, --port PORT          Port of CoAP device (default: 5683)
  -I, --int                Treat values as integers

# Global Options
  -D, --debug              Enable debug output
```

## 📊 Output Formats & Examples

### Device Discovery Output

```bash
$ philips-airctrl discover
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

💡 Use 'philips-airctrl device-info -H <IP>' to extract technical device data
💡 Use 'philips-airctrl setup' to collect device info for developers
```

### Device Information JSON Export

```bash
$ philips-airctrl device-info -H 192.168.1.100 --format json
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

### Device Technical Data in YAML Format

```bash
$ philips-airctrl device-info -H 192.168.1.100 --format yaml
```

**⚠️ Note**: This is technical data for developers, NOT a ready-to-use Home Assistant configuration!

Sample technical data structure:

```yaml
device:
  model_number: "AC4220/12"
  firmware_version: "0.2.1"
  serial_number: "688001001527"

capabilities:
  has_humidifier: true
  has_purifier: true
  has_pm25_sensor: true
  filter_types: ["main_filter", "hepa_filter"]

sensors:
  pm25_value:
    key: "D03224"
    unit: "μg/m³"
    device_class: "pm25"
  humidity_sensor:
    key: "D03110"
    unit: "%"
    device_class: "humidity"

# This data helps developers understand your device's capabilities
# and add support to existing Home Assistant integrations
```

## Development

### Setting up Development Environment

```bash
git clone https://github.com/domalab/philips-airctrl.git
cd philips-airctrl

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
pytest --cov=philips_airctrl

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
black philips_airctrl tests

# Check linting
flake8 philips_airctrl

# Type checking
mypy philips_airctrl

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
   - Try specifying a specific network: `philips-airctrl discover -n 192.168.1.0/24`
   - Increase timeout: `philips-airctrl discover -t 10.0`

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
philips-airctrl status -H 192.168.1.100 -D

# For discovery (verbose network scanning)
philips-airctrl discover -D

# For device analysis
philips-airctrl device-info -H 192.168.1.100 -D
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
