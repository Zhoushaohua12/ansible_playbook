# cron 模块使用指南

## 模块用途
`ansible.builtin.cron` 模块用于管理 cron 定时任务，支持创建、修改和删除用户的定时任务。适用于自动化备份、日志清理、监控检查、定时脚本执行等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | 任务描述名称（必需） | "每日备份"、"日志清理" 等 |
| `job` | str | 要执行的命令或脚本（必需） | `/usr/local/bin/backup.sh`、`rm -rf /tmp/*.log` 等 |
| `minute` | str | 分钟（0-59，* 表示任意） | 0、30、*/15 等 |
| `hour` | str | 小时（0-23，* 表示任意） | 2、*/6、0-23 等 |
| `day` | str | 日期（1-31，* 表示任意） | 1、15、*/7 等 |
| `month` | str | 月份（1-12，* 表示任意） | 1、6-12、* 等 |
| `weekday` | str | 星期（0-7，0 和 7 都表示周日，* 表示任意） | 0、1-5、* 等 |
| `user` | str | 执行任务的用户（默认 root） | root、www-data、backup 等 |
| `state` | str | 任务状态（present 创建，absent 删除） | present、absent |
| `cron_file` | str | 自定义 cron 文件名（可选） | backup、cleanup 等 |
| `disabled` | bool | 是否禁用任务（注释掉） | true、false |
| `env` | bool | 是否设置环境变量 | true、false |
| `insertafter` | str | 在指定任务后插入 | `@reboot`、`@hourly` 等 |
| `backup` | bool | 是否备份原 cron 文件 | true、false |

## 特殊时间字符串

| 字符串 | 说明 |
|--------|------|
| `@reboot` | 系统重启时执行一次 |
| `@yearly` 或 `@annually` | 每年执行一次（0 0 1 1 *） |
| `@monthly` | 每月执行一次（0 0 1 * *） |
| `@weekly` | 每周执行一次（0 0 * * 0） |
| `@daily` 或 `@midnight` | 每天执行一次（0 0 * * *） |
| `@hourly` | 每小时执行一次（0 * * * *） |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `jobs` | 当前的 cron 任务列表 | ["backup", "cleanup"] |
| `envs` | 当前的环境变量列表 | ["PATH=/usr/local/bin"] |
| `crontab` | 完整的 crontab 内容 | 文本内容 |
| `changed` | 是否修改了 cron 配置 | true/false |
| `msg` | 操作结果消息 | "cron job added" |

## 使用情境

### 系统维护任务
- **日志清理**：定期清理过期日志文件，防止磁盘空间不足
- **临时文件清理**：清理 `/tmp`、`/var/tmp` 目录中的临时文件
- **系统备份**：定时备份重要数据和配置文件
- **系统监控**：定期检查系统状态并发送报告

### 应用运维任务
- **数据库备份**：定时备份数据库到指定位置
- **应用日志轮转**：轮转和压缩应用日志文件
- **缓存清理**：清理应用缓存和临时数据
- **健康检查**：检查应用服务状态并重启异常服务

### 数据处理任务
- **数据同步**：定时同步数据到备份服务器
- **报表生成**：生成日报、周报、月报等统计报表
- **数据归档**：将历史数据归档到长期存储
- **数据清理**：删除过期的临时数据

## 安全注意事项

### 权限控制
1. **最小权限原则**：使用专用用户执行 cron 任务，避免使用 root
2. **脚本权限**：确保脚本文件权限正确（755 或更严格）
3. **环境变量**：谨慎设置环境变量，避免路径劫持
4. **用户隔离**：不同应用的 cron 任务使用不同用户执行

### 命令安全
1. **绝对路径**：使用绝对路径执行命令，避免 PATH 劫持
2. **输入验证**：脚本中验证所有输入参数
3. **错误处理**：脚本中包含适当的错误处理逻辑
4. **日志记录**：记录任务执行结果，便于审计和故障排查

### 网络安全
1. **SSH 密钥**：使用 SSH 密钥而非密码进行远程操作
2. **防火墙规则**：确保 cron 任务的网络访问符合安全策略
3. **数据传输**：敏感数据传输使用加密方式
4. **访问控制**：限制 cron 任务只能访问必要的资源

## 环境依赖

### 必需
- 目标主机必须支持 cron 服务（cron、crond、vixie-cron 等）
- cron 服务必须正在运行
- 执行 cron 任务的用户必须存在

### 推荐
- 安装 `cronie` 或 `vixie-cron` 包
- 配置邮件服务用于 cron 任务输出发送
- 设置合理的日志轮转策略

## 常见问题

### 1. cron 任务不执行
**可能原因**：
- cron 服务未启动
- 时间格式错误
- 脚本路径不正确
- 权限不足

**排查方法**：
```bash
# 检查 cron 服务状态
sudo systemctl status cron

# 查看 cron 日志
sudo tail -f /var/log/cron.log

# 检查用户 crontab
crontab -u username -l
```

### 2. cron 任务执行失败
**可能原因**：
- 脚本本身有错误
- 环境变量缺失
- 权限问题
- 依赖服务未启动

**排查方法**：
```bash
# 手动执行脚本测试
/path/to/script.sh

# 检查脚本权限
ls -la /path/to/script.sh

# 查看 cron 邮件或日志
mail
tail /var/log/syslog | grep CRON
```

### 3. 环境变量问题
**解决方案**：
```yaml
- name: 设置环境变量的 cron 任务
  ansible.builtin.cron:
    name: "带环境变量的备份任务"
    job: "/usr/local/bin/backup.sh"
    minute: "0"
    hour: "2"
    user: "backup"
    environment:
      PATH: "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
      BACKUP_DIR: "/backup"
```

### 4. 权限问题
**解决方案**：
```yaml
- name: 为特定用户创建 cron 任务
  ansible.builtin.cron:
    name: "应用数据备份"
    job: "/opt/app/scripts/backup.sh"
    minute: "30"
    hour: "3"
    user: "appuser"
    state: present
```

## 最佳实践

### 创建备份任务示例
```yaml
- name: 创建每日数据库备份任务
  ansible.builtin.cron:
    name: "MySQL 数据库备份"
    job: "/usr/local/bin/mysql_backup.sh"
    minute: "0"
    hour: "2"
    user: "backup"
    state: present
    backup: yes
```

### 创建清理任务示例
```yaml
- name: 创建日志清理任务
  ansible.builtin.cron:
    name: "应用日志清理"
    job: "find /var/log/app -name '*.log' -mtime +7 -delete"
    minute: "0"
    hour: "4"
    weekday: "0"  # 每周日执行
    user: "logrotate"
    state: present
```

### 创建监控任务示例
```yaml
- name: 创建系统监控任务
  ansible.builtin.cron:
    name: "系统健康检查"
    job: "/usr/local/bin/health_check.sh"
    minute: "*/15"  # 每15分钟执行一次
    user: "monitor"
    state: present
```

### 使用特殊时间示例
```yaml
- name: 重启时执行的任务
  ansible.builtin.cron:
    name: "系统启动后检查"
    job: "/usr/local/bin/startup_check.sh"
    special_time: "@reboot"
    user: "root"
    state: present

- name: 每小时执行的任务
  ansible.builtin.cron:
    name: "缓存清理"
    job: "/usr/local/bin/clear_cache.sh"
    special_time: "@hourly"
    user: "www-data"
    state: present
```

### 禁用任务示例
```yaml
- name: 临时禁用备份任务
  ansible.builtin.cron:
    name: "MySQL 数据库备份"
    job: "/usr/local/bin/mysql_backup.sh"
    minute: "0"
    hour: "2"
    user: "backup"
    disabled: yes  # 禁用但不删除
    state: present
```

### 删除任务示例
```yaml
- name: 删除过期的清理任务
  ansible.builtin.cron:
    name: "旧版日志清理"
    state: absent
    user: "root"
```

## 相关示例
- [user 模块](../user/README.md) - 用户管理
- [service 模块](../service/README.md) - 服务管理
- [file 模块](../../files/file/README.md) - 文件权限管理
- [script 模块](../../commands/script/README.md) - 脚本执行