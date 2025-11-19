# Splunk 日志管理集成

本模块提供 Splunk 企业级日志聚合和分析平台的自动化配置功能，支持日志转发、索引管理、数据输入配置和 API 集成。

## 模块用途

- 自动部署和配置 Splunk Universal Forwarder
- 管理日志输入和数据源
- 配置日志转发和索引策略
- 设置搜索和告警规则
- 管理 HEC (HTTP Event Collector) 端点
- 配置数据安全和访问控制

## 主要参数

### 连接参数
- `splunk_url`: Splunk 管理端点 URL（默认：`https://localhost:8089`）
- `splunk_username`: Splunk 管理员用户名
- `splunk_password`: Splunk 管理员密码
- `splunk_hec_token`: HEC Token（用于 HTTP 事件收集）
- `splunk_verify_ssl`: 是否验证 SSL 证书（默认：`true`）

### Forwarder 配置参数
- `splunk_forwarder_url`: 日志转发目标地址
- `splunk_deployment_server`: 部署服务器地址
- `splunk_forward_server_list`: 索引器列表
- `splunk_tcp_out_port`: TCP 输出端口（默认：`9997`）

### 数据输入参数
- `splunk_monitor_paths`: 监控的日志文件路径列表
- `splunk_sourcetype`: 源类型标识
- `splunk_index`: 目标索引名称
- `splunk_source`: 数据源标识
- `splunk_host`: 主机标识（默认：主机名）

### HEC 参数
- `splunk_hec_port`: HEC 端口（默认：`8088`）
- `splunk_hec_ssl`: 是否启用 SSL（默认：`true`）
- `splunk_hec_token`: HEC 认证 Token
- `splunk_hec_indexes`: 允许的索引列表

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `forwarder_status`: Forwarder 安装和配置状态
- `input_status`: 数据输入配置状态
- `hec_status`: HEC 配置状态

## 常见使用场景

### 1. 配置 Universal Forwarder
```yaml
- name: 安装和配置 Splunk Universal Forwarder
  community.general.splunk_forwarder:
    state: present
    forward_server: "splunk-indexer.example.com:9997"
    deployment_server: "splunk-deployment.example.com:8089"
```

### 2. 配置日志监控
```yaml
- name: 配置应用日志监控
  community.general.splunk_data_input_monitor:
    name: "/var/log/nginx/*.log"
    state: present
    index: "web_logs"
    sourcetype: "nginx_access"
    host: "{{ inventory_hostname }}"
```

### 3. 配置 HEC Token
```yaml
- name: 创建 HEC Token
  uri:
    url: "{{ splunk_url }}/services/data/inputs/http"
    method: POST
    user: "{{ splunk_username }}"
    password: "{{ splunk_password }}"
    body_format: form-urlencoded
    body:
      name: "app_hec_token"
      index: "application_logs"
      sourcetype: "json"
    status_code: [201, 409]
  no_log: true  # 保护密码
```

### 4. 配置搜索和告警
```yaml
- name: 创建实时告警
  uri:
    url: "{{ splunk_url }}/services/saved/searches"
    method: POST
    user: "{{ splunk_username }}"
    password: "{{ splunk_password }}"
    body_format: form-urlencoded
    body:
      name: "High Error Rate Alert"
      search: 'index=app_logs level=ERROR | stats count by host | where count > 100'
      is_scheduled: "1"
      cron_schedule: "*/5 * * * *"
      actions: "email"
      action.email.to: "ops@example.com"
    status_code: [201, 409]
  no_log: true
```

## 安全提示

### ⚠️ 敏感信息处理

1. **API 凭证管理**
   - 使用 Ansible Vault 加密 `splunk_username` 和 `splunk_password`
   - HEC Token 必须加密存储
   - 定期轮换管理员密码和 HEC Token
   - 使用角色限制 API 访问权限
   - 启用双因素认证（2FA）

2. **日志数据安全**
   - 配置日志脱敏规则，过滤敏感信息
   - 使用 SSL/TLS 加密日志传输
   - 限制索引访问权限，实施基于角色的访问控制
   - 配置数据保留策略，及时清理过期日志
   - 审计日志访问和搜索操作

3. **网络安全**
   - 限制 Splunk 管理端口（8089）访问
   - 使用防火墙规则保护 HEC 端口（8088）
   - 配置 IP 白名单限制 Forwarder 连接
   - 启用 SSL 证书验证
   - 使用 VPN 或专用网络传输日志

### 变量占位符示例
```yaml
# 不要这样写！
splunk_username: "admin"
splunk_password: "changeme123"
splunk_hec_token: "abcd1234-5678-90ef-ghij-klmnopqrstuv"

# 推荐方式
splunk_username: "{{ vault_splunk_username }}"
splunk_password: "{{ vault_splunk_password }}"
splunk_hec_token: "{{ vault_splunk_hec_token }}"

# 或使用环境变量
splunk_username: "{{ lookup('env', 'SPLUNK_USERNAME') }}"
splunk_password: "{{ lookup('env', 'SPLUNK_PASSWORD') }}"
splunk_hec_token: "{{ lookup('env', 'SPLUNK_HEC_TOKEN') }}"
```

### 日志脱敏配置示例
```yaml
# props.conf 配置
[access_logs]
SEDCMD-mask_passwords = s/(password|passwd|pwd)=\S+/\1=***MASKED***/g
SEDCMD-mask_tokens = s/(token|api_key):\s*"[^"]+"/\1: "***MASKED***"/g
SEDCMD-mask_credit_cards = s/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/****-****-****-****/g
```

## 依赖要求

- Ansible collection: `community.general` (splunk 相关模块)
- Python 库: `requests`, `splunk-sdk`
- Splunk Universal Forwarder: 目标主机需要安装
- Splunk Enterprise/Cloud: 需要可访问的 Splunk 实例
- 网络权限：访问 Splunk 管理端口（8089）和 HEC 端口（8088）

## 安装步骤

1. 安装 Ansible collection：
```bash
ansible-galaxy collection install community.general
```

2. 安装 Python 依赖：
```bash
pip install requests splunk-sdk
```

3. 安装 Splunk Universal Forwarder：
```bash
# Ubuntu/Debian
wget -O splunkforwarder.deb "https://download.splunk.com/products/universalforwarder/..."
dpkg -i splunkforwarder.deb

# RHEL/CentOS
wget -O splunkforwarder.rpm "https://download.splunk.com/products/universalforwarder/..."
rpm -i splunkforwarder.rpm
```

4. 配置防火墙允许 Forwarder 连接（9997 端口）
5. 验证 Forwarder 与 Indexer 连接
6. 配置 HEC 并获取 Token

## 数据输入类型

### 文件和目录监控
```yaml
# 监控日志文件
[monitor:///var/log/nginx/access.log]
index = web_logs
sourcetype = nginx_access
disabled = false
```

### TCP/UDP 输入
```yaml
# TCP 输入
[tcp://9514]
index = syslog
sourcetype = syslog
connection_host = ip
```

### HTTP Event Collector (HEC)
```yaml
# 应用程序通过 HTTP 发送日志
curl -k https://splunk.example.com:8088/services/collector \
  -H "Authorization: Splunk $HEC_TOKEN" \
  -d '{"event": "hello world", "sourcetype": "manual"}'
```

### 脚本输入
```yaml
# 执行脚本并收集输出
[script:///opt/splunk/bin/scripts/system_metrics.sh]
index = metrics
sourcetype = system_metrics
interval = 60
```

## 索引管理

### 索引配置示例
```yaml
# indexes.conf
[application_logs]
homePath = $SPLUNK_DB/application_logs/db
coldPath = $SPLUNK_DB/application_logs/colddb
thawedPath = $SPLUNK_DB/application_logs/thaweddb
maxTotalDataSizeMB = 50000
frozenTimePeriodInSecs = 2592000  # 30 天
```

### 索引策略
- **热/温/冷数据分层**: 根据数据访问频率分配存储
- **数据保留期**: 设置合理的保留时间
- **索引大小限制**: 避免单个索引过大
- **搜索优化**: 使用摘要索引加速常用搜索

## 转发配置

### Outputs.conf 示例
```yaml
[tcpout]
defaultGroup = primary_indexers
forwardedindex.filter.disable = true
indexAndForward = false

[tcpout:primary_indexers]
server = indexer1.example.com:9997, indexer2.example.com:9997
sslPassword = $7$encrypted_password
sslVerifyServerCert = true
compressed = true
```

### 负载均衡
- **轮询**: 在多个索引器间平均分配
- **自动负载均衡**: 根据索引器负载动态调整
- **故障转移**: 主索引器不可用时自动切换

## 调试方法

- 检查 Forwarder 状态：`/opt/splunkforwarder/bin/splunk status`
- 查看转发队列：`/opt/splunkforwarder/bin/splunk list forward-server`
- 检查内部日志：`/opt/splunkforwarder/var/log/splunk/splunkd.log`
- 验证 HEC 连接：使用 curl 测试 HEC 端点
- 搜索测试事件：在 Splunk UI 中搜索 `index=_internal`
- 监控数据流量：在 Splunk UI 查看 Forwarding 页面
- 诊断连接问题：`/opt/splunkforwarder/bin/splunk btool outputs list --debug`

## 最佳实践

1. **部署架构**: 使用 Deployment Server 集中管理 Forwarder 配置
2. **索引策略**: 合理规划索引，避免使用默认索引
3. **数据分类**: 按应用、环境、日志类型划分索引
4. **性能优化**: 配置合理的监控间隔和批量大小
5. **高可用**: 配置多个索引器实现负载均衡和故障转移
6. **安全加固**: 启用 SSL、认证和访问控制
7. **监控告警**: 监控 Forwarder 状态和数据流量
8. **容量规划**: 根据日志量规划存储和索引器资源
9. **数据质量**: 配置正确的 sourcetype 和时间戳解析
10. **成本控制**: 监控索引大小和许可证使用量

## HEC 使用指南

### HEC 配置
```yaml
# inputs.conf
[http://app_logs]
disabled = 0
token = abcd1234-5678-90ef-ghij-klmnopqrstuv
index = application_logs
indexes = application_logs, app_errors
sourcetype = json
```

### HEC 客户端示例
```python
import requests
import json

splunk_url = "https://splunk.example.com:8088/services/collector"
hec_token = "your-hec-token-here"

event = {
    "event": {
        "message": "Application started",
        "level": "INFO"
    },
    "sourcetype": "app:log",
    "index": "application_logs",
    "host": "app-server-01"
}

headers = {
    "Authorization": f"Splunk {hec_token}",
    "Content-Type": "application/json"
}

response = requests.post(splunk_url, headers=headers, data=json.dumps(event), verify=False)
print(response.json())
```

## 性能考虑

### Forwarder 优化
- **队列大小**: 调整 `maxQueueSize` 避免数据丢失
- **压缩**: 启用数据压缩减少网络带宽
- **批量发送**: 配置合理的 `autoLBFrequency`
- **监控间隔**: 避免过于频繁的文件扫描

### 网络优化
- **带宽规划**: 估算日志量和网络带宽需求
- **连接复用**: 使用持久连接减少开销
- **SSL 性能**: 平衡安全性和性能需求
