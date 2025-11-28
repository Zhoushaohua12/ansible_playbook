"""
Configuration Manager for health check system.

Handles loading, validation, and caching of configuration from YAML files
with support for environment variable overrides.
"""

import os
import re
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from ..exceptions import ConfigurationError


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Path to configuration file. If None, looks for config.yaml
                        in the same directory as this module.
        """
        self._config: Dict[str, Any] = {}
        self._config_path = config_path or os.path.join(
            os.path.dirname(__file__), 'config.yaml'
        )
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            config_file = Path(self._config_path)
            if not config_file.exists():
                # Create default config if it doesn't exist
                self._create_default_config()
                return
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
                
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config: {e}")
    
    def _create_default_config(self) -> None:
        """Create a default configuration file."""
        default_config = {
            'ssh': {
                'timeout': 30,
                'max_retries': 3,
                'retry_delay': 5,
                'key_file': None,
                'port': 22
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'health_check.log',
                'console': True
            },
            'checks': {
                'linux': {
                    'enabled': True,
                    'commands': {
                        'disk_usage': 'df -h',
                        'memory': 'free -m',
                        'cpu_load': 'uptime',
                        'services': 'systemctl list-units --type=service --state=failed',
                        'network': 'ip addr show'
                    }
                },
                'aix': {
                    'enabled': True,
                    'commands': {
                        'disk_usage': 'df -g',
                        'memory': 'svmon -G',
                        'cpu_load': 'uptime',
                        'services': 'lssrc -a',
                        'network': 'ifconfig -a'
                    }
                }
            },
            'report': {
                'output_dir': './reports',
                'formats': ['json', 'html'],
                'include_raw_output': False
            }
        }
        
        try:
            config_file = Path(self._config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            self._config = default_config
        except Exception as e:
            raise ConfigurationError(f"Failed to create default config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with support for environment variable overrides.
        
        Args:
            key: Configuration key in dot notation (e.g., 'ssh.timeout')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Check environment variable first
        env_key = f"HEALTH_CHECK_{key.upper().replace('.', '_')}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return self._convert_env_value(env_value)
        
        # Get from config
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        if re.match(r'^-?\d+$', value):
            return int(value)
        
        # Float conversion
        if re.match(r'^-?\d*\.\d+$', value):
            return float(value)
        
        return value
    
    def get_ssh_config(self) -> Dict[str, Any]:
        """Get SSH configuration."""
        return self.get('ssh', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def get_checks_config(self, os_type: str) -> Dict[str, Any]:
        """
        Get checks configuration for specific OS type.
        
        Args:
            os_type: 'linux' or 'aix'
            
        Returns:
            Checks configuration dictionary
        """
        return self.get(f'checks.{os_type}', {})
    
    def get_report_config(self) -> Dict[str, Any]:
        """Get report configuration."""
        return self.get('report', {})
    
    def validate_host_config(self, host_config: Dict[str, Any]) -> None:
        """
        Validate host configuration.
        
        Args:
            host_config: Host configuration dictionary
            
        Raises:
            ConfigurationError: If validation fails
        """
        required_fields = ['host', 'username']
        for field in required_fields:
            if field not in host_config:
                raise ConfigurationError(f"Missing required field: {field}")
        
        # Validate IP address or hostname
        host = host_config['host']
        if not self._is_valid_host(host):
            raise ConfigurationError(f"Invalid host: {host}")
        
        # Validate port
        port = host_config.get('port', 22)
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ConfigurationError(f"Invalid port: {port}")
    
    def _is_valid_host(self, host: str) -> bool:
        """Validate IP address or hostname."""
        # IPv4 pattern
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        # IPv6 pattern (simplified)
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4}$|^::1$|^::$|^([0-9a-fA-F]{1,4}:){1,7}:
        # Hostname pattern
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        return (re.match(ipv4_pattern, host) or 
                re.match(ipv6_pattern, host) or 
                re.match(hostname_pattern, host))
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()
        # Hostname pattern
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        return (re.match(ipv4_pattern, host) or 
                re.match(ipv6_pattern, host) or 
                re.match(hostname_pattern, host))
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()