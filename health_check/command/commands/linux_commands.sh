#!/bin/bash

# Linux health check commands
# Format: COMMAND_NAME="command"

# Disk usage check
DISK_USAGE="df -h"

# Memory usage check
MEMORY="free -m"

# CPU load check
CPU_LOAD="uptime"

# Service status check
SERVICES="systemctl list-units --type=service --state=failed"

# Network interface check
NETWORK="ip addr show"

# Process information
PROCESSES="ps aux | head -20"

# System information
SYSTEM_INFO="uname -a"

# Disk space analysis (detailed)
DISK_DETAIL="du -sh /* 2>/dev/null | sort -hr | head -10"

# Open files count
OPEN_FILES="lsof | wc -l"

# Network connections
NET_CONNECTIONS="netstat -tuln | head -20"