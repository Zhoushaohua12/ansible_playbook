"""
Test module for health check system.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Set up test fixtures and configuration
@pytest.fixture
def mock_ssh_config():
    """Mock SSH configuration."""
    return {
        'timeout': 30,
        'max_retries': 3,
        'retry_delay': 5,
        'port': 22
    }

@pytest.fixture
def mock_host_config():
    """Mock host configuration."""
    return {
        'host': '192.168.1.100',
        'username': 'testuser',
        'password': 'testpass',
        'port': 22,
        'os_type': 'linux'
    }

@pytest.fixture
def mock_checks_config():
    """Mock checks configuration."""
    return {
        'enabled': True,
        'commands': {
            'disk_usage': 'df -h',
            'memory': 'free -m',
            'cpu_load': 'uptime',
            'services': 'systemctl list-units --type=service --state=failed',
            'network': 'ip addr show',
            'processes': 'ps aux | head -20'
        }
    }

@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file."""
    config_data = {
        'ssh': {
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 5,
            'port': 22
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'test_health_check.log',
            'console': False
        },
        'checks': {
            'linux': {
                'enabled': True,
                'commands': {
                    'disk_usage': 'df -h',
                    'memory': 'free -m'
                }
            },
            'aix': {
                'enabled': True,
                'commands': {
                    'disk_usage': 'df -g',
                    'memory': 'svmon -G'
                }
            }
        },
        'report': {
            'output_dir': './test_reports',
            'formats': ['json'],
            'include_raw_output': False
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(config_data, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)

@pytest.fixture
def sample_linux_outputs():
    """Sample Linux command outputs."""
    return {
        'disk_usage': """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        20G   5G   15G  25% /
/dev/sda2       100G  95G    5G  95% /data
tmpfs           2.0G     0  2.0G   0% /dev/shm""",
        'memory': """              total        used        free      shared  buff/cache   available
Mem:           3952        1024        2048          0         880        2928
Swap:          2047           0        2047""",
        'cpu_load': """ 10:30:15 up 10 days,  2:45,  2 users,  load average: 0.15, 0.20, 0.25""",
        'services': """UNIT LOAD ACTIVE SUB DESCRIPTION
0 failed units listed.""",
        'network': """1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:11:22:33:44:55 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.100/24 brd 192.168.1.255 scope global eth0""",
        'processes': """USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  19356  1544 ?        Ss   10:20   0:01 /sbin/init
root       123  0.0  0.2  25432  2048 ?        S    10:21   0:00 /usr/sbin/sshd
user       456  0.1  0.5  45678  2048 pts/0    Ss   10:25   0:00 -bash"""
    }

@pytest.fixture
def sample_aix_outputs():
    """Sample AIX command outputs."""
    return {
        'disk_usage': """Filesystem    GB blocks      Free %Used    Iused %Iused Mounted on
/dev/hd4           2.00      1.20   40%     1234    15% /
/dev/hd2          10.00      2.00   80%     5678    30% /usr""",
        'memory': """memory size 4096 MB
                size       inuse        free        pin    virtual
memory        4096MB      2048MB      2048MB       512MB      1024MB
pg space      2048MB       512MB      1536MB""",
        'cpu_load': """ 10:30:15 up 10 days,  2:45,  2 users,  load average: 0.15, 0.20, 0.25""",
        'services': """Subsystem         Group            PID          Status
sendmail          mail             1234         active
sshd              tcpip           5678         active""",
        'network': """lo0: flags=e08084b<UP,BROADCAST,LOOPBACK,RUNNING,SIMPLEX,MULTICAST,GROUPRT,64BIT>
        inet 127.0.0.1 netmask 0xff000000
en0: flags=1e080863<UP,BROADCAST,NOTRAILERS,RUNNING,SIMPLEX,MULTICAST,GROUPRT,64BIT>
        inet 192.168.1.100 netmask 0xffffff00 broadcast 192.168.1.255""",
        'processes': """  UID   PID  PPID   C    STIME TTY  TIME CMD
    0     1     0   0   Oct 20 ?    0:10 /etc/init
    0  1234     1   0   Oct 20 ?    0:05 /usr/sbin/sshd
  100  4567  1234   0   10:25 pts/0 0:00 -ksh"""
    }