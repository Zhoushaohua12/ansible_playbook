# Prometheus 监控集成

本模块提供 Prometheus 开源监控系统的自动化配置功能，支持指标抓取、服务发现、告警规则配置和多目标监控。

## 模块用途

- 自动部署和配置 Prometheus Server
- 管理监控目标（targets）和服务发现
- 配置指标抓取（scrape）规则
- 设置告警规则和 Alertmanager 集成
- 管理数据持久化和存储策略
- 配置远程存储和联邦集群

## 主要参数

### 连接参数
- `prometheus_url`: Prometheus API 端点 URL（默认：`http://localhost:9090`）
- `prometheus_api_token`: API 认证 Token（可选）
- `prometheus_basic_auth_user`: HTTP Basic 认证用户名
- `prometheus_basic_auth_password`: HTTP Basic 认证密码

### 配置参数
- `prometheus_config_file`: 配置文件路径（默认：`/etc/prometheus/prometheus.yml`）
- `prometheus_storage_path`: 数据存储路径（默认：`/var/lib/prometheus`）
- `prometheus_retention_time`: 数据保留时间（如：`15d`）
- `prometheus_retention_size`: 数据保留大小（如：`50GB`）

### 抓取配置参数
- `scrape_interval`: 全局抓取间隔（默认：`15s`）
- `scrape_timeout`: 抓取超时时间（默认：`10s`）
- `evaluation_interval`: 规则评估间隔（默认：`15s`）
- `targets`: 监控目标列表
- `labels`: 附加标签配置

### 告警参数
- `alertmanager_urls`: Alertmanager 端点列表
- `alert_relabel_configs`: 告警标签重写规则
- `rule_files`: 告警规则文件路径列表

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `prometheus_status`: Prometheus 服务状态
- `config_valid`: 配置文件验证结果
- `targets_status`: 监控目标健康状态

## 常见使用场景

### 1. 基础设施监控
```yaml
- name: 配置 Node Exporter 监控
  community.prometheus.prometheus_target:
    targets:
      - "{{ inventory_hostname }}:9100"
    labels:
      job: "node"
      env: "production"
```

### 2. 服务发现配置
```yaml
- name: 配置 Kubernetes 服务发现
  community.prometheus.prometheus_config:
    service_discovery:
      - type: "kubernetes_sd"
        role: "pod"
        namespaces:
          names: ["production", "staging"]
```

### 3. 告警规则管理
```yaml
- name: 配置 CPU 告警规则
  community.prometheus.prometheus_alert_rule:
    name: "HighCPUUsage"
    expr: "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100) > 80"
    for_duration: "5m"
    labels:
      severity: "warning"
    annotations:
      summary: "主机 CPU 使用率过高"
      description: "实例 {{ $labels.instance }} CPU 使用率为 {{ $value }}%"
```

### 4. 远程存储配置
```yaml
- name: 配置远程写入存储
  community.prometheus.prometheus_remote_storage:
    url: "https://remote-storage.example.com/api/v1/write"
    basic_auth:
      username: "{{ prometheus_remote_user }}"
      password: "{{ prometheus_remote_password }}"
    queue_config:
      capacity: 10000
      max_samples_per_send: 500
```

## 安全提示

### ⚠️ 敏感信息处理

1. **API 认证管理**
   - 使用 Ansible Vault 加密 `prometheus_api_token`、`prometheus_basic_auth_password`
   - 配置文件中的认证信息应使用 Vault 变量引用
   - 限制 API 访问权限，仅允许必要的 IP 地址
   - 使用 TLS 加密 Prometheus API 通信

2. **监控数据安全**
   - 配置网络隔离，限制 Prometheus 端口访问
   - 使用防火墙规则保护 9090 端口
   - 敏感指标数据应脱敏或限制访问
   - 定期审计监控目标和配置变更

3. **远程存储凭证**
   - 远程存储的认证信息必须加密存储
   - 使用独立的服务账号，限制权限范围
   - 定期轮换远程存储凭证
   - 监控凭证过期和访问失败情况

### 变量占位符示例
```yaml
# 不要这样写！
prometheus_basic_auth_password: "mypassword123"
prometheus_api_token: "Bearer abc123def456"

# 推荐方式
prometheus_basic_auth_password: "{{ vault_prometheus_password }}"
prometheus_api_token: "{{ vault_prometheus_api_token }}"

# 或使用环境变量
prometheus_basic_auth_password: "{{ lookup('env', 'PROMETHEUS_PASSWORD') }}"
prometheus_api_token: "{{ lookup('env', 'PROMETHEUS_API_TOKEN') }}"
```

### 配置文件保护示例
```yaml
- name: 配置 Prometheus 并保护敏感信息
  ansible.builtin.template:
    src: prometheus.yml.j2
    dest: /etc/prometheus/prometheus.yml
    owner: prometheus
    group: prometheus
    mode: '0640'  # 限制读取权限
  no_log: true  # 防止密码泄露到日志
  notify: reload prometheus
```

## 依赖要求

- Ansible collection: `community.prometheus`（可选，若使用专用模块）
- Python 库: `requests`, `pyyaml`
- Prometheus Server: 目标主机需要安装 Prometheus
- Exporters: Node Exporter, cAdvisor 等（根据监控需求）
- 网络权限：访问监控目标的抓取端口

## 安装步骤

1. 安装 Ansible collection（如可用）：
```bash
ansible-galaxy collection install community.prometheus
```

2. 安装 Python 依赖：
```bash
pip install requests pyyaml
```

3. 安装 Prometheus Server：
```bash
# Ubuntu/Debian
apt-get install prometheus

# RHEL/CentOS (使用官方二进制)
wget https://github.com/prometheus/prometheus/releases/download/v2.x.x/prometheus-2.x.x.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
```

4. 配置防火墙允许访问 Prometheus 端口（9090）
5. 验证 Prometheus API 可访问性

## 指标抓取配置

### 抓取配置结构
```yaml
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node'
    static_configs:
      - targets: 
          - 'server1.example.com:9100'
          - 'server2.example.com:9100'
        labels:
          env: 'production'
          datacenter: 'dc1'
```

### 服务发现类型
- **静态配置**: `static_configs`
- **文件发现**: `file_sd_configs`
- **DNS 发现**: `dns_sd_configs`
- **Kubernetes 发现**: `kubernetes_sd_configs`
- **Consul 发现**: `consul_sd_configs`
- **EC2 发现**: `ec2_sd_configs`

## 告警规则管理

### 告警规则格式
```yaml
groups:
  - name: node_alerts
    interval: 30s
    rules:
      - alert: NodeDown
        expr: up{job="node"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "节点 {{ $labels.instance }} 不可达"
          description: "节点已离线超过 5 分钟"
```

### 告警严重级别
- `critical`: 严重告警，需要立即处理
- `warning`: 警告告警，需要关注
- `info`: 信息告警，仅供参考

## 调试方法

- 验证配置文件语法：`promtool check config /etc/prometheus/prometheus.yml`
- 检查规则文件：`promtool check rules /etc/prometheus/rules/*.yml`
- 查看服务状态：`systemctl status prometheus`
- 检查 Prometheus 日志：`journalctl -u prometheus -f`
- 访问 Web UI：`http://prometheus-server:9090`
- 查看目标状态：访问 `/targets` 页面
- 测试 PromQL 查询：使用 Web UI 的查询功能

## 最佳实践

1. **监控分层**: 区分基础设施、应用和业务指标监控
2. **标签标准化**: 建立统一的标签命名规范（env, region, service）
3. **告警分级**: 设置合理的告警阈值和 for 持续时间
4. **数据保留**: 根据存储容量合理设置 retention 策略
5. **高可用部署**: 关键环境使用 Prometheus 联邦或 Thanos
6. **性能优化**: 控制抓取频率和目标数量，避免过载
7. **安全加固**: 启用 TLS、认证和网络隔离
8. **备份配置**: 定期备份 Prometheus 配置和告警规则

## 性能考虑

### 资源规划
- **时间序列数**: 每个监控目标约 1000-3000 个时间序列
- **内存需求**: 每百万活跃时间序列约需 1-2GB RAM
- **磁盘空间**: 根据保留时间和采样率计算（约 1-2 bytes/sample）
- **CPU**: 查询密集型场景需要更多 CPU 资源

### 优化建议
- 使用 `relabel_configs` 删除不需要的指标
- 调整 `scrape_interval` 避免过于频繁抓取
- 使用 `metric_relabel_configs` 删除高基数标签
- 配置合理的查询超时时间
