# Architecture Documentation

## System Overview

The Health Check System is designed with a modular, object-oriented architecture that promotes maintainability, extensibility, and testability. The system follows the Single Responsibility Principle and Dependency Injection patterns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Health Check System                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Main App  │    │ Config Mgr  │    │   Logger    │    │
│  │             │    │             │    │             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │SSH Connector│    │Command Exec │    │Report Gen   │    │
│  │             │    │             │    │             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │Base Checker │    │Linux Checker│    │AIX Checker  │    │
│  │             │    │             │    │             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### Core Modules

#### 1. Configuration Management (`config/`)

**Purpose**: Centralized configuration management with validation and environment variable support.

**Classes**:
- `ConfigManager`: Loads, validates, and manages configuration

**Key Features**:
- YAML-based configuration
- Environment variable overrides
- Configuration validation
- Type conversion
- Caching

**Dependencies**: None (core module)

#### 2. Connection Management (`connection/`)

**Purpose**: Secure SSH connectivity with retry logic and connection pooling.

**Classes**:
- `SSHConnector`: Manages SSH connections and command execution

**Key Features**:
- Connection pooling
- Automatic reconnection with exponential backoff
- Context manager support
- Comprehensive error handling
- Authentication methods (password, key file)

**Dependencies**: `paramiko`

#### 3. Health Checkers (`checker/`)

**Purpose**: OS-specific health check implementations.

**Classes**:
- `BaseChecker`: Abstract base class defining common interface
- `LinuxChecker`: Linux-specific health checks
- `AIXChecker`: AIX-specific health checks

**Key Features**:
- Polymorphic design
- Extensible check framework
- Result parsing and validation
- Prerequisites validation

**Dependencies**: `connection`, `logger`

#### 4. Command Execution (`command/`)

**Purpose**: Command execution with caching, parameter injection, and safety validation.

**Classes**:
- `CommandExecutor`: Manages command execution and caching

**Key Features**:
- Command result caching
- Parameter injection
- Safety validation
- Batch execution
- External script loading

**Dependencies**: `connection`, `logger`

#### 5. Report Generation (`report/`)

**Purpose**: Multi-format report generation with customizable output.

**Classes**:
- `ReportGenerator`: Generates reports in JSON, HTML, and text formats

**Key Features**:
- Multiple output formats
- Template-based HTML generation
- Batch reporting
- Configurable output options

**Dependencies**: `checker`

#### 6. Logging (`logger/`)

**Purpose**: Centralized logging configuration and management.

**Classes**:
- Logger configuration functions

**Key Features**:
- Configurable log levels
- Multiple output destinations
- Structured logging
- Performance-friendly

**Dependencies**: None (standard library)

## Class Relationships

### Inheritance Hierarchy

```
BaseChecker (Abstract)
├── LinuxChecker
└── AIXChecker
```

### Composition Relationships

```
HealthCheckApp
├── ConfigManager
├── ReportGenerator
└── SSHConnector (context)
    └── CommandExecutor
        └── BaseChecker (implementation)
            └── CheckResult
```

## Data Flow

### Single Host Check Flow

```
1. HealthCheckApp.load_config()
2. HealthCheckApp.validate_host_config()
3. SSHConnector.connect()
4. CommandExecutor.execute_commands()
5. BaseChecker.run_all_checks()
   ├─ BaseChecker.execute_check()
   ├─ BaseChecker.parse_result()
   └─ CheckResult created
6. ReportGenerator.generate_report()
7. HealthCheckApp.cleanup()
```

### Batch Check Flow

```
1. HealthCheckApp.load_hosts_config()
2. For each host:
   ├─ Execute Single Host Check Flow
   └─ Store results
3. ReportGenerator.generate_batch_report()
```

## Design Patterns

### 1. Strategy Pattern

**Used in**: Health checkers implementation

**Description**: Different OS types have different check strategies (Linux vs AIX)

```python
class BaseChecker(ABC):
    @abstractmethod
    def parse_result(self, check_name, stdout, stderr, exit_code):
        pass

class LinuxChecker(BaseChecker):
    def parse_result(self, check_name, stdout, stderr, exit_code):
        # Linux-specific parsing

class AIXChecker(BaseChecker):
    def parse_result(self, check_name, stdout, stderr, exit_code):
        # AIX-specific parsing
```

### 2. Factory Pattern

**Used in**: Checker creation

**Description**: Appropriate checker is created based on OS type

```python
def create_checker(os_type, connector, config):
    if os_type.lower() == 'linux':
        return LinuxChecker(connector, config)
    elif os_type.lower() == 'aix':
        return AIXChecker(connector, config)
    else:
        raise ConfigurationError(f"Unsupported OS type: {os_type}")
```

### 3. Template Method Pattern

**Used in**: Base checker workflow

**Description**: Common workflow with customizable steps

```python
def run_all_checks(self):
    self.validate_prerequisites()  # Common
    for check_name, command in self.commands.items():
        result = self.execute_check(check_name, command)  # Common
        # parse_result() is implemented by subclasses
```

### 4. Context Manager Pattern

**Used in**: SSH connections

**Description**: Automatic resource management

```python
with SSHConnector(host_config, ssh_config) as connector:
    # Connection is automatically managed
    results = checker.run_all_checks()
# Connection is automatically closed
```

### 5. Dependency Injection

**Used in**: Throughout the system

**Description**: Dependencies are injected rather than created

```python
class LinuxChecker(BaseChecker):
    def __init__(self, ssh_connector, config):
        self.ssh_connector = ssh_connector  # Injected
        self.config = config  # Injected
```

## Error Handling Strategy

### Exception Hierarchy

```
HealthCheckError (Base Exception)
├── ConfigurationError
├── ConnectionError
│   └── AuthenticationError
├── CommandExecutionError
├── ReportGenerationError
├── ValidationError
└── TimeoutError
```

### Error Handling Principles

1. **Fail Fast**: Validate inputs early
2. **Recovery**: Implement retry mechanisms where appropriate
3. **Context**: Preserve error context and chain exceptions
4. **Logging**: Log all errors with appropriate detail
5. **Graceful Degradation**: Continue processing when possible

## Security Considerations

### 1. Credential Management

- Support for SSH key files (preferred)
- Password authentication (fallback)
- Environment variable support for sensitive data
- No credential logging

### 2. Command Safety

- Command validation against dangerous patterns
- Parameter injection sanitization
- Limited command scope

### 3. Connection Security

- SSH protocol only
- Host key verification
- Connection timeouts

## Performance Considerations

### 1. Connection Management

- Connection pooling and reuse
- Lazy connection establishment
- Automatic cleanup

### 2. Caching

- Command result caching with TTL
- Configuration caching
- Avoid redundant operations

### 3. Concurrency

- Thread-safe logging
- Isolated checker instances
- Non-blocking operations where possible

## Extensibility

### Adding New OS Support

1. Create new checker class inheriting from `BaseChecker`
2. Implement required abstract methods
3. Add OS-specific commands to configuration
4. Update factory method

### Adding New Checks

1. Add command to configuration
2. Implement parsing logic in appropriate checker
3. Add test cases
4. Update documentation

### Adding New Report Formats

1. Add format method to `ReportGenerator`
2. Implement template/logic
3. Add tests
4. Update configuration schema

## Testing Strategy

### Test Categories

1. **Unit Tests**: Individual class/function testing
2. **Integration Tests**: Module interaction testing
3. **End-to-End Tests**: Complete workflow testing
4. **Mock Tests**: External dependency testing

### Test Coverage

- Minimum 60% code coverage
- Focus on critical paths
- Error condition testing
- Edge case validation

### Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── test_config_manager.py
├── test_ssh_connector.py
├── test_linux_checker.py
├── test_aix_checker.py
├── test_command_executor.py
├── test_report_generator.py
└── fixtures/
    ├── sample_hosts.yaml
    └── mock_responses.json
```

## Configuration Management

### Configuration Layers

1. **Default Configuration**: Built-in defaults
2. **File Configuration**: YAML configuration file
3. **Environment Variables**: Runtime overrides
4. **Command Line**: Session-specific overrides

### Configuration Validation

- Type validation
- Range validation
- Format validation
- Dependency validation

## Deployment Considerations

### Dependencies

- Python 3.8+
- External packages: paramiko, pyyaml
- Optional: pytest for testing

### Directory Structure

```
health_check/
├── __init__.py
├── health_check.py          # Main entry point
├── config/
├── connection/
├── checker/
├── command/
├── report/
├── logger/
├── exceptions.py
├── tests/
└── docs/
```

### Runtime Requirements

- SSH access to target systems
- Appropriate user permissions
- Network connectivity
- Sufficient disk space for reports