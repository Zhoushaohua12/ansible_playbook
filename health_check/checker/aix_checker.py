"""
AIX system health checker.

Implements health checks specific to AIX systems.
"""

import re
from typing import Dict, Any
from .base_checker import BaseChecker, CheckResult


class AIXChecker(BaseChecker):
    """Health checker for AIX systems."""
    
    def get_os_type(self) -> str:
        """Return the OS type."""
        return 'aix'
    
    def get_default_commands(self) -> Dict[str, str]:
        """Return default commands for AIX systems."""
        return {
            'disk_usage': 'df -g',
            'memory': 'svmon -G',
            'cpu_load': 'uptime',
            'services': 'lssrc -a',
            'network': 'ifconfig -a',
            'processes': 'ps -ef | head -20'
        }
    
    def parse_result(self, check_name: str, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """
        Parse AIX-specific command results.
        
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
        """Parse AIX disk usage output."""
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
        
        # Parse filesystem usage (AIX df -g output)
        filesystems = []
        warning_count = 0
        
        for line in lines[1:]:  # Skip header
            if not line.strip() or line.startswith('Filesystem'):
                continue
            
            parts = line.split()
            if len(parts) >= 6:
                usage_percent = parts[4].rstrip('%')
                try:
                    usage = int(usage_percent)
                    filesystems.append({
                        'filesystem': parts[0],
                        'blocks': parts[1],
                        'free': parts[2],
                        'used': parts[3],
                        'usage_percent': usage,
                        'mount_point': parts[6] if len(parts) > 6 else parts[5]
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
        """Parse AIX memory usage from svmon output."""
        if exit_code != 0:
            return CheckResult(
                name='memory',
                status='FAIL',
                message=f"Failed to get memory info: {stderr.strip()}",
                raw_output=stdout
            )
        
        # Parse svmon -G output
        memory_info = {}
        lines = stdout.strip().split('\n')
        
        for line in lines:
            if 'memory size' in line.lower():
                # Look for memory size information
                size_match = re.search(r'(\d+)\s*[KMGT]?B?', line)
                if size_match:
                    memory_info['total_pages'] = int(size_match.group(1))
            elif 'memory' in line.lower() and 'size' not in line.lower():
                # Parse memory details line
                if 'inuse' in line.lower() or 'in use' in line.lower():
                    use_match = re.search(r'(\d+)', line)
                    if use_match:
                        memory_info['in_use_pages'] = int(use_match.group(1))
                elif 'free' in line.lower():
                    free_match = re.search(r'(\d+)', line)
                    if free_match:
                        memory_info['free_pages'] = int(free_match.group(1))
        
        if not memory_info:
            return CheckResult(
                name='memory',
                status='FAIL',
                message="Failed to parse memory information",
                raw_output=stdout
            )
        
        # Calculate usage percentage if we have the data
        if 'total_pages' in memory_info and 'in_use_pages' in memory_info:
            total = memory_info['total_pages']
            used = memory_info['in_use_pages']
            memory_info['usage_percent'] = int((used / total) * 100)
            usage_percent = memory_info['usage_percent']
        else:
            usage_percent = 0
        
        status = 'WARN' if usage_percent > 90 else 'PASS'
        message = f"Memory usage: {usage_percent}%"
        
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
        
        # Parse uptime output for load averages (similar to Linux)
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
            cpu_count_stdout, _, cpu_count_exit = self.ssh_connector.execute_command("lsdev -c processor | wc -l")
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
        """Parse AIX services from lssrc output."""
        if exit_code != 0:
            return CheckResult(
                name='services',
                status='FAIL',
                message=f"Failed to get services status: {stderr.strip()}",
                raw_output=stdout
            )
        
        lines = stdout.strip().split('\n')
        services = []
        inactive_count = 0
        
        for line in lines:
            if not line.strip() or line.startswith('Subsystem'):
                continue
            
            # Parse lssrc -a output
            parts = line.split()
            if len(parts) >= 4:
                subsystem = parts[0]
                group = parts[1]
                pid = parts[2] if parts[2] != '-' and parts[2].isdigit() else None
                status = parts[3]
                
                services.append({
                    'subsystem': subsystem,
                    'group': group,
                    'status': status,
                    'pid': pid,
                    'description': ' '.join(parts[4:]) if len(parts) > 4 else ''
                })
                
                if status.lower() in ['inoperative', 'inactive']:
                    inactive_count += 1
        
        status = 'FAIL' if inactive_count > 0 else 'PASS'
        message = f"Found {len(services)} service(s), {inactive_count} inactive"
        
        return CheckResult(
            name='services',
            status=status,
            message=message,
            details={'services': services, 'inactive_count': inactive_count},
            raw_output=stdout
        )
    
    def _parse_network(self, stdout: str, stderr: str, exit_code: int) -> CheckResult:
        """Parse AIX network interface information."""
        if exit_code != 0:
            return CheckResult(
                name='network',
                status='FAIL',
                message=f"Failed to get network info: {stderr.strip()}",
                raw_output=stdout
            )
        
        # Parse ifconfig -a output
        interfaces = []
        current_interface = None
        
        for line in stdout.split('\n'):
            line = line.strip()
            
            # Interface name line
            interface_match = re.match(r'^(\w+):', line)
            if interface_match:
                if current_interface:
                    interfaces.append(current_interface)
                
                current_interface = {
                    'name': interface_match.group(1),
                    'flags': [],
                    'addresses': []
                }
                
                # Extract flags - handle both <...> and flags=... formats
                flags_match = re.search(r'flags=(\w+)<(.+?)>|flags=(\w+)(?:<(.+?)>)?', line)
                if flags_match:
                    if flags_match.group(3):  # <...> format
                        current_interface['flags'] = flags_match.group(3).split(',')
                    elif flags_match.group(2):  # flags=... format
                        current_interface['flags'] = flags_match.group(2).split(',')
                    else:  # Just flags word
                        current_interface['flags'] = [flags_match.group(1)]
            
            # Parse IP address
            elif current_interface and ('inet ' in line or 'inet6 ' in line):
                addr_match = re.search(r'inet\s+(\S+)', line)
                if addr_match:
                    current_interface['addresses'].append(addr_match.group(1))
                else:
                    # Try IPv6
                    addr_match = re.search(r'inet6\s+(\S+)', line)
                    if addr_match:
                        current_interface['addresses'].append(addr_match.group(1))
        
        if current_interface:
            interfaces.append(current_interface)
        
        # Check if at least one interface is UP
        up_interfaces = [i for i in interfaces if 'UP' in i.get('flags', [])]
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
        """Parse AIX process information."""
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
            
            # Parse ps -ef output
            parts = line.split(None, 7)  # Split on whitespace, max 8 parts
            if len(parts) >= 8:
                processes.append({
                    'user': parts[0],
                    'pid': parts[1],
                    'ppid': parts[2],
                    'c': parts[3],
                    'stime': parts[4],
                    'tty': parts[5],
                    'time': parts[6],
                    'command': parts[7]
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