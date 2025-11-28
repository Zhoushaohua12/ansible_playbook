"""
Linux system health checker.

Implements health checks specific to Linux systems.
"""

import re
from typing import Dict, Any
from .base_checker import BaseChecker, CheckResult


class LinuxChecker(BaseChecker):
    """Health checker for Linux systems."""
    
    def get_os_type(self) -> str:
        """Return the OS type."""
        return 'linux'
    
    def get_default_commands(self) -> Dict[str, str]:
        """Return default commands for Linux systems."""
        return {
            'disk_usage': 'df -h',
            'memory': 'free -m',
            'cpu_load': 'uptime',
            'services': 'systemctl list-units --type=service --state=failed',
            'network': 'ip addr show',
            'processes': 'ps aux | head -20'
        }
    
    def parse_result(self, check_name: str, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """
        Parse Linux-specific command results.
        
        Args:
            check_name: Name of the check
            stdout: Standard output
            stderr: Standard error
            exit_code: Exit code
            
        Returns:
            Parsed CheckResult
        """
        if check_name == 'disk_usage':
            return self._parse_disk_usage(stdout, stderr, exit_code)
        elif check_name == 'memory':
            return self._parse_memory(stdout, stderr, exit_code)
        elif check_name == 'cpu_load':
            return self._parse_cpu_load(stdout, stderr, exit_code)
        elif check_name == 'services':
            return self._parse_services(stdout, stderr, exit_code)
        elif check_name == 'network':
            return self._parse_network(stdout, stderr, exit_code)
        elif check_name == 'processes':
            return self._parse_processes(stdout, stderr, exit_code)
        else:
            # Default parsing for unknown checks
            status = 'PASS' if exit_code == 0 else 'FAIL'
            message = f"Command executed with exit code {exit_code}"
            
            return CheckResult(
                name=check_name,
                status=status,
                message=message,
                details={'exit_code': exit_code},
                raw_output=stdout
            )
    
    def _parse_disk_usage(self, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """Parse disk usage output."""
        if exit_code != 0:
            return CheckResult(
                name='disk_usage',
                status='FAIL',
                message=f"Failed to get disk usage: {stderr.strip()}",
                raw_output=stdout
            )
        
        lines = stdout.strip().split('\n')
        if len(lines) < 2:
            return CheckResult(
                name='disk_usage',
                status='FAIL',
                message="Invalid disk usage output",
                raw_output=stdout
            )
        
        # Parse filesystem usage
        filesystems = []
        warning_count = 0
        
        for line in lines[1:]:  # Skip header
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 6:
                usage_percent = parts[4].rstrip('%')
                try:
                    usage = int(usage_percent)
                    filesystems.append({
                        'filesystem': parts[0],
                        'size': parts[1],
                        'used': parts[2],
                        'available': parts[3],
                        'usage_percent': usage,
                        'mount_point': parts[5]
                    })
                    
                    if usage > 90:
                        warning_count += 1
                except ValueError:
                    continue
        
        status = 'FAIL' if warning_count > 0 else 'PASS'
        message = f"Disk usage check completed. {warning_count} filesystem(s) above 90% usage"
        
        return CheckResult(
            name='disk_usage',
            status=status,
            message=message,
            details={
                'filesystems': filesystems,
                'warning_count': warning_count
            },
            raw_output=stdout
        )
    
    def _parse_memory(self, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """Parse memory usage output."""
        if exit_code != 0:
            return CheckResult(
                name='memory',
                status='FAIL',
                message=f"Failed to get memory info: {stderr.strip()}",
                raw_output=stdout
            )
        
        # Parse free -m output
        memory_info = {}
        lines = stdout.strip().split('\n')
        
        for line in lines:
            if line.startswith('Mem:'):
                parts = line.split()
                if len(parts) >= 7:
                    memory_info['total'] = int(parts[1])
                    memory_info['used'] = int(parts[2])
                    memory_info['free'] = int(parts[3])
                    memory_info['available'] = int(parts[6])
                    memory_info['usage_percent'] = int((memory_info['used'] / memory_info['total']) * 100)
        
        if not memory_info:
            return CheckResult(
                name='memory',
                status='FAIL',
                message="Failed to parse memory information",
                raw_output=stdout
            )
        
        usage_percent = memory_info['usage_percent']
        status = 'WARN' if usage_percent > 90 else 'PASS'
        message = f"Memory usage: {usage_percent}% ({memory_info['used']}MB used of {memory_info['total']}MB)"
        
        return CheckResult(
            name='memory',
            status=status,
            message=message,
            details=memory_info,
            raw_output=stdout
        )
    
    def _parse_cpu_load(self, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """Parse CPU load from uptime output."""
        if exit_code != 0:
            return CheckResult(
                name='cpu_load',
                status='FAIL',
                message=f"Failed to get CPU load: {stderr.strip()}",
                raw_output=stdout
            )
        
        # Parse uptime output for load averages
        load_match = re.search(r'load average: ([\d.]+), ([\d.]+), ([\d.]+)', stdout)
        if not load_match:
            return CheckResult(
                name='cpu_load',
                status='FAIL',
                message="Failed to parse CPU load information",
                raw_output=stdout
            )
        
        load_1min = float(load_match.group(1))
        load_5min = float(load_match.group(2))
        load_15min = float(load_match.group(3))
        
        # Get CPU count for comparison
        try:
            cpu_count_stdout, _, cpu_count_exit = self.ssh_connector.execute_command("nproc")
            cpu_count = int(cpu_count_stdout.strip()) if cpu_count_exit == 0 else 1
        except:
            cpu_count = 1
        
        load_info = {
            'load_1min': load_1min,
            'load_5min': load_5min,
            'load_15min': load_15min,
            'cpu_count': cpu_count,
            'load_per_cpu': load_1min / cpu_count
        }
        
        # Consider high load if load per CPU > 2.0
        status = 'WARN' if load_info['load_per_cpu'] > 2.0 else 'PASS'
        message = f"CPU load: {load_1min:.2f} (1min), {load_5min:.2f} (5min), {load_15min:.2f} (15min)"
        
        return CheckResult(
            name='cpu_load',
            status=status,
            message=message,
            details=load_info,
            raw_output=stdout
        )
    
    def _parse_services(self, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """Parse systemd services status."""
        if exit_code != 0:
            return CheckResult(
                name='services',
                status='FAIL',
                message=f"Failed to get services status: {stderr.strip()}",
                raw_output=stdout
            )
        
        lines = stdout.strip().split('\n')
        failed_services = []
        
        for line in lines:
            if 'failed' in line.lower() and not line.startswith('UNIT'):
                parts = line.split()
                if len(parts) >= 4:
                    failed_services.append({
                        'unit': parts[0],
                        'load': parts[1],
                        'active': parts[2],
                        'sub': parts[3],
                        'description': ' '.join(parts[4:]) if len(parts) > 4 else ''
                    })
        
        status = 'FAIL' if failed_services else 'PASS'
        message = f"Found {len(failed_services)} failed service(s)"
        
        return CheckResult(
            name='services',
            status=status,
            message=message,
            details={'failed_services': failed_services},
            raw_output=stdout
        )
    
    def _parse_network(self, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """Parse network interface information."""
        if exit_code != 0:
            return CheckResult(
                name='network',
                status='FAIL',
                message=f"Failed to get network info: {stderr.strip()}",
                raw_output=stdout
            )
        
        # Parse network interfaces
        interfaces = []
        current_interface = None
        
        for line in stdout.split('\n'):
            line = line.strip()
            if re.match(r'^\d+:', line):  # Interface line
                if current_interface:
                    interfaces.append(current_interface)
                
                # Parse interface name and status
                interface_match = re.match(r'^\d+: (\w+): <(.+)> mtu (\d+)', line)
                if interface_match:
                    current_interface = {
                        'name': interface_match.group(1),
                        'flags': interface_match.group(2),
                        'mtu': int(interface_match.group(3)),
                        'addresses': []
                    }
            elif current_interface and line.startswith('inet '):
                # Parse IP address
                inet_match = re.match(r'inet (\S+)', line)
                if inet_match:
                    current_interface['addresses'].append(inet_match.group(1))
        
        if current_interface:
            interfaces.append(current_interface)
        
        # Check if at least one interface is UP
        up_interfaces = [i for i in interfaces if 'UP' in i.get('flags', '')]
        status = 'PASS' if up_interfaces else 'FAIL'
        message = f"Found {len(interfaces)} interface(s), {len(up_interfaces)} up"
        
        return CheckResult(
            name='network',
            status=status,
            message=message,
            details={'interfaces': interfaces, 'up_count': len(up_interfaces)},
            raw_output=stdout
        )
    
    def _parse_processes(self, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """Parse process information."""
        if exit_code != 0:
            return CheckResult(
                name='processes',
                status='FAIL',
                message=f"Failed to get process info: {stderr.strip()}",
                raw_output=stdout
            )
        
        lines = stdout.strip().split('\n')
        processes = []
        
        for line in lines[1:]:  # Skip header
            if not line.strip():
                continue
            
            # Simple parsing of ps aux output
            parts = line.split(None, 10)  # Split on whitespace, max 11 parts
            if len(parts) >= 11:
                processes.append({
                    'user': parts[0],
                    'pid': parts[1],
                    'cpu': parts[2],
                    'mem': parts[3],
                    'command': parts[10]
                })
        
        status = 'PASS'
        message = f"Showing top {len(processes)} processes"
        
        return CheckResult(
            name='processes',
            status=status,
            message=message,
            details={'processes': processes},
            raw_output=stdout
        )