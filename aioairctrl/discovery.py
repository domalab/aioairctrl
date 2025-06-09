"""Device discovery functionality for Philips air purifiers."""
import asyncio
import ipaddress
import logging
import socket
from typing import Dict, List, Optional, Tuple

import netifaces
from aiocoap import Context, Message, NON
from aiocoap.numbers.codes import GET

from aioairctrl.coap.client import Client

logger = logging.getLogger(__name__)


class DeviceInfo:
    """Information about a discovered device."""
    
    def __init__(self, ip: str, port: int = 5683):
        self.ip = ip
        self.port = port
        self.model = None
        self.name = None
        self.device_id = None
        self.product_id = None
        self.firmware_version = None
        self.wifi_version = None
        self.serial_number = None
        self.status = None
        self.reachable = False
        
    def to_dict(self) -> Dict:
        """Convert device info to dictionary."""
        return {
            'ip': self.ip,
            'port': self.port,
            'model': self.model,
            'name': self.name,
            'device_id': self.device_id,
            'product_id': self.product_id,
            'firmware_version': self.firmware_version,
            'wifi_version': self.wifi_version,
            'serial_number': self.serial_number,
            'reachable': self.reachable,
            'status': self.status
        }


class DeviceDiscovery:
    """Discover Philips air purifier devices on the network."""
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        
    def get_network_ranges(self) -> List[str]:
        """Get all local network ranges to scan."""
        networks = []
        
        try:
            # Get all network interfaces
            interfaces = netifaces.interfaces()
            
            for interface in interfaces:
                # Skip loopback and non-active interfaces
                if interface.startswith('lo'):
                    continue
                    
                addrs = netifaces.ifaddresses(interface)
                
                # Check IPv4 addresses
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        ip = addr_info.get('addr')
                        netmask = addr_info.get('netmask')
                        
                        if ip and netmask and not ip.startswith('127.'):
                            try:
                                # Create network from IP and netmask
                                network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                                networks.append(str(network))
                            except (ipaddress.AddressValueError, ValueError):
                                continue
                                
        except Exception as e:
            logger.warning(f"Error getting network interfaces: {e}")
            # Fallback to common private networks
            networks = ['192.168.1.0/24', '192.168.0.0/24', '10.0.0.0/24']
            
        return networks
    
    async def scan_ip(self, ip: str) -> Optional[DeviceInfo]:
        """Scan a single IP address for a Philips air purifier."""
        try:
            # Quick port check first
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1.0)
            try:
                # Try to connect to CoAP port
                result = sock.connect_ex((ip, 5683))
                sock.close()
                
                # If port is not reachable, skip
                if result != 0:
                    return None
            except Exception:
                sock.close()
                return None
            
            # Try to connect with CoAP client
            device_info = DeviceInfo(ip)
            
            try:
                client = await asyncio.wait_for(
                    Client.create(host=ip, port=5683), 
                    timeout=self.timeout
                )
                
                try:
                    # Get device status
                    status, _ = await asyncio.wait_for(
                        client.get_status(), 
                        timeout=self.timeout
                    )
                    
                    # Extract device information from status
                    device_info.reachable = True
                    device_info.status = status
                    device_info.model = status.get('D01S05', 'Unknown')
                    device_info.name = status.get('D01S03', 'Unknown')
                    device_info.device_id = status.get('DeviceId')
                    device_info.product_id = status.get('ProductId')
                    device_info.firmware_version = status.get('D01S12')
                    device_info.wifi_version = status.get('WifiVersion')
                    device_info.serial_number = status.get('D01S0D')
                    
                    logger.info(f"Found Philips air purifier at {ip}: {device_info.model}")
                    return device_info
                    
                finally:
                    await client.shutdown()
                    
            except asyncio.TimeoutError:
                logger.debug(f"Timeout connecting to {ip}")
                return None
            except Exception as e:
                logger.debug(f"Error connecting to {ip}: {e}")
                return None
                
        except Exception as e:
            logger.debug(f"Error scanning {ip}: {e}")
            return None
    
    async def discover_devices(self, networks: Optional[List[str]] = None) -> List[DeviceInfo]:
        """Discover all Philips air purifier devices on the network."""
        if networks is None:
            networks = self.get_network_ranges()
        
        logger.info(f"Scanning networks: {networks}")
        
        # Generate all IP addresses to scan
        ips_to_scan = []
        for network_str in networks:
            try:
                network = ipaddress.IPv4Network(network_str, strict=False)
                # Limit scan to reasonable size networks (max /16)
                if network.prefixlen < 16:
                    logger.warning(f"Skipping large network {network_str} (prefix < 16)")
                    continue
                    
                # Skip network and broadcast addresses
                for ip in network.hosts():
                    ips_to_scan.append(str(ip))
                    
            except ipaddress.AddressValueError:
                logger.warning(f"Invalid network: {network_str}")
                continue
        
        logger.info(f"Scanning {len(ips_to_scan)} IP addresses...")
        
        # Scan IPs in parallel with limited concurrency
        semaphore = asyncio.Semaphore(20)  # Limit concurrent scans
        
        async def scan_with_semaphore(ip):
            async with semaphore:
                return await self.scan_ip(ip)
        
        # Execute scans
        tasks = [scan_with_semaphore(ip) for ip in ips_to_scan]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        devices = []
        for result in results:
            if isinstance(result, DeviceInfo):
                devices.append(result)
            elif isinstance(result, Exception):
                logger.debug(f"Scan error: {result}")
        
        logger.info(f"Discovery complete. Found {len(devices)} devices.")
        return devices
    
    async def discover_single_network(self, network: str) -> List[DeviceInfo]:
        """Discover devices on a single network."""
        return await self.discover_devices([network])
