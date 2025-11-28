#!/bin/bash

# AIX health check commands
# Format: COMMAND_NAME="command"

# Disk usage check
DISK_USAGE="df -g"

# Memory usage check
MEMORY="svmon -G"

# CPU load check
CPU_LOAD="uptime"

# Service status check
SERVICES="lssrc -a"

# Network interface check
NETWORK="ifconfig -a"

# Process information
PROCESSES="ps -ef | head -20"

# System information
SYSTEM_INFO="uname -a"

# Disk space analysis (detailed)
DISK_DETAIL="du -sg /* 2>/dev/null | sort -nr | head -10"

# Paging space usage
PAGING_SPACE="lsps -a"

# Volume group information
VG_INFO="lsvg"

# Logical volume information
LV_INFO="lsvg -l rootvg"