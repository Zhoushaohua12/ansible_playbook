"""
Base checker abstract class for health check system.

Defines the common interface and shared functionality for all system checkers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from ..connection.ssh_connector import SSHConnector
from ..logger.logger_config import get_logger
from ..exceptions import ValidationError, CommandExecutionError


class CheckResult:
    """Represents the result of a health check."""
    
    def __init__(self, name: str, status: str, message: str, 
                 details: Optional[Dict[str, Any]] = None,
                 raw_output: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        """
        Initialize check result.
        
        Args:
            name: Check name
            status: Check status (PASS, FAIL, WARN, SKIP)
            message: Check result message
            details: Additional details about the check
            raw_output: Raw command output
            timestamp: Check timestamp
        """
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.raw_output = raw_output
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert check result to dictionary."""
        return {
            'name': self.name,
            'status': self.status,
            'message': self.message,
            'details': self.details,
            'raw_output': self.raw_output,
            'timestamp': self.timestamp.isoformat()
        }


class BaseChecker(ABC):
    """Abstract base class for system health checkers."""
    
    def __init__(self, ssh_connector: SSHConnector, config: Dict[str, Any]):
        """
        Initialize base checker.
        
        Args:
            ssh_connector: SSH connection instance
            config: Checker configuration
        """
        self.ssh_connector = ssh_connector
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self.results: List[CheckResult] = []
    
    @abstractmethod
    def get_os_type(self) -> str:
        """Return the OS type this checker supports."""
        pass
    
    @abstractmethod
    def get_default_commands(self) -> Dict[str, str]:
        """Return default commands for this OS type."""
        pass
    
    def validate_prerequisites(self) -> None:
        """
        Validate prerequisites for running checks.
        
        Raises:
            ValidationError: If prerequisites are not met
        """
        if not self.ssh_connector.test_connection():
            raise ValidationError("SSH connection is not active")
        
        # Check if required commands are available
        os_type = self.get_os_type()
        commands = self.config.get('commands', {})
        
        for check_name, command in commands.items():
            if not command:
                raise ValidationError(f"Empty command for check: {check_name}")
    
    def execute_check(self, check_name: str, command: str) -> CheckResult:
        """
        Execute a single health check.
        
        Args:
            check_name: Name of the check
            command: Command to execute
            
        Returns:
            CheckResult instance
        """
        try:
            self.logger.info(f"Executing check '{check_name}' on {self.ssh_connector.host}")
            
            stdout, stderr, exit_code = self.ssh_connector.execute_command(command)
            
            # Parse the result based on check type
            result = self.parse_result(check_name, stdout, stderr, exit_code)
            
            self.logger.info(f"Check '{check_name}' completed with status: {result.status}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing check '{check_name}': {e}")
            return CheckResult(
                name=check_name,
                status='FAIL',
                message=f"Error executing check: {str(e)}",
                details={'error': str(e), 'command': command}
            )
    
    @abstractmethod
    def parse_result(self, check_name: str, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """
        Parse the result of a command execution.
        
        Args:
            check_name: Name of the check
            stdout: Standard output
            stderr: Standard error
            exit_code: Exit code
            
        Returns:
            Parsed CheckResult
        """
        pass
    
    def run_all_checks(self) -> List[CheckResult]:
        """
        Run all configured health checks.
        
        Returns:
            List of CheckResult instances
        """
        self.results = []
        
        try:
            self.validate_prerequisites()
        except ValidationError as e:
            self.logger.error(f"Prerequisites validation failed: {e}")
            # Return a single failed result
            return [CheckResult(
                name='prerequisites',
                status='FAIL',
                message=f"Prerequisites validation failed: {str(e)}"
            )]
        
        commands = self.config.get('commands', {})
        if not commands:
            self.logger.warning("No commands configured for checks")
            return []
        
        for check_name, command in commands.items():
            result = self.execute_check(check_name, command)
            self.results.append(result)
        
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all check results.
        
        Returns:
            Summary dictionary
        """
        if not self.results:
            return {'total': 0, 'passed': 0, 'failed': 0, 'warning': 0, 'skipped': 0}
        
        summary = {
            'total': len(self.results),
            'passed': len([r for r in self.results if r.status == 'PASS']),
            'failed': len([r for r in self.results if r.status == 'FAIL']),
            'warning': len([r for r in self.results if r.status == 'WARN']),
            'skipped': len([r for r in self.results if r.status == 'SKIP'])
        }
        
        summary['overall_status'] = 'PASS' if summary['failed'] == 0 else 'FAIL'
        
        return summary