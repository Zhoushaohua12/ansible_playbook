"""
Health Check Module for Linux/AIX Systems

A modular, object-oriented health check system for Linux and AIX systems
with SSH connectivity, configurable checks, and multiple report formats.
"""

__version__ = "1.0.0"
__author__ = "Health Check Team"

from .checker.base_checker import BaseChecker
from .checker.linux_checker import LinuxChecker
from .checker.aix_checker import AIXChecker
from .connection.ssh_connector import SSHConnector
from .config.config_manager import ConfigManager
from .command.command_executor import CommandExecutor
from .report.report_generator import ReportGenerator
from .exceptions import (
    HealthCheckError,
    ConfigurationError,
    ConnectionError,
    CommandExecutionError,
    ReportGenerationError
)

__all__ = [
    "BaseChecker",
    "LinuxChecker", 
    "AIXChecker",
    "SSHConnector",
    "ConfigManager",
    "CommandExecutor",
    "ReportGenerator",
    "HealthCheckError",
    "ConfigurationError",
    "ConnectionError",
    "CommandExecutionError",
    "ReportGenerationError"
]