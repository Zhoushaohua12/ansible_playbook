"""
Tests for LinuxChecker class.
"""

import pytest
from unittest.mock import Mock, patch
from health_check.checker.linux_checker import LinuxChecker
from health_check.connection.ssh_connector import SSHConnector
from health_check.checker.base_checker import CheckResult


class TestLinuxChecker:
    """Test cases for LinuxChecker."""
    
    def test_init(self, mock_ssh_connector, mock_checks_config):
        """Test LinuxChecker initialization."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        assert checker.get_os_type() == 'linux'
        assert checker.ssh_connector == mock_ssh_connector
        assert checker.config == mock_checks_config
    
    def test_get_default_commands(self, mock_ssh_connector):
        """Test getting default commands for Linux."""
        checker = LinuxChecker(mock_ssh_connector, {})
        commands = checker.get_default_commands()
        
        assert isinstance(commands, dict)
        assert 'disk_usage' in commands
        assert 'memory' in commands
        assert 'cpu_load' in commands
        assert 'services' in commands
        assert 'network' in commands
        assert 'processes' in commands
    
    def test_validate_prerequisites_success(self, mock_ssh_connector, mock_checks_config):
        """Test successful prerequisites validation."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        # Mock successful connection test
        mock_ssh_connector.test_connection.return_value = True
        
        # Should not raise exception
        checker.validate_prerequisites()
    
    def test_validate_prerequisites_no_connection(self, mock_ssh_connector, mock_checks_config):
        """Test prerequisites validation with no connection."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        # Mock failed connection test
        mock_ssh_connector.test_connection.return_value = False
        
        with pytest.raises(Exception, match="SSH connection is not active"):
            checker.validate_prerequisites()
    
    def test_parse_disk_usage_success(self, mock_ssh_connector, mock_checks_config, sample_linux_outputs):
        """Test successful disk usage parsing."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_linux_outputs['disk_usage']
        result = checker.parse_result('disk_usage', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'disk_usage'
        assert result.status == 'FAIL'  # One filesystem at 95%
        assert '95% filesystem(s)' in result.message
        assert 'filesystems' in result.details
        assert len(result.details['filesystems']) == 3
    
    def test_parse_disk_usage_no_issues(self, mock_ssh_connector, mock_checks_config):
        """Test disk usage parsing with no issues."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        20G   5G   15G  25% /
/dev/sda2       100G  50G   50G  50% /data"""
        
        result = checker.parse_result('disk_usage', stdout, '', 0)
        
        assert result.status == 'PASS'
        assert '0 filesystem(s)' in result.message or 'Disk usage check completed' in result.message
    
    def test_parse_memory_success(self, mock_ssh_connector, mock_checks_config, sample_linux_outputs):
        """Test successful memory parsing."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_linux_outputs['memory']
        result = checker.parse_result('memory', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'memory'
        assert result.status == 'PASS'
        assert 'Memory usage:' in result.message
        assert 'total' in result.details
        assert 'used' in result.details
        assert 'usage_percent' in result.details
    
    def test_parse_memory_high_usage(self, mock_ssh_connector, mock_checks_config):
        """Test memory parsing with high usage."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = """              total        used        free      shared  buff/cache   available
Mem:           3952        3560         95          0         300         392
Swap:          2047           0        2047"""
        
        result = checker.parse_result('memory', stdout, '', 0)
        
        assert result.status == 'WARN'
        assert result.details['usage_percent'] == 90
    
    def test_parse_cpu_load_success(self, mock_ssh_connector, mock_checks_config, sample_linux_outputs):
        """Test successful CPU load parsing."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_linux_outputs['cpu_load']
        result = checker.parse_result('cpu_load', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'cpu_load'
        assert result.status == 'PASS'
        assert 'CPU load:' in result.message
        assert 'load_1min' in result.details
        assert 'cpu_count' in result.details
    
    def test_parse_cpu_load_with_mock_nproc(self, mock_ssh_connector, mock_checks_config, sample_linux_outputs):
        """Test CPU load parsing with mocked nproc command."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_linux_outputs['cpu_load']
        
        # Mock nproc command
        mock_ssh_connector.execute_command.return_value = ('4\n', '', 0)
        
        result = checker.parse_result('cpu_load', stdout, '', 0)
        
        assert result.details['cpu_count'] == 4
        assert result.details['load_per_cpu'] == 0.15 / 4
    
    def test_parse_services_success(self, mock_ssh_connector, mock_checks_config, sample_linux_outputs):
        """Test successful services parsing."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_linux_outputs['services']
        result = checker.parse_result('services', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'services'
        assert result.status == 'PASS'
        assert '0 failed service(s)' in result.message or 'Found 0' in result.message
        assert 'failed_services' in result.details
    
    def test_parse_services_with_failures(self, mock_ssh_connector, mock_checks_config):
        """Test services parsing with failed services."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = """UNIT LOAD ACTIVE SUB DESCRIPTION
nginx.service loaded failed failed The nginx HTTP and reverse proxy server
mysql.service loaded failed failed MySQL Community Server"""
        
        result = checker.parse_result('services', stdout, '', 0)
        
        assert result.status == 'FAIL'
        assert '2 failed service(s)' in result.message
        assert len(result.details['failed_services']) == 2
    
    def test_parse_network_success(self, mock_ssh_connector, mock_checks_config, sample_linux_outputs):
        """Test successful network parsing."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_linux_outputs['network']
        result = checker.parse_result('network', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'network'
        assert result.status == 'PASS'
        assert '2 interface(s)' in result.message
        assert '2 up' in result.message
        assert 'interfaces' in result.details
        assert len(result.details['interfaces']) == 2
    
    def test_parse_network_no_up_interfaces(self, mock_ssh_connector, mock_checks_config):
        """Test network parsing with no up interfaces."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = """1: eth0: <BROADCAST,MULTICAST> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 00:11:22:33:44:55 brd ff:ff:ff:ff:ff:ff"""
        
        result = checker.parse_result('network', stdout, '', 0)
        
        assert result.status == 'FAIL'
        assert '0 up' in result.message
    
    def test_parse_processes_success(self, mock_ssh_connector, mock_checks_config, sample_linux_outputs):
        """Test successful processes parsing."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = sample_linux_outputs['processes']
        result = checker.parse_result('processes', stdout, '', 0)
        
        assert isinstance(result, CheckResult)
        assert result.name == 'processes'
        assert result.status == 'PASS'
        assert 'Showing top' in result.message
        assert 'processes' in result.details
        assert len(result.details['processes']) == 3
    
    def test_parse_unknown_check(self, mock_ssh_connector, mock_checks_config):
        """Test parsing unknown check type."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = "some output"
        result = checker.parse_result('unknown_check', stdout, '', 0)
        
        assert result.status == 'PASS'
        assert result.message == "Command executed with exit code 0"
        assert result.details['exit_code'] == 0
    
    def test_parse_command_failure(self, mock_ssh_connector, mock_checks_config):
        """Test parsing command with non-zero exit code."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        stdout = ""
        stderr = "command failed"
        result = checker.parse_result('disk_usage', stdout, stderr, 1)
        
        assert result.status == 'FAIL'
        assert 'Failed to get disk usage' in result.message
    
    def test_execute_check_success(self, mock_ssh_connector, mock_checks_config):
        """Test successful check execution."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        mock_ssh_connector.test_connection.return_value = True
        
        result = checker.execute_check('disk_usage', 'df -h')
        
        assert isinstance(result, CheckResult)
        assert result.name == 'disk_usage'
        mock_ssh_connector.execute_command.assert_called_once_with('df -h')
    
    def test_execute_check_failure(self, mock_ssh_connector, mock_checks_config):
        """Test check execution with failure."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        # Mock SSH connector to raise exception
        mock_ssh_connector.execute_command.side_effect = Exception("Connection error")
        mock_ssh_connector.test_connection.return_value = True
        
        result = checker.execute_check('disk_usage', 'df -h')
        
        assert result.status == 'FAIL'
        assert 'Error executing check' in result.message
    
    def test_run_all_checks_success(self, mock_ssh_connector, mock_checks_config):
        """Test running all checks successfully."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        mock_ssh_connector.test_connection.return_value = True
        
        results = checker.run_all_checks()
        
        assert len(results) == len(mock_checks_config['commands'])
        for result in results:
            assert isinstance(result, CheckResult)
    
    def test_run_all_checks_prerequisites_failure(self, mock_ssh_connector, mock_checks_config):
        """Test running all checks with prerequisites failure."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        # Mock failed connection test
        mock_ssh_connector.test_connection.return_value = False
        
        results = checker.run_all_checks()
        
        assert len(results) == 1
        assert results[0].name == 'prerequisites'
        assert results[0].status == 'FAIL'
    
    def test_get_summary(self, mock_ssh_connector, mock_checks_config):
        """Test getting summary of check results."""
        checker = LinuxChecker(mock_ssh_connector, mock_checks_config)
        
        # Add some mock results
        from health_check.checker.base_checker import CheckResult
        from datetime import datetime
        
        checker.results = [
            CheckResult('test1', 'PASS', 'OK'),
            CheckResult('test2', 'FAIL', 'Error'),
            CheckResult('test3', 'WARN', 'Warning'),
        ]
        
        summary = checker.get_summary()
        
        assert summary['total'] == 3
        assert summary['passed'] == 1
        assert summary['failed'] == 1
        assert summary['warning'] == 1
        assert summary['skipped'] == 0
        assert summary['overall_status'] == 'FAIL'  # Because there's a failure


@pytest.fixture
def mock_ssh_connector():
    """Create a mock SSH connector."""
    connector = Mock(spec=SSHConnector)
    connector.host = 'test-host'
    return connector