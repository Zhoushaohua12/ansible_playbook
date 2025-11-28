"""
Tests for ConfigManager class.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch
from health_check.config.config_manager import ConfigManager
from health_check.exceptions import ConfigurationError


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    def test_init_with_default_config(self, temp_config_file):
        """Test initialization with default config file."""
        config_manager = ConfigManager(temp_config_file)
        assert config_manager.get('ssh.timeout') == 30
        assert config_manager.get('ssh.port') == 22
    
    def test_init_creates_default_config(self):
        """Test that default config is created when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'test_config.yaml')
            config_manager = ConfigManager(config_path)
            
            # Check that config file was created
            assert os.path.exists(config_path)
            
            # Check default values
            assert config_manager.get('ssh.timeout') == 30
            assert config_manager.get('logging.level') == 'INFO'
    
    def test_get_existing_key(self, temp_config_file):
        """Test getting existing configuration key."""
        config_manager = ConfigManager(temp_config_file)
        assert config_manager.get('ssh.timeout') == 30
        assert config_manager.get('logging.level') == 'INFO'
    
    def test_get_nonexistent_key(self, temp_config_file):
        """Test getting non-existent configuration key."""
        config_manager = ConfigManager(temp_config_file)
        assert config_manager.get('nonexistent.key') is None
        assert config_manager.get('nonexistent.key', 'default') == 'default'
    
    def test_get_with_env_override(self, temp_config_file):
        """Test environment variable override."""
        config_manager = ConfigManager(temp_config_file)
        
        # Set environment variable
        os.environ['HEALTH_CHECK_SSH_TIMEOUT'] = '60'
        
        try:
            assert config_manager.get('ssh.timeout') == 60
        finally:
            os.environ.pop('HEALTH_CHECK_SSH_TIMEOUT', None)
    
    def test_env_type_conversion(self, temp_config_file):
        """Test environment variable type conversion."""
        config_manager = ConfigManager(temp_config_file)
        
        # Test boolean conversion
        os.environ['HEALTH_CHECK_LOGGING_CONSOLE'] = 'false'
        try:
            assert config_manager.get('logging.console') is False
        finally:
            os.environ.pop('HEALTH_CHECK_LOGGING_CONSOLE', None)
        
        # Test integer conversion
        os.environ['HEALTH_CHECK_SSH_PORT'] = '2222'
        try:
            assert config_manager.get('ssh.port') == 2222
        finally:
            os.environ.pop('HEALTH_CHECK_SSH_PORT', None)
        
        # Test float conversion
        os.environ['HEALTH_CHECK_SSH_RETRY_DELAY'] = '2.5'
        try:
            assert config_manager.get('ssh.retry_delay') == 2.5
        finally:
            os.environ.pop('HEALTH_CHECK_SSH_RETRY_DELAY', None)
    
    def test_get_ssh_config(self, temp_config_file):
        """Test getting SSH configuration."""
        config_manager = ConfigManager(temp_config_file)
        ssh_config = config_manager.get_ssh_config()
        
        assert isinstance(ssh_config, dict)
        assert ssh_config['timeout'] == 30
        assert ssh_config['port'] == 22
    
    def test_get_logging_config(self, temp_config_file):
        """Test getting logging configuration."""
        config_manager = ConfigManager(temp_config_file)
        logging_config = config_manager.get_logging_config()
        
        assert isinstance(logging_config, dict)
        assert logging_config['level'] == 'INFO'
        assert logging_config['console'] is False
    
    def test_get_checks_config(self, temp_config_file):
        """Test getting checks configuration."""
        config_manager = ConfigManager(temp_config_file)
        
        linux_config = config_manager.get_checks_config('linux')
        assert isinstance(linux_config, dict)
        assert 'commands' in linux_config
        assert 'disk_usage' in linux_config['commands']
        
        aix_config = config_manager.get_checks_config('aix')
        assert isinstance(aix_config, dict)
        assert 'commands' in aix_config
        assert 'disk_usage' in aix_config['commands']
    
    def test_get_report_config(self, temp_config_file):
        """Test getting report configuration."""
        config_manager = ConfigManager(temp_config_file)
        report_config = config_manager.get_report_config()
        
        assert isinstance(report_config, dict)
        assert report_config['output_dir'] == './test_reports'
        assert 'json' in report_config['formats']
    
    def test_validate_host_config_valid(self, temp_config_file):
        """Test validation of valid host configuration."""
        config_manager = ConfigManager(temp_config_file)
        
        valid_config = {
            'host': '192.168.1.100',
            'username': 'testuser',
            'port': 22
        }
        
        # Should not raise exception
        config_manager.validate_host_config(valid_config)
    
    def test_validate_host_config_missing_field(self, temp_config_file):
        """Test validation fails with missing required field."""
        config_manager = ConfigManager(temp_config_file)
        
        invalid_config = {
            'host': '192.168.1.100'
            # Missing username
        }
        
        with pytest.raises(ConfigurationError, match="Missing required field: username"):
            config_manager.validate_host_config(invalid_config)
    
    def test_validate_host_config_invalid_host(self, temp_config_file):
        """Test validation fails with invalid host."""
        config_manager = ConfigManager(temp_config_file)
        
        invalid_config = {
            'host': 'invalid..host',
            'username': 'testuser'
        }
        
        with pytest.raises(ConfigurationError, match="Invalid host"):
            config_manager.validate_host_config(invalid_config)
    
    def test_validate_host_config_invalid_port(self, temp_config_file):
        """Test validation fails with invalid port."""
        config_manager = ConfigManager(temp_config_file)
        
        invalid_config = {
            'host': '192.168.1.100',
            'username': 'testuser',
            'port': 70000  # Invalid port number
        }
        
        with pytest.raises(ConfigurationError, match="Invalid port"):
            config_manager.validate_host_config(invalid_config)
    
    def test_validate_host_config_valid_hostname(self, temp_config_file):
        """Test validation with valid hostname."""
        config_manager = ConfigManager(temp_config_file)
        
        valid_config = {
            'host': 'test-server.example.com',
            'username': 'testuser'
        }
        
        # Should not raise exception
        config_manager.validate_host_config(valid_config)
    
    def test_validate_host_config_valid_ipv6(self, temp_config_file):
        """Test validation with valid IPv6 address."""
        config_manager = ConfigManager(temp_config_file)
        
        valid_config = {
            'host': '2001:db8::1',
            'username': 'testuser'
        }
        
        # Should not raise exception
        config_manager.validate_host_config(valid_config)
    
    def test_reload(self, temp_config_file):
        """Test configuration reload."""
        config_manager = ConfigManager(temp_config_file)
        
        # Initial value
        assert config_manager.get('ssh.timeout') == 30
        
        # Modify config file
        config_data = {
            'ssh': {
                'timeout': 60,
                'port': 22
            }
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Reload and check new value
        config_manager.reload()
        assert config_manager.get('ssh.timeout') == 60
    
    def test_invalid_yaml_config(self):
        """Test handling of invalid YAML configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            invalid_file = f.name
        
        try:
            with pytest.raises(ConfigurationError, match="Invalid YAML"):
                ConfigManager(invalid_file)
        finally:
            os.unlink(invalid_file)