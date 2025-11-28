"""
Command executor for health check system.

Manages command execution with support for external script loading,
parameter injection, result caching, and detailed logging.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from ..connection.ssh_connector import SSHConnector
from ..logger.logger_config import get_logger
from ..exceptions import CommandExecutionError


class CommandExecutor:
    """Manages command execution for health checks."""
    
    def __init__(self, ssh_connector: SSHConnector, cache_ttl: int = 300):
        """
        Initialize command executor.
        
        Args:
            ssh_connector: SSH connection instance
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.ssh_connector = ssh_connector
        self.cache_ttl = cache_ttl
        self.logger = get_logger(self.__class__.__name__)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._command_files: Dict[str, str] = {}
    
    def load_commands_from_file(self, file_path: str, os_type: str) -> None:
        """
        Load commands from external script file.
        
        Args:
            file_path: Path to command file
            os_type: OS type ('linux' or 'aix')
        """
        try:
            script_path = Path(file_path)
            if not script_path.exists():
                script_path = Path(__file__).parent / 'commands' / file_path
            
            if not script_path.exists():
                raise CommandExecutionError(f"Command file not found: {file_path}")
            
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse commands from script
            commands = self._parse_command_file(content, os_type)
            self._command_files.update(commands)
            
            self.logger.info(f"Loaded {len(commands)} commands from {file_path}")
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to load command file {file_path}: {e}")
    
    def _parse_command_file(self, content: str, os_type: str) -> Dict[str, str]:
        """
        Parse commands from script file content.
        
        Args:
            content: File content
            os_type: OS type
            
        Returns:
            Dictionary of command names to command strings
        """
        commands = {}
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Look for command definitions in format: NAME="command"
            if '=' in line and not line.startswith(' '):
                name, command = line.split('=', 1)
                name = name.strip()
                command = command.strip().strip('"\'')
                commands[name] = command
        
        return commands
    
    def inject_parameters(self, command: str, params: Dict[str, Any]) -> str:
        """
        Inject parameters into command template.
        
        Args:
            command: Command template with placeholders
            params: Parameters to inject
            
        Returns:
            Command with parameters injected
        """
        try:
            # Simple string replacement for parameters
            formatted_command = command
            for key, value in params.items():
                placeholder = f"${{{key}}}"
                if placeholder in formatted_command:
                    formatted_command = formatted_command.replace(placeholder, str(value))
            
            return formatted_command
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to inject parameters: {e}")
    
    def _get_cache_key(self, command: str, params: Dict[str, Any]) -> str:
        """Generate cache key for command."""
        content = f"{command}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        timestamp = cache_entry.get('timestamp')
        if not timestamp:
            return False
        
        age = datetime.now() - timestamp
        return age.total_seconds() < self.cache_ttl
    
    def execute_command(self, command: str, params: Optional[Dict[str, Any]] = None,
                       use_cache: bool = True, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        """
        Execute command with caching and parameter injection.
        
        Args:
            command: Command to execute
            params: Parameters to inject into command
            use_cache: Whether to use cached results
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (stdout, stderr, exit_code)
        """
        params = params or {}
        
        # Check if command is a named command from loaded files
        if command in self._command_files:
            command = self._command_files[command]
        
        # Inject parameters
        formatted_command = self.inject_parameters(command, params)
        
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(formatted_command, params)
            if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]):
                self.logger.debug(f"Using cached result for command: {formatted_command[:50]}...")
                cached_result = self._cache[cache_key]['result']
                return cached_result['stdout'], cached_result['stderr'], cached_result['exit_code']
        
        # Execute command
        try:
            self.logger.debug(f"Executing command: {formatted_command}")
            
            stdout, stderr, exit_code = self.ssh_connector.execute_command(
                formatted_command, timeout=timeout
            )
            
            # Cache result
            if use_cache:
                cache_entry = {
                    'timestamp': datetime.now(),
                    'result': {
                        'stdout': stdout,
                        'stderr': stderr,
                        'exit_code': exit_code
                    }
                }
                self._cache[cache_key] = cache_entry
            
            return stdout, stderr, exit_code
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise CommandExecutionError(f"Failed to execute command '{formatted_command}': {e}")
    
    def execute_commands_batch(self, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple commands in batch.
        
        Args:
            commands: List of command dictionaries with 'name', 'command', and optional 'params'
            
        Returns:
            List of results with name, stdout, stderr, exit_code
        """
        results = []
        
        for cmd_info in commands:
            name = cmd_info.get('name', 'unknown')
            command = cmd_info.get('command', '')
            params = cmd_info.get('params', {})
            timeout = cmd_info.get('timeout')
            
            try:
                stdout, stderr, exit_code = self.execute_command(
                    command, params, timeout=timeout
                )
                
                results.append({
                    'name': name,
                    'command': command,
                    'stdout': stdout,
                    'stderr': stderr,
                    'exit_code': exit_code,
                    'success': exit_code == 0
                })
                
            except Exception as e:
                results.append({
                    'name': name,
                    'command': command,
                    'stdout': '',
                    'stderr': str(e),
                    'exit_code': -1,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def clear_cache(self) -> None:
        """Clear command cache."""
        self._cache.clear()
        self.logger.info("Command cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        valid_entries = sum(1 for entry in self._cache.values() if self._is_cache_valid(entry))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'cache_ttl': self.cache_ttl
        }
    
    def validate_command(self, command: str) -> bool:
        """
        Validate command syntax and safety.
        
        Args:
            command: Command to validate
            
        Returns:
            True if command is safe, False otherwise
        """
        # Basic safety checks
        dangerous_patterns = [
            'rm -rf /',
            'mkfs',
            'dd if=',
            'format',
            'fdisk',
            'shutdown',
            'reboot',
            'halt',
            'poweroff'
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                self.logger.warning(f"Dangerous command detected: {command}")
                return False
        
        return True