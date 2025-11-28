"""
Tests for AIXChecker class.
"""

import pytest
from unittest.mock import Mock, patch
from health_check.checker.aix_checker import AIXChecker
from health_check.connection.ssh_connector import SSHConnector
from health_check.checker.base_checker import CheckResult


class TestAIXChecker:
    """Test cases for AIXChecker."""
    
    def test_init(self, mock_ssh_connector, mock_checks_config):
        """Test AIXChecker initialization."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        assert checker.get_os_type() == 'aix'
        assert checker.ssh_connector == mock_ssh_connector
        assert checker.config == mock_checks_config
    
    def test_get_default_commands(self, mock_ssh_connector):
        """Test getting default commands for AIX."""
        checker = AIXChecker(mock_ssh_connector, {})
        commands = checker.get_default_commands()
        
        assert isinstance(commands, dict)
        assert 'disk_usage' in commands
        assert 'memory' in commands
        assert 'cpu_load' in commands
        assert 'services' in commands
        assert 'network' in commands
        assert 'processes' in commands
    
    def test_parse_disk_usage_success(self, mock_ssh_connector, mock_checks_config, sample_aix_outputs):
        """Test successful AIX disk usage parsing."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_aix_outputs['disk_usage']
        result = checker.parse_result('disk_usage', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'disk_usage'
        assert result.status == 'FAIL'  # One filesystem at 80%
        assert 'filesystem(s)' in result.message
        assert 'filesystems' in result.details
        assert len(result.details['filesystems']) == 2
    
    def test_parse_memory_success(self, mock_ssh_connector, mock_checks_config, sample_aix_outputs):
        """Test successful AIX memory parsing."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_aix_outputs['memory']
        result = checker.parse_result('memory', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'memory'
        assert result.status == 'PASS'
        assert 'Memory usage:' in result.message
        assert 'total_pages' in result.details or 'total' in result.details
    
    def test_parse_cpu_load_success(self, mock_ssh_connector, mock_checks_config, sample_aix_outputs):
        """Test successful AIX CPU load parsing."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_aix_outputs['cpu_load']
        result = checker.parse_result('cpu_load', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'cpu_load'
        assert result.status == 'PASS'
        assert 'CPU load:' in result.message
        assert 'load_1min' in result.details
        assert 'cpu_count' in result.details
    
    def test_parse_services_success(self, mock_ssh_connector, mock_checks_config, sample_aix_outputs):
        """Test successful AIX services parsing."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_aix_outputs['services']
        result = checker.parse_result('services', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'services'
        assert result.status == 'PASS'
        assert 'service(s)' in result.message
        assert 'inactive_count' in result.details
        assert result.details['inactive_count'] == 0
    
    def test_parse_services_with_inactive(self, mock_ssh_connector, mock_checks_config):
        """Test AIX services parsing with inactive services."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = """Subsystem         Group            PID          Status
sendmail          mail             1234         active
sshd              tcpip           5678         active
failed_service    system             -         inoperative"""
        
        result = checker.parse_result('services', stdout, '', 0)
        
        assert result.status == 'FAIL'
        assert '1 inactive' in result.message
        assert len(result.details['services']) == 3
    
    def test_parse_network_success(self, mock_ssh_connector, mock_checks_config, sample_aix_outputs):
        """Test successful AIX network parsing."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_aix_outputs['network']
        result = checker.parse_result('network', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'network'
        assert result.status == 'PASS'
        assert 'interface(s)' in result.message
        assert 'up' in result.message
        assert 'interfaces' in result.details
        assert len(result.details['interfaces']) == 2
    
    def test_parse_processes_success(self, mock_ssh_connector, mock_checks_config, sample_aix_outputs):
        """Test successful AIX processes parsing."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_aix_outputs['processes']
        result = checker.parse_result('processes', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'processes'
        assert result.status == 'PASS'
        assert 'Showing top' in result.message
        assert 'processes' in result.details
        assert len(result.details['processes']) == 3
    
    def test_parse_unknown_check(self, mock_ssh_connector, mock_checks_config):
        """Test parsing unknown check type for AIX."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = "some output"
        result = checker.parse_result('unknown_check', stdout, '', 0)
        
        assert result.status == 'PASS'
        assert result.message == "Command executed with exit code 0"
        assert result.details['exit_code'] == 0
    
    def test_execute_check_success(self, mock_ssh_connector, mock_checks_config):
        """Test successful AIX check execution."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        mock_ssh_connector.test_connection.return_value = True
        
        result = checker.execute_check('disk_usage', 'df -g')
        
        assert isinstance(result, CheckResult)
        assert result.name == 'disk_usage'
        mock_ssh_connector.execute_command.assert_called_once_with('df -g')
    
    def test_run_all_checks_success(self, mock_ssh_connector, mock_checks_config):
        """Test running all AIX checks successfully."""
        checker = AIXChecker(mock_ssh_connector, mock_checks_config)
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        mock_ssh_connector.test_connection.return_value = True
        
        results = checker.run_all_checks()
        
        assert len(results) == len(mock_checks_config['commands'])
        for result in results:
            assert isinstance(result, CheckResult)


@pytest.fixture
def mock_ssh_connector():
    """Create a mock SSH connector."""
    connector = Mock(spec=SSHConnector)
    connector.host = 'test-host'
    return connector