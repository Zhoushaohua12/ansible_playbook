# Datadog 监控集成

本模块提供 Datadog 云原生监控平台的自动化配置功能，支持基础设施监控、应用性能监控（APM）、日志聚合和告警管理。

## 模块用途

- 自动部署和配置 Datadog Agent
- 管理监控主机和容器
- 配置自定义指标和日志收集
- 设置告警规则和通知集成
- 管理 Dashboard 和监控面板

## 主要参数

### 连接参数
- `datadog_api_key`: Datadog API Key（必需）
- `datadog_app_key`: Datadog Application Key（必需）
- `datadog_site`: Datadog 站点（默认：`datadoghq.com`）
- `datadog_api_url`: API 端点 URL

### Agent 配置参数
- `hostname`: 主机名标识
- `tags`: 主机标签列表
- `log_level`: 日志级别（info, warn, error）
- `process_enabled`: 是否启用进程监控
- `apm_enabled`: 是否启用 APM
- `logs_enabled`: 是否启用日志收集

### 监控参数
- `metric_name`: 指标名称
- `metric_type`: 指标类型（gauge, counter, rate, histogram）
- `threshold_warning`: 警告阈值
- `threshold_critical`: 严重阈值
- `evaluation_window`: 评估窗口时间

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `agent_status`: Agent 安装和配置状态
- `monitor_status`: 监控配置状态
- `dashboard_id`: 创建的 Dashboard ID

## 常见使用场景

### 1. 云监控集成
```yaml
- name: 配置云资源监控
  community.datadog.datadog_monitor:
    type: "metric alert"
    query: "avg(last_5m):avg:aws.ec2.cpuutilization{host:{{ inventory_hostname }}} > 80"
    name: "High CPU Usage on {{ inventory_hostname }}"
    # ... 其他参数
```

### 2. 应用性能监控
```yaml
- name: 配置 APM 服务监控
  community.datadog.datadog_service_check:
    check_name: "datadog.agent.up"
    host_name: "{{ inventory_hostname }}"
    status: "0"
    tags: "env:production,service:webapp"
```

### 3. 容器监控
```yaml
- name: 配置 Docker 监控
  community.datadog.datadog_agent_integration:
    integration_name: "docker"
    config:
      host: "unix:///var/run/docker.sock"
      collect_events: true
      container_include_all: true
```

### 4. 日志聚合配置
```yaml
- name: 配置日志收集
  community.datadog.datadog_agent_integration:
    integration_name: "logs"
    config:
      logs_enabled: true
      logs_config:
        logs_collect_container_logs: true
        logs_container_collect_all: true
```

## 安全提示

### ⚠️ 敏感信息处理

1. **API Key 管理**
   - 使用 Ansible Vault 加密 `datadog_api_key` 和 `datadog_app_key`
   - 定期轮换 API Key
   - 限制 API Key 权限范围（只读 vs. 读写）
   - 使用环境变量或密钥管理系统

2. **Agent 安全配置**
   - 限制 Agent 网络访问权限
   - 配置防火墙规则限制出站连接
   - 使用 TLS 加密 Agent 到 Datadog 的通信
   - 禁用不必要的集成和功能

3. **数据隐私保护**
   - 过滤敏感信息（密码、密钥、个人身份信息）
   - 配置日志脱敏规则
   - 使用标签隔离敏感环境数据

### 变量占位符示例
```yaml
# 不要这样写！
datadog_api_key: "1234567890abcdef1234567890abcdef"

# 推荐方式
datadog_api_key: "{{ vault_datadog_api_key }}"
datadog_app_key: "{{ vault_datadog_app_key }}"

# 或使用环境变量
datadog_api_key: "{{ lookup('env', 'DATADOG_API_KEY') }}"
datadog_app_key: "{{ lookup('env', 'DATADOG_APP_KEY') }}"
```

### 日志脱敏配置示例
```yaml
logs_config:
  processing_rules:
    - type: "exclude_at_match"
      name: "exclude_sensitive_data"
      pattern: "(password|secret|token|key)\\s*[:=]\\s*[\"']?[\\w-]+[\"']?"
```

## 依赖要求

- Ansible collection: `community.datadog`
- Python 库: `datadog`, `requests`
- Datadog Agent: 目标主机需要安装 Datadog Agent
- 网络权限：出站 HTTPS 连接到 Datadog API 端点

## 安装步骤

1. 安装 Ansible collection：
```bash
ansible-galaxy collection install community.datadog
```

2. 安装 Python 依赖：
```bash
pip install datadog requests
```

3. 获取 Datadog API Key 和 App Key
4. 配置网络防火墙允许 HTTPS 出站连接
5. 验证 API 连接和权限

## API 管理提示

### API Key 权限分级
- **只读 Key**: 仅用于查询和监控配置
- **读写 Key**: 用于创建和修改监控配置
- **管理员 Key**: 完全访问权限（谨慎使用）

### 站点选择
- `datadoghq.com`: 美国站点（默认）
- `datadoghq.eu`: 欧洲站点
- `us3.datadoghq.com`: 美国 3 号站点
- `ddog-gov.com`: 政府站点

### 速率限制
- API 调用频率限制：每分钟 500 次请求
- 批量操作优化：使用批量 API 端点
- 重试机制：实现指数退避重试策略

## 调试方法

- 使用 `--check` 模式验证配置变更
- 检查 Agent 状态：`datadog-agent status`
- 查看 Agent 日志：`tail -f /var/log/datadog/agent.log`
- 测试 API 连接：手动调用 Datadog API
- 验证指标发送：检查 Datadog UI 中的实时指标

## 最佳实践

1. **标签标准化**: 建立统一的标签命名规范
2. **监控分层**: 区分基础设施、应用和业务监控
3. **告警分级**: 设置合理的告警优先级和通知策略
4. **成本控制**: 监控自定义指标数量，避免超限费用
5. **合规要求**: 确保数据处理符合相关法规要求