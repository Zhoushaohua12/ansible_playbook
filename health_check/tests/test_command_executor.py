"""
Tests for CommandExecutor class.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from health_check.command.command_executor import CommandExecutor
from health_check.connection.ssh_connector import SSHConnector
from health_check.exceptions import CommandExecutionError


class TestCommandExecutor:
    """Test cases for CommandExecutor."""
    
    def test_init(self, mock_ssh_connector):
        """Test CommandExecutor initialization."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=300)
        
        assert executor.ssh_connector == mock_ssh_connector
        assert executor.cache_ttl == 300
        assert executor._cache == {}
        assert executor._command_files == {}
    
    def test_load_commands_from_file(self, mock_ssh_connector):
        """Test loading commands from file."""
        executor = CommandExecutor(mock_ssh_connector)
        
        # Create a temporary command file
        command_content = """
# Test commands
DISK_USAGE="df -h"
MEMORY="free -m"
CPU_LOAD="uptime"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(command_content)
            temp_file = f.name
        
        try:
            executor.load_commands_from_file(temp_file, 'linux')
            
            assert 'DISK_USAGE' in executor._command_files
            assert executor._command_files['DISK_USAGE'] == 'df -h'
            assert 'MEMORY' in executor._command_files
            assert executor._command_files['MEMORY'] == 'free -m'
            assert 'CPU_LOAD' in executor._command_files
            assert executor._command_files['CPU_LOAD'] == 'uptime'
        
        finally:
            os.unlink(temp_file)
    
    def test_load_commands_from_nonexistent_file(self, mock_ssh_connector):
        """Test loading commands from non-existent file."""
        executor = CommandExecutor(mock_ssh_connector)
        
        with pytest.raises(CommandExecutionError, match="Command file not found"):
            executor.load_commands_from_file('nonexistent.sh', 'linux')
    
    def test_parse_command_file(self, mock_ssh_connector):
        """Test parsing command file content."""
        executor = CommandExecutor(mock_ssh_connector)
        
        content = """
# Comment line
DISK_USAGE="df -h"
MEMORY="free -m"
# Another comment
CPU_LOAD="uptime"
"""
        
        commands = executor._parse_command_file(content, 'linux')
        
        assert len(commands) == 3
        assert commands['DISK_USAGE'] == 'df -h'
        assert commands['MEMORY'] == 'free -m'
        assert commands['CPU_LOAD'] == 'uptime'
    
    def test_inject_parameters(self, mock_ssh_connector):
        """Test parameter injection into commands."""
        executor = CommandExecutor(mock_ssh_connector)
        
        command = "ls ${directory}"
        params = {'directory': '/tmp'}
        
        result = executor.inject_parameters(command, params)
        
        assert result == "ls /tmp"
    
    def test_inject_parameters_no_replacement(self, mock_ssh_connector):
        """Test parameter injection with no replacements."""
        executor = CommandExecutor(mock_ssh_connector)
        
        command = "ls /tmp"
        params = {'directory': '/var'}
        
        result = executor.inject_parameters(command, params)
        
        assert result == "ls /tmp"
    
    def test_get_cache_key(self, mock_ssh_connector):
        """Test cache key generation."""
        executor = CommandExecutor(mock_ssh_connector)
        
        command = "ls ${directory}"
        params = {'directory': '/tmp'}
        
        cache_key1 = executor._get_cache_key(command, params)
        cache_key2 = executor._get_cache_key(command, params)
        
        assert cache_key1 == cache_key2
        assert isinstance(cache_key1, str)
        assert len(cache_key1) == 32  # MD5 hash length
    
    def test_is_cache_valid(self, mock_ssh_connector):
        """Test cache validity checking."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=60)
        
        from datetime import datetime, timedelta
        
        # Valid entry
        valid_entry = {
            'timestamp': datetime.now() - timedelta(seconds=30)
        }
        assert executor._is_cache_valid(valid_entry) is True
        
        # Expired entry
        expired_entry = {
            'timestamp': datetime.now() - timedelta(seconds=120)
        }
        assert executor._is_cache_valid(expired_entry) is False
        
        # Entry without timestamp
        no_timestamp_entry = {}
        assert executor._is_cache_valid(no_timestamp_entry) is False
    
    def test_execute_command_success(self, mock_ssh_connector):
        """Test successful command execution."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=0)  # Disable cache
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        
        stdout, stderr, exit_code = executor.execute_command("test command")
        
        assert stdout == "output"
        assert stderr == ""
        assert exit_code == 0
        mock_ssh_connector.execute_command.assert_called_once_with("test command", timeout=None)
    
    def test_execute_command_with_cache(self, mock_ssh_connector):
        """Test command execution with caching."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=300)
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        
        # First call
        stdout1, stderr1, exit_code1 = executor.execute_command("test command")
        
        # Second call should use cache
        stdout2, stderr2, exit_code2 = executor.execute_command("test command")
        
        assert stdout1 == "output"
        assert stdout2 == "output"
        # SSH connector should only be called once due to caching
        mock_ssh_connector.execute_command.assert_called_once()
    
    def test_execute_command_with_params(self, mock_ssh_connector):
        """Test command execution with parameters."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=0)
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        
        command = "ls ${directory}"
        params = {'directory': '/tmp'}
        
        stdout, stderr, exit_code = executor.execute_command(command, params)
        
        assert stdout == "output"
        mock_ssh_connector.execute_command.assert_called_once_with("ls /tmp", timeout=None)
    
    def test_execute_command_named_command(self, mock_ssh_connector):
        """Test execution of named command from loaded file."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=0)
        
        # Load a named command
        executor._command_files['DISK_USAGE'] = 'df -h'
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        
        stdout, stderr, exit_code = executor.execute_command("DISK_USAGE")
        
        assert stdout == "output"
        mock_ssh_connector.execute_command.assert_called_once_with("df -h", timeout=None)
    
    def test_execute_command_failure(self, mock_ssh_connector):
        """Test command execution failure."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=0)
        
        # Mock SSH connector to raise exception
        mock_ssh_connector.execute_command.side_effect = Exception("Connection error")
        
        with pytest.raises(CommandExecutionError, match="Failed to execute command"):
            executor.execute_command("test command")
    
    def test_execute_commands_batch(self, mock_ssh_connector):
        """Test batch command execution."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=0)
        
        # Mock SSH connector
        mock_ssh_connector.execute_command.return_value = ("output", "", 0)
        
        commands = [
            {'name': 'cmd1', 'command': 'command1'},
            {'name': 'cmd2', 'command': 'command2', 'params': {'param': 'value'}},
            {'name': 'cmd3', 'command': 'command3', 'timeout': 60}
        ]
        
        results = executor.execute_commands_batch(commands)
        
        assert len(results) == 3
        for result in results:
            assert result['success'] is True
            assert result['stdout'] == "output"
        
        assert mock_ssh_connector.execute_command.call_count == 3
    
    def test_execute_commands_batch_with_failure(self, mock_ssh_connector):
        """Test batch command execution with failure."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=0)
        
        # Mock SSH connector - first command succeeds, second fails
        mock_ssh_connector.execute_command.side_effect = [
            ("output1", "", 0),
            Exception("Connection error")
        ]
        
        commands = [
            {'name': 'cmd1', 'command': 'command1'},
            {'name': 'cmd2', 'command': 'command2'}
        ]
        
        results = executor.execute_commands_batch(commands)
        
        assert len(results) == 2
        assert results[0]['success'] is True
        assert results[1]['success'] is False
        assert 'error' in results[1]
    
    def test_clear_cache(self, mock_ssh_connector):
        """Test cache clearing."""
        executor = CommandExecutor(mock_ssh_connector)
        
        # Add something to cache
        executor._cache['test'] = {'data': 'value'}
        
        executor.clear_cache()
        
        assert executor._cache == {}
    
    def test_get_cache_stats(self, mock_ssh_connector):
        """Test getting cache statistics."""
        executor = CommandExecutor(mock_ssh_connector, cache_ttl=300)
        
        from datetime import datetime, timedelta
        
        # Add some cache entries
        executor._cache['valid'] = {
            'timestamp': datetime.now() - timedelta(seconds=30),
            'result': {}
        }
        executor._cache['expired'] = {
            'timestamp': datetime.now() - timedelta(seconds=400),
            'result': {}
        }
        
        stats = executor.get_cache_stats()
        
        assert stats['total_entries'] == 2
        assert stats['valid_entries'] == 1
        assert stats['expired_entries'] == 1
        assert stats['cache_ttl'] == 300
    
    def test_validate_command_safe(self, mock_ssh_connector):
        """Test validation of safe commands."""
        executor = CommandExecutor(mock_ssh_connector)
        
        safe_commands = [
            "df -h",
            "free -m",
            "uptime",
            "ps aux",
            "ls -la /tmp"
        ]
        
        for command in safe_commands:
            assert executor.validate_command(command) is True
    
    def test_validate_command_dangerous(self, mock_ssh_connector):
        """Test validation of dangerous commands."""
        executor = CommandExecutor(mock_ssh_connector)
        
        dangerous_commands = [
            "rm -rf /",
            "mkfs /dev/sda1",
            "dd if=/dev/zero of=/dev/sda",
            "shutdown -h now",
            "reboot",
            "format /dev/sda1"
        ]
        
        for command in dangerous_commands:
            assert executor.validate_command(command) is False


@pytest.fixture
def mock_ssh_connector():
    """Create a mock SSH connector."""
    connector = Mock(spec=SSHConnector)
    return connector