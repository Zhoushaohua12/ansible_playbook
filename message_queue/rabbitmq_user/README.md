# RabbitMQ 用户管理

本模块提供 RabbitMQ 用户、虚拟主机和权限的自动化管理功能，支持创建用户、配置权限、管理虚拟主机和标签。

## 模块用途

- 创建和删除 RabbitMQ 用户
- 配置用户密码和标签（tags）
- 管理虚拟主机（vhosts）
- 设置用户权限（configure、write、read）
- 配置用户访问控制和资源限制

## 主要参数

### 连接参数
- `rabbitmq_management_url`: RabbitMQ Management API 地址（默认：`http://localhost:15672`）
- `rabbitmq_admin_user`: 管理员用户名
- `rabbitmq_admin_password`: 管理员密码
- `rabbitmq_verify_ssl`: 是否验证 SSL 证书

### 用户参数
- `name`: 用户名（必需）
- `password`: 用户密码
- `tags`: 用户标签列表（如：`administrator`, `monitoring`）
- `state`: 用户状态（`present` 或 `absent`）
- `update_password`: 密码更新策略（`always` 或 `on_create`）

### 虚拟主机参数
- `vhost`: 虚拟主机名称
- `state`: 虚拟主机状态
- `tracing`: 是否启用消息追踪

### 权限参数
- `user`: 用户名
- `vhost`: 虚拟主机
- `configure_priv`: 配置权限正则表达式
- `write_priv`: 写权限正则表达式
- `read_priv`: 读权限正则表达式

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `user`: 用户信息
- `permissions`: 权限配置信息

## 常见使用场景

### 1. 创建管理员用户
```yaml
- name: 创建 RabbitMQ 管理员用户
  community.rabbitmq.rabbitmq_user:
    user: admin
    password: "{{ vault_rabbitmq_admin_password }}"
    tags: administrator
    state: present
  no_log: true
```

### 2. 创建应用用户
```yaml
- name: 创建应用用户
  community.rabbitmq.rabbitmq_user:
    user: app_user
    password: "{{ vault_rabbitmq_app_password }}"
    vhost: /app
    configure_priv: "^$"
    write_priv: "app.*"
    read_priv: "app.*"
    tags: ""
    state: present
  no_log: true
```

### 3. 创建虚拟主机
```yaml
- name: 创建虚拟主机
  community.rabbitmq.rabbitmq_vhost:
    name: /app
    state: present
    tracing: false
```

### 4. 配置用户权限
```yaml
- name: 配置用户权限
  community.rabbitmq.rabbitmq_user:
    user: app_user
    vhost: /app
    configure_priv: "^$"
    write_priv: "app\..*"
    read_priv: "app\..*"
    state: present
```

## 安全提示

### ⚠️ 敏感信息处理

1. **密码管理**
   - 使用 Ansible Vault 加密所有用户密码
   - 定期轮换用户密码
   - 禁用默认 `guest` 用户或限制其访问
   - 使用强密码策略

2. **权限控制**
   - 遵循最小权限原则
   - 为不同应用创建独立用户
   - 使用虚拟主机隔离不同环境
   - 定期审计用户权限

3. **网络安全**
   - 限制 Management API 访问
   - 使用 TLS/SSL 加密连接
   - 配置防火墙规则
   - 启用客户端证书认证

### 变量占位符示例
```yaml
# 不要这样写！
rabbitmq_admin_password: "admin123"
rabbitmq_user_password: "password123"

# 推荐方式
rabbitmq_admin_password: "{{ vault_rabbitmq_admin_password }}"
rabbitmq_user_password: "{{ vault_rabbitmq_user_password }}"

# 或使用环境变量
rabbitmq_admin_password: "{{ lookup('env', 'RABBITMQ_ADMIN_PASSWORD') }}"
```

## 依赖要求

- Ansible collection: `community.rabbitmq`
- Python 库: `requests`
- RabbitMQ Server: 3.8+ 版本
- RabbitMQ Management Plugin: 必须启用

## 安装步骤

1. 安装 Ansible collection：
```bash
ansible-galaxy collection install community.rabbitmq
```

2. 安装 Python 依赖：
```bash
pip install requests
```

3. 安装 RabbitMQ：
```bash
# Ubuntu/Debian
apt-get install rabbitmq-server

# RHEL/CentOS
yum install rabbitmq-server
```

4. 启用 Management Plugin：
```bash
rabbitmq-plugins enable rabbitmq_management
```

5. 创建初始管理员用户：
```bash
rabbitmqctl add_user admin changeme
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

## 用户标签说明

- `administrator`: 管理员，可以访问所有功能
- `monitoring`: 监控用户，可以访问监控 API
- `policymaker`: 策略制定者，可以管理策略
- `management`: 管理用户，可以访问 Management UI
- `impersonator`: 模拟用户，可以模拟其他用户

## 权限配置

### 权限类型
- **configure**: 创建和删除资源（队列、交换机）
- **write**: 发布消息
- **read**: 消费消息和获取队列信息

### 权限正则表达式示例
```yaml
# 允许所有操作
configure_priv: ".*"
write_priv: ".*"
read_priv: ".*"

# 禁止所有操作
configure_priv: "^$"
write_priv: "^$"
read_priv: "^$"

# 只允许特定前缀
configure_priv: "^app_.*"
write_priv: "^app_.*"
read_priv: "^app_.*"
```

## 调试方法

- 列出用户：`rabbitmqctl list_users`
- 列出权限：`rabbitmqctl list_permissions -p /`
- 列出虚拟主机：`rabbitmqctl list_vhosts`
- 验证连接：`curl -u admin:password http://localhost:15672/api/whoami`
- 查看日志：`tail -f /var/log/rabbitmq/rabbit@hostname.log`

## 最佳实践

1. **用户管理**: 为每个应用创建独立用户
2. **虚拟主机**: 使用虚拟主机隔离不同环境
3. **权限最小化**: 只授予必要的权限
4. **密码策略**: 使用强密码并定期更换
5. **审计日志**: 启用审计插件记录操作
6. **备份配置**: 定期导出用户和权限配置
