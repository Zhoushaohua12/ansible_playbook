# API Reference

This document provides detailed API documentation for the Health Check System modules and classes.

## Table of Contents

- [Configuration Module](#configuration-module)
- [Connection Module](#connection-module)
- [Checker Module](#checker-module)
- [Command Module](#command-module)
- [Report Module](#report-module)
- [Logger Module](#logger-module)
- [Exceptions](#exceptions)
- [Main Application](#main-application)

## Configuration Module

### ConfigManager

Manages configuration loading, validation, and caching.

```python
class ConfigManager:
    def __init__(self, config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (str, optional): Path to configuration YAML file

**Methods:**

#### get(key, default=None)
Get configuration value with environment variable override support.

```python
def get(self, key: str, default: Any = None) -> Any
```

**Parameters:**
- `key` (str): Configuration key in dot notation (e.g., 'ssh.timeout')
- `default` (Any, optional): Default value if key not found

**Returns:** Configuration value

**Example:**
```python
config = ConfigManager()
timeout = config.get('ssh.timeout', 30)
```

#### get_ssh_config()
Get SSH configuration dictionary.

```python
def get_ssh_config(self) -> Dict[str, Any]
```

**Returns:** SSH configuration dictionary

#### get_logging_config()
Get logging configuration dictionary.

```python
def get_logging_config(self) -> Dict[str, Any]
```

**Returns:** Logging configuration dictionary

#### get_checks_config(os_type)
Get checks configuration for specific OS type.

```python
def get_checks_config(self, os_type: str) -> Dict[str, Any]
```

**Parameters:**
- `os_type` (str): 'linux' or 'aix'

**Returns:** Checks configuration dictionary

#### get_report_config()
Get report configuration dictionary.

```python
def get_report_config(self) -> Dict[str, Any]
```

**Returns:** Report configuration dictionary

#### validate_host_config(host_config)
Validate host configuration.

```python
def validate_host_config(self, host_config: Dict[str, Any]) -> None
```

**Parameters:**
- `host_config` (dict): Host configuration dictionary

**Raises:** `ConfigurationError` if validation fails

#### reload()
Reload configuration from file.

```python
def reload(self) -> None
```

## Connection Module

### SSHConnector

Manages SSH connections and command execution.

```python
class SSHConnector:
    def __init__(self, host_config: Dict[str, Any], ssh_config: Optional[Dict[str, Any]] = None)
```

**Parameters:**
- `host_config` (dict): Host configuration containing connection details
- `ssh_config` (dict, optional): SSH configuration (timeout, retries, etc.)

**Methods:**

#### connect()
Establish SSH connection with retry logic.

```python
def connect(self) -> None
```

**Raises:** `ConnectionError`, `AuthenticationError`

#### disconnect()
Close SSH connection.

```python
def disconnect(self) -> None
```

#### execute_command(command, timeout=None)
Execute command on remote host.

```python
def execute_command(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]
```

**Parameters:**
- `command` (str): Command to execute
- `timeout` (int, optional): Command timeout in seconds

**Returns:** Tuple of (stdout, stderr, exit_code)

**Raises:** `ConnectionError`, `TimeoutError`

#### test_connection()
Test if connection is alive.

```python
def test_connection(self) -> bool
```

**Returns:** True if connection is alive, False otherwise

#### ensure_connected()
Ensure connection is established, reconnect if necessary.

```python
def ensure_connected(self) -> None
```

**Context Manager Support:**
```python
with SSHConnector(host_config, ssh_config) as connector:
    stdout, stderr, exit_code = connector.execute_command('uptime')
```

## Checker Module

### BaseChecker

Abstract base class for system health checkers.

```python
class BaseChecker(ABC):
    def __init__(self, ssh_connector: SSHConnector, config: Dict[str, Any])
```

**Abstract Methods:**

#### get_os_type()
Return the OS type this checker supports.

```python
@abstractmethod
def get_os_type(self) -> str
```

#### get_default_commands()
Return default commands for this OS type.

```python
@abstractmethod
def get_default_commands(self) -> Dict[str, str]
```

#### parse_result(check_name, stdout, stderr, exit_code)
Parse the result of a command execution.

```python
@abstractmethod
def parse_result(self, check_name: str, stdout: str, stderr: str, exit_code: int) -> CheckResult
```

**Parameters:**
- `check_name` (str): Name of the check
- `stdout` (str): Standard output
- `stderr` (str): Standard error
- `exit_code` (int): Exit code

**Returns:** `CheckResult` instance

**Methods:**

#### validate_prerequisites()
Validate prerequisites for running checks.

```python
def validate_prerequisites(self) -> None
```

**Raises:** `ValidationError` if prerequisites are not met

#### execute_check(check_name, command)
Execute a single health check.

```python
def execute_check(self, check_name: str, command: str) -> CheckResult
```

**Parameters:**
- `check_name` (str): Name of the check
- `command` (str): Command to execute

**Returns:** `CheckResult` instance

#### run_all_checks()
Run all configured health checks.

```python
def run_all_checks(self) -> List[CheckResult]
```

**Returns:** List of `CheckResult` instances

#### get_summary()
Get summary of all check results.

```python
def get_summary(self) -> Dict[str, Any]
```

**Returns:** Summary dictionary

### LinuxChecker

Health checker for Linux systems.

```python
class LinuxChecker(BaseChecker):
    def __init__(self, ssh_connector: SSHConnector, config: Dict[str, Any])
```

**Inherits all methods from BaseChecker**

**Supported Checks:**
- `disk_usage`: Filesystem usage analysis
- `memory`: Memory usage monitoring
- `cpu_load`: System load averages
- `services`: Failed systemd services
- `network`: Network interface status
- `processes`: Top processes

### AIXChecker

Health checker for AIX systems.

```python
class AIXChecker(BaseChecker):
    def __init__(self, ssh_connector: SSHConnector, config: Dict[str, Any])
```

**Inherits all methods from BaseChecker**

**Supported Checks:**
- `disk_usage`: Filesystem usage analysis
- `memory`: Memory usage monitoring
- `cpu_load`: System load averages
- `services`: Subsystem status
- `network`: Network interface status
- `processes`: Top processes

### CheckResult

Represents the result of a health check.

```python
class CheckResult:
    def __init__(self, name: str, status: str, message: str, 
                 details: Optional[Dict[str, Any]] = None,
                 raw_output: Optional[str] = None,
                 timestamp: Optional[datetime] = None)
```

**Parameters:**
- `name` (str): Check name
- `status` (str): Check status ('PASS', 'FAIL', 'WARN', 'SKIP')
- `message` (str): Check result message
- `details` (dict, optional): Additional details about the check
- `raw_output` (str, optional): Raw command output
- `timestamp` (datetime, optional): Check timestamp

**Methods:**

#### to_dict()
Convert check result to dictionary.

```python
def to_dict(self) -> Dict[str, Any]
```

**Returns:** Dictionary representation of the check result

## Command Module

### CommandExecutor

Manages command execution with caching and parameter injection.

```python
class CommandExecutor:
    def __init__(self, ssh_connector: SSHConnector, cache_ttl: int = 300)
```

**Parameters:**
- `ssh_connector` (SSHConnector): SSH connection instance
- `cache_ttl` (int): Cache time-to-live in seconds

**Methods:**

#### load_commands_from_file(file_path, os_type)
Load commands from external script file.

```python
def load_commands_from_file(self, file_path: str, os_type: str) -> None
```

**Parameters:**
- `file_path` (str): Path to command file
- `os_type` (str): OS type ('linux' or 'aix')

**Raises:** `CommandExecutionError`

#### inject_parameters(command, params)
Inject parameters into command template.

```python
def inject_parameters(self, command: str, params: Dict[str, Any]) -> str
```

**Parameters:**
- `command` (str): Command template with placeholders
- `params` (dict): Parameters to inject

**Returns:** Command with parameters injected

#### execute_command(command, params=None, use_cache=True, timeout=None)
Execute command with caching and parameter injection.

```python
def execute_command(self, command: str, params: Optional[Dict[str, Any]] = None,
                   use_cache: bool = True, timeout: Optional[int] = None) -> Tuple[str, str, int]
```

**Parameters:**
- `command` (str): Command to execute
- `params` (dict, optional): Parameters to inject into command
- `use_cache` (bool): Whether to use cached results
- `timeout` (int, optional): Command timeout in seconds

**Returns:** Tuple of (stdout, stderr, exit_code)

#### execute_commands_batch(commands)
Execute multiple commands in batch.

```python
def execute_commands_batch(self, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]
```

**Parameters:**
- `commands` (list): List of command dictionaries

**Returns:** List of results

#### clear_cache()
Clear command cache.

```python
def clear_cache(self) -> None
```

#### get_cache_stats()
Get cache statistics.

```python
def get_cache_stats(self) -> Dict[str, Any]
```

**Returns:** Cache statistics dictionary

#### validate_command(command)
Validate command syntax and safety.

```python
def validate_command(self, command: str) -> bool
```

**Parameters:**
- `command` (str): Command to validate

**Returns:** True if command is safe, False otherwise

## Report Module

### ReportGenerator

Generates health check reports in various formats.

```python
class ReportGenerator:
    def __init__(self, config: Optional[Dict[str, Any]] = None)
```

**Parameters:**
- `config` (dict, optional): Report configuration

**Methods:**

#### generate_report(host, os_type, results, summary, timestamp=None)
Generate health check report in configured formats.

```python
def generate_report(self, host: str, os_type: str, results: List[CheckResult],
                   summary: Dict[str, Any], timestamp: Optional[datetime] = None) -> Dict[str, str]
```

**Parameters:**
- `host` (str): Host name or IP
- `os_type` (str): Operating system type
- `results` (list): List of check results
- `summary` (dict): Check summary statistics
- `timestamp` (datetime, optional): Report timestamp

**Returns:** Dictionary mapping format to file path

**Raises:** `ReportGenerationError`

#### generate_batch_report(reports)
Generate a batch report for multiple hosts.

```python
def generate_batch_report(self, reports: List[Dict[str, Any]]) -> str
```

**Parameters:**
- `reports` (list): List of report data dictionaries

**Returns:** Path to generated batch report file

## Logger Module

### get_logger(name, config=None)
Get configured logger instance.

```python
def get_logger(name: str, config: Optional[Dict[str, Any]] = None) -> logging.Logger
```

**Parameters:**
- `name` (str): Logger name
- `config` (dict, optional): Logging configuration

**Returns:** Configured logger instance

### configure_logging(config)
Configure root logger for the application.

```python
def configure_logging(config: Dict[str, Any]) -> None
```

**Parameters:**
- `config` (dict): Logging configuration

## Exceptions

### HealthCheckError

Base exception for all health check related errors.

```python
class HealthCheckError(Exception)
```

### ConfigurationError

Raised when there's an issue with configuration.

```python
class ConfigurationError(HealthCheckError)
```

### ConnectionError

Raised when there's an issue with SSH connections.

```python
class ConnectionError(HealthCheckError)
```

### AuthenticationError

Raised when SSH authentication fails.

```python
class AuthenticationError(ConnectionError)
```

### CommandExecutionError

Raised when command execution fails.

```python
class CommandExecutionError(HealthCheckError)
```

### ReportGenerationError

Raised when report generation fails.

```python
class ReportGenerationError(HealthCheckError)
```

### ValidationError

Raised when validation of inputs or prerequisites fails.

```python
class ValidationError(HealthCheckError)
```

### TimeoutError

Raised when operations timeout.

```python
class TimeoutError(HealthCheckError)
```

## Main Application

### HealthCheckApp

Main health check application.

```python
class HealthCheckApp:
    def __init__(self, config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (str, optional): Path to configuration file

**Methods:**

#### run_single_host_check(host_config)
Run health check on a single host.

```python
def run_single_host_check(self, host_config: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters:**
- `host_config` (dict): Host configuration

**Returns:** Check results dictionary

#### run_batch_check(hosts_file)
Run health check on multiple hosts.

```python
def run_batch_check(self, hosts_file: str) -> List[Dict[str, Any]]
```

**Parameters:**
- `hosts_file` (str): Path to hosts configuration file

**Returns:** List of check results

#### run_scheduled_check(hosts_file, interval=3600)
Run scheduled health checks.

```python
def run_scheduled_check(self, hosts_file: str, interval: int = 3600) -> None
```

**Parameters:**
- `hosts_file` (str): Path to hosts configuration file
- `interval` (int): Check interval in seconds

## Usage Examples

### Basic Usage

```python
from health_check import HealthCheckApp

# Initialize app
app = HealthCheckApp('config.yaml')

# Single host check
host_config = {
    'host': '192.168.1.100',
    'username': 'admin',
    'password': 'secret',
    'os_type': 'linux'
}

result = app.run_single_host_check(host_config)
print(f"Status: {result['summary']['overall_status']}")
```

### Advanced Usage

```python
from health_check.config import ConfigManager
from health_check.connection import SSHConnector
from health_check.checker import LinuxChecker
from health_check.report import ReportGenerator

# Load configuration
config = ConfigManager('config.yaml')

# Create SSH connection
host_config = {'host': '192.168.1.100', 'username': 'admin', 'password': 'secret'}
ssh_config = config.get_ssh_config()

with SSHConnector(host_config, ssh_config) as connector:
    # Create checker
    checker_config = config.get_checks_config('linux')
    checker = LinuxChecker(connector, checker_config)
    
    # Run checks
    results = checker.run_all_checks()
    summary = checker.get_summary()
    
    # Generate report
    report_config = config.get_report_config()
    generator = ReportGenerator(report_config)
    report_files = generator.generate_report(
        host='192.168.1.100',
        os_type='linux',
        results=results,
        summary=summary
    )
    
    print(f"Reports generated: {report_files}")
```

### Custom Checker Implementation

```python
from health_check.checker.base_checker import BaseChecker, CheckResult

class CustomChecker(BaseChecker):
    def get_os_type(self):
        return 'custom_os'
    
    def get_default_commands(self):
        return {
            'custom_check': 'custom_command --option'
        }
    
    def parse_result(self, check_name, stdout, stderr, exit_code):
        if check_name == 'custom_check':
            # Custom parsing logic
            if 'ERROR' in stdout:
                status = 'FAIL'
                message = 'Custom check detected errors'
            else:
                status = 'PASS'
                message = 'Custom check passed'
            
            return CheckResult(
                name=check_name,
                status=status,
                message=message,
                details={'exit_code': exit_code}
            )
        
        # Default handling for other checks
        return CheckResult(
            name=check_name,
            status='PASS' if exit_code == 0 else 'FAIL',
            message=f"Command completed with exit code {exit_code}"
        )
```