"""Device information extraction and formatting for Home Assistant integration."""
import json
import logging
from typing import Any, Dict, List, Optional

import yaml

from philips_airctrl.coap.client import Client

logger = logging.getLogger(__name__)


class DeviceInfoExtractor:
    """Extract comprehensive device information for Home Assistant integration."""
    
    # Known device status fields and their meanings
    DEVICE_FIELDS = {
        # Device identification
        'D01S03': {'name': 'device_name', 'type': 'string', 'description': 'Device name'},
        'D01S04': {'name': 'device_nickname', 'type': 'string', 'description': 'Device nickname'},
        'D01S05': {'name': 'model_number', 'type': 'string', 'description': 'Model number'},
        'D01S0D': {'name': 'serial_number', 'type': 'string', 'description': 'Serial number'},
        'D01S12': {'name': 'firmware_version', 'type': 'string', 'description': 'Firmware version'},
        'DeviceId': {'name': 'device_id', 'type': 'string', 'description': 'Unique device ID'},
        'ProductId': {'name': 'product_id', 'type': 'string', 'description': 'Product ID'},
        'WifiVersion': {'name': 'wifi_version', 'type': 'string', 'description': 'WiFi module version'},
        
        # Device status
        'D01102': {'name': 'error_code', 'type': 'integer', 'description': 'Error code'},
        'D01107': {'name': 'warning_code', 'type': 'integer', 'description': 'Warning code'},
        'D01108': {'name': 'device_status', 'type': 'integer', 'description': 'Device status'},
        'D01109': {'name': 'connection_status', 'type': 'integer', 'description': 'Connection status'},
        'D0110A': {'name': 'update_available', 'type': 'integer', 'description': 'Update available'},
        'D0110C': {'name': 'temperature', 'type': 'integer', 'description': 'Temperature (°C)'},
        'D0110F': {'name': 'language', 'type': 'integer', 'description': 'Language setting'},
        'D01213': {'name': 'child_lock', 'type': 'integer', 'description': 'Child lock status'},
        
        # Air quality and sensors
        'D03102': {'name': 'power', 'type': 'boolean', 'description': 'Power on/off'},
        'D03103': {'name': 'pm25_sensor', 'type': 'integer', 'description': 'PM2.5 sensor value'},
        'D03105': {'name': 'allergen_sensor', 'type': 'integer', 'description': 'Allergen sensor value'},
        'D03106': {'name': 'gas_sensor', 'type': 'integer', 'description': 'Gas sensor value'},
        'D0310A': {'name': 'fan_speed', 'type': 'integer', 'description': 'Fan speed setting'},
        'D0310C': {'name': 'target_humidity', 'type': 'integer', 'description': 'Target humidity (%)'},
        'D0310D': {'name': 'water_level', 'type': 'integer', 'description': 'Water level'},
        'D03110': {'name': 'humidity_sensor', 'type': 'integer', 'description': 'Humidity sensor value (%)'},
        'D03115': {'name': 'auto_mode', 'type': 'boolean', 'description': 'Auto mode enabled'},
        'D0311F': {'name': 'sleep_mode', 'type': 'boolean', 'description': 'Sleep mode enabled'},
        'D03120': {'name': 'display_brightness', 'type': 'integer', 'description': 'Display brightness'},
        'D03122': {'name': 'display_enabled', 'type': 'boolean', 'description': 'Display enabled'},
        'D03125': {'name': 'current_humidity', 'type': 'integer', 'description': 'Current humidity (%)'},
        'D0312A': {'name': 'humidifier_enabled', 'type': 'boolean', 'description': 'Humidifier enabled'},
        'D0312B': {'name': 'purifier_enabled', 'type': 'boolean', 'description': 'Purifier enabled'},
        'D0312C': {'name': 'air_quality_index', 'type': 'integer', 'description': 'Air quality index'},
        'D03130': {'name': 'filter_life', 'type': 'integer', 'description': 'Filter life remaining (%)'},
        'D03134': {'name': 'pre_filter_life', 'type': 'integer', 'description': 'Pre-filter life remaining (%)'},
        'D03135': {'name': 'hepa_filter_life', 'type': 'integer', 'description': 'HEPA filter life remaining (%)'},
        'D03136': {'name': 'carbon_filter_life', 'type': 'integer', 'description': 'Carbon filter life remaining (%)'},
        'D03180': {'name': 'timer_enabled', 'type': 'boolean', 'description': 'Timer enabled'},
        'D03182': {'name': 'schedule_enabled', 'type': 'boolean', 'description': 'Schedule enabled'},
        'D0313B': {'name': 'timer_remaining', 'type': 'integer', 'description': 'Timer remaining (minutes)'},
        
        # Advanced features
        'D03211': {'name': 'turbo_mode', 'type': 'boolean', 'description': 'Turbo mode enabled'},
        'D03221': {'name': 'allergen_mode', 'type': 'integer', 'description': 'Allergen mode setting'},
        'D03224': {'name': 'pm25_value', 'type': 'integer', 'description': 'PM2.5 value (μg/m³)'},
        'D03240': {'name': 'bacteria_virus_mode', 'type': 'boolean', 'description': 'Bacteria/virus mode'},
        
        # System information
        'Runtime': {'name': 'runtime', 'type': 'integer', 'description': 'Device runtime (seconds)'},
        'rssi': {'name': 'wifi_signal', 'type': 'integer', 'description': 'WiFi signal strength (dBm)'},
        'free_memory': {'name': 'free_memory', 'type': 'integer', 'description': 'Free memory (bytes)'},
        'StatusType': {'name': 'status_type', 'type': 'string', 'description': 'Status message type'},
        'ConnectType': {'name': 'connect_type', 'type': 'string', 'description': 'Connection type'},
        
        # Filter and maintenance
        'D05102': {'name': 'filter_type', 'type': 'integer', 'description': 'Filter type'},
        'D05207': {'name': 'filter_usage_hours', 'type': 'integer', 'description': 'Filter usage (hours)'},
        'D05408': {'name': 'filter_total_hours', 'type': 'integer', 'description': 'Filter total hours'},
        'D0520D': {'name': 'pre_filter_usage', 'type': 'integer', 'description': 'Pre-filter usage (hours)'},
        'D0540E': {'name': 'pre_filter_total', 'type': 'integer', 'description': 'Pre-filter total hours'},
    }
    
    def __init__(self, host: str, port: int = 5683):
        self.host = host
        self.port = port
        
    async def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information."""
        client = await Client.create(host=self.host, port=self.port)
        
        try:
            # Get device status
            status, max_age = await client.get_status()
            
            # Extract and categorize information
            device_info = {
                'connection': {
                    'host': self.host,
                    'port': self.port,
                    'max_age': max_age,
                    'protocol': 'CoAP',
                    'encryption': 'AES-CBC'
                },
                'device': {},
                'sensors': {},
                'controls': {},
                'filters': {},
                'system': {},
                'raw_status': status,
                'capabilities': self._analyze_capabilities(status),
                'home_assistant': self._generate_ha_config(status)
            }
            
            # Categorize all status fields
            for key, value in status.items():
                if key in self.DEVICE_FIELDS:
                    field_info = self.DEVICE_FIELDS[key]
                    category = self._get_field_category(key)
                    
                    device_info[category][field_info['name']] = {
                        'value': value,
                        'type': field_info['type'],
                        'description': field_info['description'],
                        'raw_key': key
                    }
                else:
                    # Unknown field - add to system category
                    device_info['system'][key] = {
                        'value': value,
                        'type': type(value).__name__,
                        'description': 'Unknown field',
                        'raw_key': key
                    }
            
            return device_info
            
        finally:
            await client.shutdown()
    
    def _get_field_category(self, key: str) -> str:
        """Determine the category for a field."""
        if key in ['D01S03', 'D01S04', 'D01S05', 'D01S0D', 'D01S12', 'DeviceId', 'ProductId', 'WifiVersion']:
            return 'device'
        elif key in ['D03103', 'D03105', 'D03106', 'D03110', 'D03125', 'D0312C', 'D03224', 'rssi']:
            return 'sensors'
        elif key in ['D03102', 'D0310A', 'D0310C', 'D03115', 'D0311F', 'D03120', 'D03122', 'D0312A', 'D0312B', 'D03180', 'D03182', 'D0313B', 'D03211', 'D03221', 'D03240']:
            return 'controls'
        elif key in ['D03130', 'D03134', 'D03135', 'D03136', 'D05102', 'D05207', 'D05408', 'D0520D', 'D0540E']:
            return 'filters'
        else:
            return 'system'
    
    def _analyze_capabilities(self, status: Dict) -> Dict[str, Any]:
        """Analyze device capabilities based on available status fields."""
        capabilities = {
            'has_humidifier': 'D0312A' in status,
            'has_purifier': 'D0312B' in status,
            'has_pm25_sensor': 'D03103' in status or 'D03224' in status,
            'has_humidity_sensor': 'D03110' in status,
            'has_allergen_sensor': 'D03105' in status,
            'has_gas_sensor': 'D03106' in status,
            'has_display': 'D03120' in status or 'D03122' in status,
            'has_timer': 'D03180' in status,
            'has_schedule': 'D03182' in status,
            'has_child_lock': 'D01213' in status,
            'has_sleep_mode': 'D0311F' in status,
            'has_turbo_mode': 'D03211' in status,
            'has_allergen_mode': 'D03221' in status,
            'has_bacteria_virus_mode': 'D03240' in status,
            'filter_types': []
        }
        
        # Determine filter types
        if 'D03130' in status:
            capabilities['filter_types'].append('main_filter')
        if 'D03134' in status:
            capabilities['filter_types'].append('pre_filter')
        if 'D03135' in status:
            capabilities['filter_types'].append('hepa_filter')
        if 'D03136' in status:
            capabilities['filter_types'].append('carbon_filter')
            
        return capabilities
    
    def _generate_ha_config(self, status: Dict) -> Dict[str, Any]:
        """Generate Home Assistant configuration suggestions."""
        model = status.get('D01S05', 'Unknown')
        name = status.get('D01S03', 'Air Purifier')
        
        config = {
            'platform': 'philips_airpurifier',
            'host': self.host,
            'name': name,
            'model': model,
            'unique_id': status.get('DeviceId', f"philips_{self.host.replace('.', '_')}"),
            'device_info': {
                'identifiers': [status.get('DeviceId', f"philips_{self.host}")],
                'name': name,
                'manufacturer': 'Philips',
                'model': model,
                'sw_version': status.get('D01S12', 'Unknown'),
                'hw_version': status.get('WifiVersion', 'Unknown')
            },
            'supported_features': [],
            'sensors': [],
            'binary_sensors': [],
            'switches': []
        }
        
        # Add supported features based on capabilities
        capabilities = self._analyze_capabilities(status)
        
        if capabilities['has_purifier']:
            config['supported_features'].append('fan_speed')
            config['supported_features'].append('power')
            
        if capabilities['has_humidifier']:
            config['supported_features'].append('humidity_target')
            
        if capabilities['has_display']:
            config['supported_features'].append('display_brightness')
            
        # Add sensor configurations
        if capabilities['has_pm25_sensor']:
            config['sensors'].append({
                'name': 'PM2.5',
                'key': 'D03224',
                'unit': 'μg/m³',
                'device_class': 'pm25'
            })
            
        if capabilities['has_humidity_sensor']:
            config['sensors'].append({
                'name': 'Humidity',
                'key': 'D03110',
                'unit': '%',
                'device_class': 'humidity'
            })
            
        # Add filter sensors
        for filter_type in capabilities['filter_types']:
            if filter_type == 'main_filter':
                config['sensors'].append({
                    'name': 'Filter Life',
                    'key': 'D03130',
                    'unit': '%',
                    'device_class': 'battery'
                })
                
        return config
    
    def export_json(self, device_info: Dict, pretty: bool = True) -> str:
        """Export device info as JSON."""
        if pretty:
            return json.dumps(device_info, indent=2, default=str)
        return json.dumps(device_info, default=str)
    
    def export_yaml(self, device_info: Dict) -> str:
        """Export device info as YAML."""
        return yaml.dump(device_info, default_flow_style=False, sort_keys=False)
