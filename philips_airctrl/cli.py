import argparse
import asyncio
import json
import logging
import sys

from tabulate import tabulate

from philips_airctrl import CoAPClient
from philips_airctrl.device_info import DeviceInfoExtractor
from philips_airctrl.discovery import DeviceDiscovery
from philips_airctrl.setup_wizard import SetupWizard

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__package__)


def parse_args(args=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="sub-command help",
    )

    parser.add_argument(
        "-D",
        "--debug",
        dest="debug",
        action="store_true",
        help="Enable debug output",
    )
    parser_status = subparsers.add_parser(
        "status",
        help="get status of device",
    )
    parser_status.add_argument(
        "-H",
        "--host",
        dest="host",
        type=str,
        required=True,
        help="Address of CoAP device",
    )
    parser_status.add_argument(
        "-P",
        "--port",
        dest="port",
        type=int,
        default=5683,
        help="Port of CoAP device (default: %(default)s)",
    )
    parser_status.add_argument(
        "-J",
        "--json",
        dest="json",
        action="store_true",
        help="Output status as JSON",
    )
    parser_status_observe = subparsers.add_parser(
        "status-observe",
        help="Observe status of device",
    )
    parser_status_observe.add_argument(
        "-H",
        "--host",
        dest="host",
        type=str,
        required=True,
        help="Address of CoAP device",
    )
    parser_status_observe.add_argument(
        "-P",
        "--port",
        dest="port",
        type=int,
        default=5683,
        help="Port of CoAP device (default: %(default)s)",
    )
    parser_status_observe.add_argument(
        "-J",
        "--json",
        dest="json",
        action="store_true",
        help="Output status as JSON",
    )
    parser_set = subparsers.add_parser(
        "set",
        help="Set value of device",
    )
    parser_set.add_argument(
        "-H",
        "--host",
        dest="host",
        type=str,
        required=True,
        help="Address of CoAP device",
    )
    parser_set.add_argument(
        "-P",
        "--port",
        dest="port",
        type=int,
        default=5683,
        help="Port of CoAP device (default: %(default)s)",
    )
    parser_set.add_argument(
        "values",
        metavar="K=V",
        type=str,
        nargs="+",
        help="Key-Value pairs to set",
    )
    parser_set.add_argument(
        "-I",
        "--int",
        dest="value_as_int",
        action="store_true",
        help="Encode value as integer",
    )

    # Discovery command
    parser_discover = subparsers.add_parser(
        "discover",
        help="Discover Philips air purifiers on the network",
    )
    parser_discover.add_argument(
        "-n",
        "--network",
        dest="network",
        type=str,
        help="Specific network to scan (e.g., 192.168.1.0/24)",
    )
    parser_discover.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        type=float,
        default=5.0,
        help="Timeout for device discovery (default: %(default)s)",
    )

    # Device info command
    parser_device_info = subparsers.add_parser(
        "device-info",
        help="Get comprehensive device information",
    )
    parser_device_info.add_argument(
        "-H",
        "--host",
        dest="host",
        type=str,
        required=True,
        help="Address of CoAP device",
    )
    parser_device_info.add_argument(
        "-P",
        "--port",
        dest="port",
        type=int,
        default=5683,
        help="Port of CoAP device (default: %(default)s)",
    )
    parser_device_info.add_argument(
        "-f",
        "--format",
        dest="format",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: %(default)s)",
    )
    parser_device_info.add_argument(
        "-o",
        "--output",
        dest="output",
        type=str,
        help="Output file (default: stdout)",
    )

    # Setup wizard command
    parser_setup = subparsers.add_parser(
        "setup",
        help="Interactive setup wizard for Home Assistant integration",
    )

    return parser.parse_args(args)


async def handle_discover_command(args):
    """Handle the discover command."""
    print("🔍 Discovering Philips air purifiers on the network...")
    print()

    discovery = DeviceDiscovery(timeout=args.timeout)

    if args.network:
        devices = await discovery.discover_single_network(args.network)
        print(f"Scanning network: {args.network}")
    else:
        devices = await discovery.discover_devices()
        networks = discovery.get_network_ranges()
        print(f"Scanning networks: {', '.join(networks)}")

    print()

    if not devices:
        print("❌ No devices found.")
        print()
        print("Troubleshooting tips:")
        print("• Ensure your air purifier is connected to the same network")
        print("• Check that the device is powered on")
        print("• Verify your firewall allows UDP traffic on port 5683")
        print("• Try specifying a specific network with -n option")
        return

    print(f"✅ Found {len(devices)} device(s):")
    print()

    # Display devices in a table
    headers = ["IP Address", "Model", "Name", "Firmware", "WiFi Signal"]
    rows = []

    for device in devices:
        signal = f"{device.status.get('rssi', 'N/A')} dBm" if device.status else "N/A"
        rows.append([
            device.ip,
            device.model or "Unknown",
            device.name or "Unknown",
            device.firmware_version or "Unknown",
            signal
        ])

    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print()
    print("💡 Use 'philips-airctrl device-info -H <IP>' to get detailed information")
    print("💡 Use 'philips-airctrl setup' for interactive Home Assistant setup")


async def handle_device_info_command(args, client):
    """Handle the device-info command."""
    print(f"📊 Gathering device information from {args.host}...")

    extractor = DeviceInfoExtractor(args.host, args.port)
    device_info = await extractor.get_device_info()

    if args.format == "json":
        output = extractor.export_json(device_info, pretty=True)
    else:  # yaml
        output = extractor.export_yaml(device_info)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"✅ Device information saved to: {args.output}")
    else:
        print(output)


async def handle_setup_command(args):
    """Handle the setup command."""
    wizard = SetupWizard()
    await wizard.run()


async def async_main() -> None:
    args = parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("coap").setLevel(logging.DEBUG)
        logging.getLogger("philips_airpurifier").setLevel(logging.DEBUG)

    # Handle commands that don't require a specific host
    if args.command == "discover":
        await handle_discover_command(args)
        return
    elif args.command == "setup":
        await handle_setup_command(args)
        return

    # Commands that require a host
    if not hasattr(args, 'host') or not args.host:
        print("Error: Host is required for this command")
        return

    client = None
    try:
        client = await CoAPClient.create(host=args.host, port=args.port)
        if args.command == "status":
            status, max_age = await client.get_status()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(status)
                print(f"max_age = {max_age}")
        elif args.command == "status-observe":
            async for status in client.observe_status():
                if args.json:
                    print(json.dumps(status, indent=2))
                else:
                    print(status)
                sys.stdout.flush()
        elif args.command == "set":
            data = {}
            failed = False
            for e in args.values:
                k, v = e.split("=")
                if v == "true":
                    v = True
                elif v == "false":
                    v = False
                elif args.value_as_int:
                    try:
                        v = int(v)
                    except ValueError:
                        print("Cannot encode value '%s' as int" % v)
                        failed = True
                        break
                data[k] = v
            if not failed and data:
                await client.set_control_values(data=data)
        elif args.command == "device-info":
            await handle_device_info_command(args, client)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        if client:
            await client.shutdown()


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
