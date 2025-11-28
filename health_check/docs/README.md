# Health Check System

A comprehensive, modular health check system for Linux and AIX systems with SSH connectivity, configurable checks, and multiple report formats.

## Features

- **Modular Design**: Object-oriented architecture with clear separation of concerns
- **Multi-OS Support**: Native support for Linux and AIX systems
- **SSH Connectivity**: Secure remote command execution with connection pooling and retry logic
- **Configurable Checks**: Flexible configuration system with YAML support
- **Multiple Report Formats**: JSON, HTML, and plain text reports
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Unit Testing**: Extensive test coverage with pytest
- **Command Line Interface**: Easy-to-use CLI for automation

## Installation

### Prerequisites

- Python 3.8+
- SSH access to target systems

### Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `paramiko` - SSH connectivity
- `pyyaml` - YAML configuration support
- `pytest` - Testing framework
- `pytest-cov` - Test coverage

## Quick Start

### 1. Basic Single Host Check

```bash
python health_check.py --host 192.168.1.100 --username admin --password secret --os-type linux
```

### 2. Check with SSH Key

```bash
python health_check.py --host 192.168.1.100 --username admin --key-file ~/.ssh/id_rsa --os-type linux
```

### 3. Batch Check

Create a hosts configuration file:

```yaml
# hosts.yaml
hosts:
  - host: "192.168.1.100"
    username: "admin"
    password: "secret"
    os_type: "linux"
    port: 22
  - host: "192.168.1.101"
    username: "admin"
    password: "secret"
    os_type: "aix"
    port: 22
```

Run batch check:

```bash
python health_check.py --batch hosts.yaml
```

### 4. Scheduled Checks

```bash
# Run checks every hour
python health_check.py --scheduled hosts.yaml --interval 3600
```

## Configuration

### Configuration File

The system uses `config/config.yaml` for configuration. A default configuration is created automatically if not present.

```yaml
# SSH Connection Configuration
ssh:
  timeout: 30
  max_retries: 3
  retry_delay: 5
  key_file: null
  port: 22

# Logging Configuration
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: health_check.log
  console: true

# Health Check Commands Configuration
checks:
  linux:
    enabled: true
    commands:
      disk_usage: "df -h"
      memory: "free -m"
      cpu_load: "uptime"
      services: "systemctl list-units --type=service --state=failed"
      network: "ip addr show"
      processes: "ps aux | head -20"
  
  aix:
    enabled: true
    commands:
      disk_usage: "df -g"
      memory: "svmon -G"
      cpu_load: "uptime"
      services: "lssrc -a"
      network: "ifconfig -a"
      processes: "ps -ef | head -20"

# Report Configuration
report:
  output_dir: "./reports"
  formats: ["json", "html"]
  include_raw_output: false
```

### Environment Variables

Configuration values can be overridden using environment variables:

```bash
export HEALTH_CHECK_SSH_TIMEOUT=60
export HEALTH_CHECK_LOGGING_LEVEL=DEBUG
export HEALTH_CHECK_REPORT_FORMATS="json,html,text"
```

## Command Line Options

```
usage: health_check.py [-h] [--host HOST] [--username USERNAME] [--password PASSWORD]
                       [--key-file KEY_FILE] [--port PORT] [--os-type {linux,aix}]
                       [--batch BATCH] [--scheduled SCHEDULED] [--interval INTERVAL]
                       [--config CONFIG] [--verbose] [--quiet]

Health Check System for Linux/AIX

Single Host Options:
  --host HOST           Host IP or hostname
  --username USERNAME   SSH username
  --password PASSWORD   SSH password
  --key-file KEY_FILE   SSH private key file
  --port PORT           SSH port (default: 22)
  --os-type {linux,aix} Operating system type

Batch Options:
  --batch BATCH         YAML file with multiple host configurations

Scheduled Check Options:
  --scheduled SCHEDULED Run scheduled checks using hosts file
  --interval INTERVAL   Check interval in seconds for scheduled mode

General Options:
  --config CONFIG       Path to configuration file
  --verbose, -v         Enable verbose logging
  --quiet, -q           Suppress console output
```

## Health Checks

### Linux Checks

- **Disk Usage**: Monitors filesystem usage using `df -h`
- **Memory**: Checks memory usage using `free -m`
- **CPU Load**: Monitors system load averages using `uptime`
- **Services**: Checks for failed systemd services
- **Network**: Verifies network interface status using `ip addr show`
- **Processes**: Shows top processes using `ps aux`

### AIX Checks

- **Disk Usage**: Monitors filesystem usage using `df -g`
- **Memory**: Checks memory usage using `svmon -G`
- **CPU Load**: Monitors system load averages using `uptime`
- **Services**: Checks subsystem status using `lssrc -a`
- **Network**: Verifies network interface status using `ifconfig -a`
- **Processes**: Shows top processes using `ps -ef`

## Reports

The system generates comprehensive reports in multiple formats:

### JSON Report

Machine-readable format with complete check details:

```json
{
  "host": "192.168.1.100",
  "os_type": "linux",
  "timestamp": "2023-01-01T12:00:00",
  "summary": {
    "total": 6,
    "passed": 5,
    "failed": 1,
    "warning": 0,
    "skipped": 0,
    "overall_status": "FAIL"
  },
  "results": [...]
}
```

### HTML Report

Visual, web-friendly report with:
- Summary statistics
- Detailed check results
- Color-coded status indicators
- Expandable details sections

### Text Report

Plain text format suitable for:
- Email notifications
- Log files
- Command-line display

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=health_check --cov-report=html

# Run specific test file
pytest tests/test_config_manager.py

# Run with verbose output
pytest -v
```

Test coverage is maintained at 60% or higher.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## API Reference

See [API.md](API.md) for detailed API documentation.

## Examples

### Using as a Python Module

```python
from health_check import HealthCheckApp

# Initialize with custom config
app = HealthCheckApp('my_config.yaml')

# Single host check
host_config = {
    'host': '192.168.1.100',
    'username': 'admin',
    'password': 'secret',
    'os_type': 'linux'
}

result = app.run_single_host_check(host_config)
print(f"Status: {result['summary']['overall_status']}")

# Batch check
results = app.run_batch_check('hosts.yaml')
print(f"Checked {len(results)} hosts")
```

### Custom Check Implementation

```python
from health_check.checker.base_checker import BaseChecker, CheckResult

class CustomChecker(BaseChecker):
    def get_os_type(self):
        return 'linux'
    
    def get_default_commands(self):
        return {
            'custom_check': 'custom_command'
        }
    
    def parse_result(self, check_name, stdout, stderr, exit_code):
        # Custom parsing logic
        return CheckResult(
            name=check_name,
            status='PASS' if exit_code == 0 else 'FAIL',
            message=f"Custom check completed with exit code {exit_code}"
        )
```

## Troubleshooting

### Common Issues

1. **SSH Connection Failures**
   - Verify network connectivity
   - Check SSH service status on target
   - Validate credentials
   - Review firewall rules

2. **Command Failures**
   - Ensure required commands are installed
   - Check user permissions
   - Verify command syntax for OS version

3. **Report Generation Issues**
   - Check output directory permissions
   - Verify disk space
   - Review file system quotas

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python health_check.py --verbose --host 192.168.1.100 --username admin --password secret
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the project repository
- Review the troubleshooting section
- Check the architecture documentation