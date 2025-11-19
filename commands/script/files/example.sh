#!/bin/bash
# Ansible script 模块示例脚本
# 用途：演示脚本模块的使用方法和最佳实践
# 作者：Ansible 中文实践指南

# 错误处理设置
set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 获取脚本参数
SCRIPT_NAME="$0"
WORKING_DIR="${1:-/tmp/ansible_script_demo}"
APP_NAME="${2:-demo_app}"
LOG_FILE="$WORKING_DIR/deployment.log"

# 日志函数
log_info() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] INFO: $message" | tee -a "$LOG_FILE"
}

log_error() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ERROR: $message" | tee -a "$LOG_FILE" >&2
}

# 检查工作目录
check_working_directory() {
    log_info "检查工作目录: $WORKING_DIR"
    
    if [ ! -d "$WORKING_DIR" ]; then
        log_info "创建工作目录"
        mkdir -p "$WORKING_DIR"
    else
        log_info "工作目录已存在"
    fi
    
    # 检查目录权限
    if [ ! -w "$WORKING_DIR" ]; then
        log_error "工作目录无写权限: $WORKING_DIR"
        exit 1
    fi
    
    log_info "工作目录检查完成"
}

# 创建应用配置文件
create_app_config() {
    log_info "创建应用配置文件"
    
    local config_file="$WORKING_DIR/app.conf"
    
    cat > "$config_file" << EOF
# $APP_NAME 应用配置文件
# 生成时间: $(date)

[application]
name = $APP_NAME
version = 3.0.0
port = 9000
debug = true

[database]
host = localhost
port = 5432
name = demo_db
pool_size = 10

[logging]
level = INFO
file = $WORKING_DIR/app.log
max_size = 100MB

[server]
host = 0.0.0.0
workers = 4
timeout = 30s
EOF
    
    log_info "配置文件创建完成: $config_file"
}

# 创建启动脚本
create_startup_script() {
    log_info "创建应用启动脚本"
    
    local startup_file="$WORKING_DIR/start_app.sh"
    
    cat > "$startup_file" << 'EOF'
#!/bin/bash
# 应用启动脚本

APP_DIR="$(dirname "$0")"
CONFIG_FILE="$APP_DIR/app.conf"
PID_FILE="$APP_DIR/app.pid"
LOG_FILE="$APP_DIR/app.log"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 启动应用
echo "启动应用..."
cd "$APP_DIR"

# 模拟应用启动（实际应用中替换为真实启动命令）
echo "应用已启动，PID: $$" > "$PID_FILE"
echo "$(date): 应用启动成功" >> "$LOG_FILE"

echo "应用启动完成"
EOF
    
    chmod +x "$startup_file"
    log_info "启动脚本创建完成: $startup_file"
}

# 创建健康检查脚本
create_health_check() {
    log_info "创建健康检查脚本"
    
    local health_file="$WORKING_DIR/health_check.sh"
    
    cat > "$health_file" << 'EOF'
#!/bin/bash
# 应用健康检查脚本

APP_DIR="$(dirname "$0")"
PID_FILE="$APP_DIR/app.pid"
CONFIG_FILE="$APP_DIR/app.conf"

# 检查 PID 文件
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "应用运行正常，PID: $PID"
        exit 0
    else
        echo "应用未运行，PID 文件存在但进程不存在"
        exit 1
    fi
else
    echo "应用未运行，PID 文件不存在"
    exit 1
fi
EOF
    
    chmod +x "$health_file"
    log_info "健康检查脚本创建完成: $health_file"
}

# 创建备份脚本
create_backup_script() {
    log_info "创建备份脚本"
    
    local backup_file="$WORKING_DIR/backup.sh"
    local backup_dir="$WORKING_DIR/backups"
    
    cat > "$backup_file" << EOF
#!/bin/bash
# 应用备份脚本

APP_DIR="\$(dirname "\$0")"
BACKUP_DIR="$backup_dir"
CONFIG_FILE="\$APP_DIR/app.conf"
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="\$BACKUP_DIR/backup_\$TIMESTAMP.tar.gz"

# 创建备份目录
mkdir -p "\$BACKUP_DIR"

# 创建备份
echo "开始备份应用数据..."
tar -czf "\$BACKUP_FILE" -C "\$APP_DIR" app.conf start_app.sh health_check.sh

echo "备份完成: \$BACKUP_FILE"

# 清理旧备份（保留最近7天）
find "\$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
echo "旧备份清理完成"
EOF
    
    chmod +x "$backup_file"
    log_info "备份脚本创建完成: $backup_file"
}

# 显示部署信息
show_deployment_info() {
    log_info "部署完成，显示信息："
    echo ""
    echo "=== 应用部署信息 ==="
    echo "工作目录: $WORKING_DIR"
    echo "应用名称: $APP_NAME"
    echo "配置文件: $WORKING_DIR/app.conf"
    echo "启动脚本: $WORKING_DIR/start_app.sh"
    echo "健康检查: $WORKING_DIR/health_check.sh"
    echo "备份脚本: $WORKING_DIR/backup.sh"
    echo "日志文件: $LOG_FILE"
    echo ""
    echo "=== 使用方法 ==="
    echo "启动应用: $WORKING_DIR/start_app.sh"
    echo "健康检查: $WORKING_DIR/health_check.sh"
    echo "备份数据: $WORKING_DIR/backup.sh"
    echo ""
}

# 主函数
main() {
    log_info "开始执行 $SCRIPT_NAME"
    log_info "工作目录: $WORKING_DIR"
    log_info "应用名称: $APP_NAME"
    
    # 执行部署步骤
    check_working_directory
    create_app_config
    create_startup_script
    create_health_check
    create_backup_script
    show_deployment_info
    
    log_info "脚本执行完成"
}

# 脚本入口点
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi