"""Interactive setup wizard for Home Assistant integration."""
import asyncio
import json
import os
from pathlib import Path
from typing import List, Optional

import click
import yaml
from tabulate import tabulate

from aioairctrl.device_info import DeviceInfoExtractor
from aioairctrl.discovery import DeviceDiscovery, DeviceInfo


class SetupWizard:
    """Interactive setup wizard for discovering and configuring devices."""
    
    def __init__(self):
        self.discovered_devices: List[DeviceInfo] = []
        self.selected_device: Optional[DeviceInfo] = None
        
    async def run(self):
        """Run the interactive setup wizard."""
        click.echo("🔍 Philips Air Purifier Setup Wizard")
        click.echo("=" * 50)
        click.echo()
        
        # Step 1: Device Discovery
        await self._discovery_step()
        
        if not self.discovered_devices:
            click.echo("❌ No devices found. Please check:")
            click.echo("   • Your air purifier is connected to the same network")
            click.echo("   • The device is powered on")
            click.echo("   • Your firewall allows UDP traffic on port 5683")
            return
        
        # Step 2: Device Selection
        self._device_selection_step()
        
        if not self.selected_device:
            click.echo("❌ No device selected. Exiting.")
            return
        
        # Step 3: Device Information Gathering
        await self._device_info_step()
        
        # Step 4: Generate Configuration
        await self._configuration_step()
        
        # Step 5: Next Steps
        self._next_steps()
    
    async def _discovery_step(self):
        """Step 1: Discover devices on the network."""
        click.echo("🔍 Step 1: Discovering devices...")
        click.echo()
        
        # Ask user about network scope
        if click.confirm("Do you want to scan all local networks? (recommended)", default=True):
            networks = None
        else:
            network = click.prompt("Enter network to scan (e.g., 192.168.1.0/24)")
            networks = [network]
        
        # Perform discovery
        discovery = DeviceDiscovery(timeout=3.0)
        
        with click.progressbar(length=100, label="Scanning network...") as bar:
            # Start discovery in background
            discovery_task = asyncio.create_task(discovery.discover_devices(networks))
            
            # Update progress bar
            for i in range(100):
                await asyncio.sleep(0.1)
                bar.update(1)
                
                # Check if discovery is complete
                if discovery_task.done():
                    bar.update(100 - i)
                    break
            
            # Get results
            self.discovered_devices = await discovery_task
        
        click.echo()
        if self.discovered_devices:
            click.echo(f"✅ Found {len(self.discovered_devices)} device(s)!")
            self._display_devices_table()
        else:
            click.echo("❌ No devices found.")
    
    def _device_selection_step(self):
        """Step 2: Let user select a device."""
        click.echo()
        click.echo("📱 Step 2: Select your device")
        click.echo()
        
        if len(self.discovered_devices) == 1:
            device = self.discovered_devices[0]
            if click.confirm(f"Use device '{device.name}' at {device.ip}?", default=True):
                self.selected_device = device
                return
        
        # Multiple devices - show selection
        click.echo("Available devices:")
        for i, device in enumerate(self.discovered_devices, 1):
            click.echo(f"  {i}. {device.name} ({device.model}) at {device.ip}")
        
        while True:
            try:
                choice = click.prompt("Select device number", type=int)
                if 1 <= choice <= len(self.discovered_devices):
                    self.selected_device = self.discovered_devices[choice - 1]
                    break
                else:
                    click.echo(f"Please enter a number between 1 and {len(self.discovered_devices)}")
            except (ValueError, click.Abort):
                click.echo("Invalid selection. Please try again.")
    
    async def _device_info_step(self):
        """Step 3: Gather detailed device information."""
        click.echo()
        click.echo("📊 Step 3: Gathering device information...")
        click.echo()
        
        device = self.selected_device
        extractor = DeviceInfoExtractor(device.ip, device.port)
        
        try:
            with click.progressbar(length=100, label="Analyzing device...") as bar:
                # Simulate progress while gathering info
                info_task = asyncio.create_task(extractor.get_device_info())
                
                for i in range(100):
                    await asyncio.sleep(0.05)
                    bar.update(1)
                    
                    if info_task.done():
                        bar.update(100 - i)
                        break
                
                device_info = await info_task
                self.device_info = device_info
            
            click.echo()
            click.echo("✅ Device analysis complete!")
            self._display_device_summary()
            
        except Exception as e:
            click.echo(f"❌ Error gathering device info: {e}")
            self.device_info = None
    
    async def _configuration_step(self):
        """Step 4: Generate and save configuration."""
        click.echo()
        click.echo("⚙️  Step 4: Generating configuration...")
        click.echo()
        
        if not self.device_info:
            click.echo("❌ No device information available.")
            return
        
        # Create output directory
        output_dir = Path.home() / "philips_airpurifier_config"
        output_dir.mkdir(exist_ok=True)
        
        device = self.selected_device
        device_name = device.name.replace(' ', '_').lower()
        
        # Save full device info as JSON
        json_file = output_dir / f"{device_name}_device_info.json"
        with open(json_file, 'w') as f:
            json.dump(self.device_info, f, indent=2, default=str)
        
        # Save Home Assistant config as YAML
        ha_config = self.device_info['home_assistant']
        yaml_file = output_dir / f"{device_name}_ha_config.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump({'air_purifier': ha_config}, f, default_flow_style=False)
        
        # Save summary report
        summary_file = output_dir / f"{device_name}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(self._generate_summary_report())
        
        click.echo(f"✅ Configuration saved to: {output_dir}")
        click.echo(f"   • Device info: {json_file.name}")
        click.echo(f"   • HA config:   {yaml_file.name}")
        click.echo(f"   • Summary:     {summary_file.name}")
    
    def _next_steps(self):
        """Step 5: Show next steps for Home Assistant integration."""
        click.echo()
        click.echo("🎉 Setup Complete!")
        click.echo("=" * 50)
        click.echo()
        click.echo("Next steps for Home Assistant integration:")
        click.echo()
        click.echo("1. 📋 Share your device information:")
        click.echo("   • Visit: https://github.com/domalab/ha-philips-airpurifier")
        click.echo("   • Create a new issue with your device info")
        click.echo("   • Attach the generated JSON file")
        click.echo()
        click.echo("2. 🏠 Install Home Assistant integration:")
        click.echo("   • Add the custom integration to HACS")
        click.echo("   • Use the generated YAML configuration")
        click.echo("   • Restart Home Assistant")
        click.echo()
        click.echo("3. 🔧 Test the integration:")
        click.echo("   • Check if your device appears in Home Assistant")
        click.echo("   • Test basic controls (power, fan speed)")
        click.echo("   • Monitor sensor readings")
        click.echo()
        click.echo("4. 🤝 Help improve the integration:")
        click.echo("   • Report any issues on GitHub")
        click.echo("   • Share feedback about missing features")
        click.echo("   • Help test new device models")
        click.echo()
        
        if click.confirm("Would you like to open the GitHub repository now?", default=False):
            click.launch("https://github.com/domalab/ha-philips-airpurifier")
    
    def _display_devices_table(self):
        """Display discovered devices in a table."""
        headers = ["IP Address", "Model", "Name", "Firmware", "Signal"]
        rows = []
        
        for device in self.discovered_devices:
            signal = f"{device.status.get('rssi', 'N/A')} dBm" if device.status else "N/A"
            rows.append([
                device.ip,
                device.model or "Unknown",
                device.name or "Unknown",
                device.firmware_version or "Unknown",
                signal
            ])
        
        click.echo()
        click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
    
    def _display_device_summary(self):
        """Display a summary of the selected device."""
        device = self.selected_device
        info = self.device_info
        
        click.echo(f"Device: {device.name} ({device.model})")
        click.echo(f"IP: {device.ip}")
        click.echo(f"Firmware: {device.firmware_version}")
        click.echo()
        
        # Show capabilities
        capabilities = info['capabilities']
        click.echo("Capabilities:")
        for cap, enabled in capabilities.items():
            if isinstance(enabled, bool):
                status = "✅" if enabled else "❌"
                cap_name = cap.replace('has_', '').replace('_', ' ').title()
                click.echo(f"  {status} {cap_name}")
        
        # Show sensor count
        sensor_count = len([k for k in info['sensors'].keys()])
        control_count = len([k for k in info['controls'].keys()])
        click.echo()
        click.echo(f"Sensors: {sensor_count}")
        click.echo(f"Controls: {control_count}")
    
    def _generate_summary_report(self) -> str:
        """Generate a text summary report."""
        device = self.selected_device
        info = self.device_info
        
        report = f"""Philips Air Purifier Device Report
Generated by aioairctrl setup wizard

DEVICE INFORMATION
==================
Name: {device.name}
Model: {device.model}
IP Address: {device.ip}
Serial Number: {device.serial_number}
Firmware Version: {device.firmware_version}
WiFi Version: {device.wifi_version}
Device ID: {device.device_id}
Product ID: {device.product_id}

CAPABILITIES
============
"""
        
        capabilities = info['capabilities']
        for cap, enabled in capabilities.items():
            if isinstance(enabled, bool):
                status = "Yes" if enabled else "No"
                cap_name = cap.replace('has_', '').replace('_', ' ').title()
                report += f"{cap_name}: {status}\n"
        
        report += f"""
SENSORS ({len(info['sensors'])})
=======
"""
        for name, sensor in info['sensors'].items():
            report += f"• {sensor['description']}: {sensor['value']} (Key: {sensor['raw_key']})\n"
        
        report += f"""
CONTROLS ({len(info['controls'])})
========
"""
        for name, control in info['controls'].items():
            report += f"• {control['description']}: {control['value']} (Key: {control['raw_key']})\n"
        
        report += """
HOME ASSISTANT INTEGRATION
==========================
This device information can be used to improve the Home Assistant
Philips Air Purifier integration. Please share this data at:
https://github.com/domalab/ha-philips-airpurifier

The generated configuration files can be used directly with the
Home Assistant integration once it supports your device model.
"""
        
        return report
