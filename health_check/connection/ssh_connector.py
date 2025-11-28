"""
SSH Connector for health check system.

Provides unified SSH connection interface with connection reuse,
automatic reconnection, and comprehensive error handling.
"""

import time
import socket
from typing import Optional, Dict, Any, Tuple
from contextlib import contextmanager
import paramiko
from ..exceptions import ConnectionError, AuthenticationError, TimeoutError
from ..logger.logger_config import get_logger


class SSHConnector:
    """Manages SSH connections to remote hosts."""
    
    def __init__(self, host_config: Dict[str, Any], ssh_config: Optional[Dict[str, Any]] = None):
        """
        Initialize SSH connector.
        
        Args:
            host_config: Host configuration containing host, username, password/key, etc.
            ssh_config: SSH configuration (timeout, retries, etc.)
        """
        self.host_config = host_config
        self.ssh_config = ssh_config or {}
        self.logger = get_logger(__name__)
        
        self.host = host_config['host']
        self.username = host_config['username']
        self.port = host_config.get('port', 22)
        self.password = host_config.get('password')
        self.key_file = host_config.get('key_file') or self.ssh_config.get('key_file')
        
        self.timeout = self.ssh_config.get('timeout', 30)
        self.max_retries = self.ssh_config.get('max_retries', 3)
        self.retry_delay = self.ssh_config.get('retry_delay', 5)
        
        self._client: Optional[paramiko.SSHClient] = None
        self._connected = False
    
    def connect(self) -> None:
        """Establish SSH connection with retry logic."""
        if self._connected and self._client:
            return
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(f"Connecting to {self.host}:{self.port} (attempt {attempt + 1})")
                
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Prepare connection parameters
                connect_kwargs = {
                    'hostname': self.host,
                    'port': self.port,
                    'username': self.username,
                    'timeout': self.timeout,
                    'allow_agent': False,
                    'look_for_keys': False
                }
                
                # Use key file if available, otherwise password
                if self.key_file:
                    connect_kwargs['key_filename'] = self.key_file
                    self.logger.debug(f"Using key file: {self.key_file}")
                elif self.password:
                    connect_kwargs['password'] = self.password
                    self.logger.debug("Using password authentication")
                else:
                    raise AuthenticationError("No authentication method provided (password or key file)")
                
                client.connect(**connect_kwargs)
                
                self._client = client
                self._connected = True
                self.logger.info(f"Successfully connected to {self.host}")
                return
                
            except paramiko.AuthenticationException as e:
                self.logger.error(f"Authentication failed for {self.host}: {e}")
                raise AuthenticationError(f"Authentication failed for {self.host}: {e}")
            
            except paramiko.SSHException as e:
                last_exception = e
                self.logger.warning(f"SSH connection failed for {self.host}: {e}")
                
            except socket.timeout as e:
                last_exception = e
                self.logger.warning(f"Connection timeout for {self.host}: {e}")
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Unexpected error connecting to {self.host}: {e}")
            
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                self.logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        raise ConnectionError(f"Failed to connect to {self.host} after {self.max_retries + 1} attempts: {last_exception}")
    
    def disconnect(self) -> None:
        """Close SSH connection."""
        if self._client:
            try:
                self._client.close()
                self.logger.info(f"Disconnected from {self.host}")
            except Exception as e:
                self.logger.warning(f"Error disconnecting from {self.host}: {e}")
            finally:
                self._client = None
                self._connected = False
    
    def execute_command(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        """
        Execute command on remote host.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds (overrides SSH timeout if provided)
            
        Returns:
            Tuple of (stdout, stderr, exit_code)
        """
        if not self._connected or not self._client:
            raise ConnectionError(f"Not connected to {self.host}")
        
        cmd_timeout = timeout or self.timeout
        
        try:
            self.logger.debug(f"Executing command on {self.host}: {command}")
            
            stdin, stdout, stderr = self._client.exec_command(command, timeout=cmd_timeout)
            
            # Read output
            stdout_str = stdout.read().decode('utf-8', errors='replace')
            stderr_str = stderr.read().decode('utf-8', errors='replace')
            exit_code = stdout.channel.recv_exit_status()
            
            self.logger.debug(f"Command completed on {self.host} with exit code: {exit_code}")
            
            if exit_code != 0:
                self.logger.warning(f"Command failed on {self.host}: {command}")
                self.logger.debug(f"stderr: {stderr_str}")
            
            return stdout_str, stderr_str, exit_code
            
        except socket.timeout as e:
            raise TimeoutError(f"Command timeout on {self.host}: {command}")
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH error executing command on {self.host}: {e}")
        except Exception as e:
            raise ConnectionError(f"Unexpected error executing command on {self.host}: {e}")
    
    def test_connection(self) -> bool:
        """
        Test if connection is alive.
        
        Returns:
            True if connection is alive, False otherwise
        """
        if not self._connected or not self._client:
            return False
        
        try:
            # Execute a simple command to test connection
            self.execute_command("echo 'connection_test'", timeout=5)
            return True
        except Exception:
            return False
    
    def ensure_connected(self) -> None:
        """Ensure connection is established, reconnect if necessary."""
        if not self.test_connection():
            self.logger.info(f"Connection to {self.host} lost, attempting to reconnect...")
            self.disconnect()
            self.connect()
    
    @contextmanager
    def connection(self):
        """Context manager for SSH connection."""
        try:
            self.connect()
            yield self
        finally:
            self.disconnect()
    
    def __enter__(self):
        """Enter context manager."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.disconnect()
    
    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.disconnect()