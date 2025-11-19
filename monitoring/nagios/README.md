# Nagios 监控集成

本模块提供 Nagios 监控系统的自动化配置功能，支持主机管理、服务监控、告警配置等核心操作。

## 模块用途

- 自动添加和移除监控主机
- 批量配置服务检查项
- 管理联系人组和通知规则
- 统一维护监控配置文件

## 主要参数

### 连接参数
- `nagios_server`: Nagios 服务器地址
- `nagios_user`: API 访问用户名
- `nagios_password`: API 访问密码
- `nagios_config_path`: 配置文件路径（默认：`/etc/nagios3/conf.d`）

### 主机参数
- `host_name`: 主机名（FQDN）
- `host_address`: IP 地址
- `host_groups`: 主机组列表
- `host_template`: 使用的主机模板

### 服务参数
- `service_description`: 服务描述
- `check_command`: 检查命令
- `max_check_attempts`: 最大重试次数
- `check_interval`: 检查间隔（分钟）
- `retry_interval`: 重试间隔（分钟）

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `host_status`: 主机配置状态
- `service_status`: 服务配置状态

## 常见使用场景

### 1. 服务探活监控
```yaml
- name: 添加 HTTP 服务监控
  community.general.nagios:
    action: "add_service"
    host_name: "{{ inventory_hostname }}"
    service_description: "HTTP Service"
    check_command: "check_http"
    # ... 其他参数
```

### 2. 基础设施监控
```yaml
- name: 添加系统负载监控
  community.general.nagios:
    action: "add_service"
    host_name: "{{ inventory_hostname }}"
    service_description: "System Load"
    check_command: "check_nrpe!check_load"
    # ... 其他参数
```

### 3. 云资源监控
```yaml
- name: 添加云实例监控
  community.general.nagios:
    action: "add_host"
    host_name: "{{ cloud_instance_name }}"
    host_address: "{{ cloud_instance_ip }}"
    host_groups: "cloud-servers"
    # ... 其他参数
```

## 安全提示

### ⚠️ 敏感信息处理

1. **API 凭证保护**
   - 使用 Ansible Vault 加密 `nagios_password`
   - 不要在代码中硬编码密码
   - 定期轮换访问凭证

2. **配置文件安全**
   - 限制配置文件的读取权限
   - 使用 `no_log: true` 保护敏感变量
   - 避免在日志中暴露密码信息

3. **网络安全**
   - 限制 API 访问的源 IP
   - 使用 HTTPS 连接 Nagios 服务器
   - 配置防火墙规则限制访问

### 变量占位符示例
```yaml
# 不要这样写！
nagios_password: "plaintext_password"

# 推荐方式
nagios_password: "{{ vault_nagios_password }}"
# 或使用环境变量
nagios_password: "{{ lookup('env', 'NAGIOS_PASSWORD') }}"
```

## 依赖要求

- Ansible collection: `community.general`
- Python 库: `python-nagios`
- Nagios 服务器配置：启用 CGI/API 访问
- 网络权限：管理节点到 Nagios 服务器的 HTTP/HTTPS 访问

## 安装步骤

1. 安装 Ansible collection：
```bash
ansible-galaxy collection install community.general
```

2. 安装 Python 依赖：
```bash
pip install python-nagios
```

3. 配置 Nagios 服务器 API 访问权限
4. 验证网络连通性和认证信息

## 调试方法

- 使用 `--check` 模式验证配置变更
- 检查 Nagios 配置文件语法：`nagios -v /etc/nagios3/nagios.cfg`
- 查看 Nagios 日志：`tail -f /var/log/nagios3/nagios.log`
- 测试 API 连接：手动调用 Nagios CGI 接口