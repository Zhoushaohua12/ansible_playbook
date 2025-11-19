# Zabbix 监控集成

本模块提供 Zabbix 企业级开源监控系统的自动化配置功能，支持分布式监控、自动发现、模板管理和告警配置。

## 模块用途

- 自动添加和管理监控主机
- 批量应用监控模板和触发器
- 配置主机组和用户权限
- 管理监控项和图形配置
- 设置告警规则和通知渠道

## 主要参数

### 连接参数
- `zabbix_server`: Zabbix 服务器地址
- `zabbix_user`: API 访问用户名
- `zabbix_password`: API 访问密码
- `zabbix_url`: Zabbix Web UI URL（默认：`http://zabbix.example.com`）

### 主机参数
- `host_name`: 主机名（必须唯一）
- `host_groups`: 主机组列表
- `host_templates`: 应用模板列表
- `host_interfaces`: 主机接口配置（IPMI、SNMP、Agent、JMX）
- `host_status`: 主机状态（enabled/disabled）

### 监控参数
- `item_name`: 监控项名称
- `item_key`: 监控项键值
- `item_type`: 监控项类型（Zabbix agent、SNMP、计算型等）
- `trigger_expression`: 触发器表达式
- `trigger_severity`: 触发器严重级别

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `host_id`: 创建或更新的主机 ID
- `template_ids`: 应用的模板 ID 列表
- `trigger_ids`: 创建的触发器 ID 列表

## 常见使用场景

### 1. 大规模主机管理
```yaml
- name: 批量添加生产服务器
  community.zabbix.zabbix_host:
    server_url: "{{ zabbix_url }}"
    login_user: "{{ zabbix_user }}"
    login_password: "{{ zabbix_password }}"
    host_name: "{{ inventory_hostname }}"
    host_groups:
      - "Production Servers"
      - "Web Servers"
    templates:
      - "Template OS Linux"
      - "Template App HTTP Service"
    state: present
```

### 2. 自动发现和监控
```yaml
- name: 配置网络设备自动发现
  community.zabbix.zabbix_discovery_rule:
    server_url: "{{ zabbix_url }}"
    login_user: "{{ zabbix_user }}"
    login_password: "{{ zabbix_password }}"
    host_name: "{{ inventory_hostname }}"
    name: "Network Interface Discovery"
    key: "net.if.discovery"
    item_prototypes:
      - name: "Interface $1 inbound traffic"
        key: "net.if.in[{#IFNAME}]"
    state: present
```

### 3. 自定义监控模板
```yaml
- name: 创建应用服务监控模板
  community.zabbix.zabbix_template:
    server_url: "{{ zabbix_url }}"
    login_user: "{{ zabbix_user }}"
    login_password: "{{ zabbix_password }}"
    template_name: "Template App Custom Service"
    host_groups:
      - "Templates"
    items:
      - name: "Service Process Status"
        key: "proc.num[mysqld]"
    triggers:
      - name: "MySQL service is down"
        expression: "{Template App Custom Service:proc.num[mysqld].last()}=0"
        severity: "high"
    state: present
```

### 4. 分布式监控配置
```yaml
- name: 配置 Zabbix Proxy
  community.zabbix.zabbix_proxy:
    server_url: "{{ zabbix_url }}"
    login_user: "{{ zabbix_user }}"
    login_password: "{{ zabbix_password }}"
    proxy_name: "proxy-datacenter-01"
    proxy_address: "192.168.1.100"
    proxy_mode: 0  # 0=active, 1=passive
    state: present
```

## 安全提示

### ⚠️ 敏感信息处理

1. **API 凭证保护**
   - 使用 Ansible Vault 加密 `zabbix_password`
   - 创建专用的 API 用户，限制权限范围
   - 定期轮换访问凭证
   - 使用强密码和双因素认证

2. **网络安全配置**
   - 限制 Zabbix API 访问的源 IP 地址
   - 使用 HTTPS 连接 Zabbix Web UI
   - 配置防火墙规则限制端口访问
   - 启用 Zabbix 的安全设置（如 CSRF 保护）

3. **权限最小化原则**
   - 为不同团队创建专用的用户组
   - 限制用户只能访问相关的主机组
   - 分离读写权限，只读用户用于监控查询
   - 定期审计用户权限和访问日志

### 变量占位符示例
```yaml
# 不要这样写！
zabbix_password: "admin123"

# 推荐方式
zabbix_password: "{{ vault_zabbix_password }}"

# 或使用环境变量
zabbix_password: "{{ lookup('env', 'ZABBIX_PASSWORD') }}"

# 创建专用 API 用户示例
zabbix_api_user: "ansible-api-user"
zabbix_api_user_group: "API Access"
zabbix_api_permissions:
  - host_group: "Production Servers"
    permission: "read-write"
  - host_group: "Development Servers"
    permission: "read-only"
```

### 网络安全配置示例
```yaml
# Zabbix 服务器安全配置
zabbix_security:
  enforce_https: true
  allowed_networks:
    - "192.168.1.0/24"    # 管理网络
    - "10.0.0.0/8"        # 内网
    - "172.16.0.0/12"     # 私有网络
  
  # API 访问限制
  api_rate_limit:
    enabled: true
    max_requests_per_minute: 200
  
  # 会话管理
  session_timeout: 1800  # 30分钟
  max concurrent sessions: 10
```

## 依赖要求

- Ansible collection: `community.zabbix`
- Python 库: `zabbix-api`, `requests`
- Zabbix Server: 4.0+ 版本
- Zabbix Agent: 目标主机需要安装 Zabbix Agent
- 网络权限：管理节点到 Zabbix Server 的 HTTP/HTTPS 访问

## 安装步骤

1. 安装 Ansible collection：
```bash
ansible-galaxy collection install community.zabbix
```

2. 安装 Python 依赖：
```bash
pip install zabbix-api requests
```

3. 配置 Zabbix Server API 访问：
   - 创建 API 用户
   - 设置用户权限
   - 配置网络安全组

4. 安装和配置 Zabbix Agent：
   - 在目标主机安装 agent
   - 配置 agent 连接到 Zabbix Server
   - 启动 agent 服务

## API 管理提示

### 用户权限管理
- **超管用户**: 完全访问权限（谨慎使用）
- **管理员用户**: 主机和模板管理权限
- **只读用户**: 仅查看监控数据和报表
- **API 用户**: 专用于自动化脚本访问

### 主机组织结构
- **按环境分组**: Production, Staging, Development
- **按业务分组**: Web Servers, Database Servers, Application Servers
- **按地域分组**: Datacenter-01, Datacenter-02, Cloud-Region

### 模板层级管理
- **基础模板**: OS、网络、硬件监控
- **应用模板**: 特定应用服务监控
- **业务模板**: 业务指标和 KPI 监控
- **自定义模板**: 针对特殊需求的监控

## 调试方法

- 使用 `--check` 模式验证配置变更
- 检查 Zabbix Server 日志：`tail -f /var/log/zabbix/zabbix_server.log`
- 验证 API 连接：手动调用 Zabbix API
- 测试 Agent 连接：`zabbix_get -s <host> -k agent.ping`
- 查看监控数据：在 Zabbix Web UI 中检查最新数据

## 最佳实践

1. **分层监控**: 基础设施 → 平台 → 应用 → 业务
2. **模板继承**: 建立清晰的模板继承关系
3. **告警分级**: 合理设置告警严重级别和通知策略
4. **性能优化**: 定期清理历史数据，优化数据库性能
5. **灾难恢复**: 制定备份和恢复策略，定期测试

## 常见问题解决

- **Agent 连接失败**: 检查防火墙、DNS 解析、agent 配置
- **权限不足**: 验证 API 用户权限和 Zabbix 用户组设置
- **模板冲突**: 检查模板依赖关系和监控项键值冲突
- **性能问题**: 优化监控频率，调整数据保留策略
- **网络延迟**: 配置 Zabbix Proxy 实现分布式监控