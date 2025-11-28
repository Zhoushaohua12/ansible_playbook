"""
Tests for SSHConnector class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import paramiko
import socket
from health_check.connection.ssh_connector import SSHConnector
from health_check.exceptions import ConnectionError, AuthenticationError, TimeoutError


class TestSSHConnector:
    """Test cases for SSHConnector."""
    
    def test_init_basic(self, mock_host_config, mock_ssh_config):
        """Test basic initialization."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        assert connector.host == '192.168.1.100'
        assert connector.username == 'testuser'
        assert connector.port == 22
        assert connector.password == 'testpass'
        assert connector.timeout == 30
        assert connector.max_retries == 3
        assert connector.retry_delay == 5
    
    def test_init_with_key_file(self, mock_ssh_config):
        """Test initialization with key file."""
        host_config = {
            'host': '192.168.1.100',
            'username': 'testuser',
            'key_file': '/path/to/key',
            'os_type': 'linux'
        }
        
        connector = SSHConnector(host_config, mock_ssh_config)
        assert connector.key_file == '/path/to/key'
        assert connector.password is None
    
    def test_connect_success(self, mock_host_config, mock_ssh_config):
        """Test successful SSH connection."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            connector.connect()
            
            assert connector._connected is True
            assert connector._client == mock_client
            mock_client.connect.assert_called_once()
    
    def test_connect_auth_failure(self, mock_host_config, mock_ssh_config):
        """Test SSH connection authentication failure."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_client.connect.side_effect = paramiko.AuthenticationException("Auth failed")
            mock_client_class.return_value = mock_client
            
            with pytest.raises(AuthenticationError, match="Authentication failed"):
                connector.connect()
    
    def test_connect_with_retry(self, mock_host_config, mock_ssh_config):
        """Test SSH connection with retry logic."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            # Fail first two attempts, succeed on third
            mock_client.connect.side_effect = [
                paramiko.SSHException("Connection failed"),
                paramiko.SSHException("Connection failed"),
                None
            ]
            mock_client_class.return_value = mock_client
            
            with patch('time.sleep'):  # Mock sleep to speed up test
                connector.connect()
            
            assert connector._connected is True
            assert mock_client.connect.call_count == 3
    
    def test_connect_max_retries_exceeded(self, mock_host_config, mock_ssh_config):
        """Test SSH connection with max retries exceeded."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_client.connect.side_effect = paramiko.SSHException("Connection failed")
            mock_client_class.return_value = mock_client
            
            with patch('time.sleep'):  # Mock sleep to speed up test
                with pytest.raises(ConnectionError, match="Failed to connect"):
                    connector.connect()
    
    def test_disconnect(self, mock_host_config, mock_ssh_config):
        """Test SSH disconnection."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            connector.connect()
            connector.disconnect()
            
            assert connector._connected is False
            assert connector._client is None
            mock_client.close.assert_called_once()
    
    def test_execute_command_success(self, mock_host_config, mock_ssh_config):
        """Test successful command execution."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_stdin = Mock()
            mock_stdout = Mock()
            mock_stderr = Mock()
            
            mock_stdout.read.return_value = b"command output"
            mock_stderr.read.return_value = b""
            mock_stdout.channel.recv_exit_status.return_value = 0
            
            mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
            mock_client_class.return_value = mock_client
            
            connector.connect()
            
            stdout, stderr, exit_code = connector.execute_command("test command")
            
            assert stdout == "command output"
            assert stderr == ""
            assert exit_code == 0
            mock_client.exec_command.assert_called_once_with("test command", timeout=30)
    
    def test_execute_command_failure(self, mock_host_config, mock_ssh_config):
        """Test command execution with non-zero exit code."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_stdin = Mock()
            mock_stdout = Mock()
            mock_stderr = Mock()
            
            mock_stdout.read.return_value = b""
            mock_stderr.read.return_value = b"command error"
            mock_stdout.channel.recv_exit_status.return_value = 1
            
            mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
            mock_client_class.return_value = mock_client
            
            connector.connect()
            
            stdout, stderr, exit_code = connector.execute_command("test command")
            
            assert stdout == ""
            assert stderr == "command error"
            assert exit_code == 1
    
    def test_execute_command_timeout(self, mock_host_config, mock_ssh_config):
        """Test command execution timeout."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_client.exec_command.side_effect = socket.timeout("Command timeout")
            mock_client_class.return_value = mock_client
            
            connector.connect()
            
            with pytest.raises(TimeoutError, match="Command timeout"):
                connector.execute_command("test command")
    
    def test_execute_command_not_connected(self, mock_host_config, mock_ssh_config):
        """Test command execution when not connected."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with pytest.raises(ConnectionError, match="Not connected"):
            connector.execute_command("test command")
    
    def test_test_connection_alive(self, mock_host_config, mock_ssh_config):
        """Test connection test when connection is alive."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_stdin = Mock()
            mock_stdout = Mock()
            mock_stderr = Mock()
            
            mock_stdout.read.return_value = b"connection_test"
            mock_stderr.read.return_value = b""
            mock_stdout.channel.recv_exit_status.return_value = 0
            
            mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
            mock_client_class.return_value = mock_client
            
            connector.connect()
            
            assert connector.test_connection() is True
    
    def test_test_connection_dead(self, mock_host_config, mock_ssh_config):
        """Test connection test when connection is dead."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_client.exec_command.side_effect = paramiko.SSHException("Connection lost")
            mock_client_class.return_value = mock_client
            
            connector.connect()
            
            assert connector.test_connection() is False
    
    def test_ensure_connected_reconnect(self, mock_host_config, mock_ssh_config):
        """Test ensure_connected triggers reconnection."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            # First test_connection call fails, second succeeds
            mock_client.exec_command.side_effect = [
                paramiko.SSHException("Connection lost"),
                (Mock(), Mock(), Mock())  # exec_command return values
            ]
            mock_client_class.return_value = mock_client
            
            connector.connect()
            
            # Should trigger reconnection
            connector.ensure_connected()
    
    def test_context_manager(self, mock_host_config, mock_ssh_config):
        """Test context manager functionality."""
        connector = SSHConnector(mock_host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            with connector as conn:
                assert conn == connector
                assert connector._connected is True
            
            # Connection should be closed after context
            assert connector._connected is False
            mock_client.close.assert_called()
    
    def test_no_auth_method(self, mock_ssh_config):
        """Test error when no authentication method is provided."""
        host_config = {
            'host': '192.168.1.100',
            'username': 'testuser',
            # No password or key_file
            'os_type': 'linux'
        }
        
        connector = SSHConnector(host_config, mock_ssh_config)
        
        with patch('paramiko.SSHClient'):
            with pytest.raises(AuthenticationError, match="No authentication method"):
                connector.connect()