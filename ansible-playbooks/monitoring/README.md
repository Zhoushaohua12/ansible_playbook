# 监控系统 Ansible Playbooks

本目录包含用于部署监控系统的 Ansible playbooks，涵盖 Prometheus 监控栈和 ELK 日志分析栈的自动化部署。

## 📋 目录结构

```
monitoring/
├── prometheus-install.yml       # Prometheus 监控栈安装
├── elk-stack-install.yml        # ELK 栈安装配置
├── vars/
│   └── default.yml              # 默认变量配置
├── templates/
│   ├── prometheus.yml.j2       # Prometheus 主配置文件
│   ├── alertmanager.yml.j2      # AlertManager 配置文件
│   ├── alert_rules.yml.j2      # 告警规则文件
│   ├── elasticsearch.yml.j2    # Elasticsearch 配置文件
│   ├── logstash.yml.j2         # Logstash 主配置文件
│   ├── logstash.conf.j2        # Logstash 管道配置
│   ├── kibana.yml.j2           # Kibana 配置文件
│   ├── filebeat.yml.j2         # Filebeat 配置文件
│   └── ...                     # 其他配置模板
├── roles/
│   ├── prometheus/             # Prometheus 角色
│   │   ├── tasks/             # 任务文件
│   │   ├── templates/         # 模板文件
│   │   └── handlers/          # 处理程序
│   └── elk/                   # ELK 角色
│       ├── tasks/             # 任务文件
│       ├── templates/         # 模板文件
│       └── handlers/          # 处理程序
└── README.md                  # 本文档
```

## 🚀 快速开始

### 1. Prometheus 监控栈部署

```bash
# 语法检查
ansible-playbook --syntax-check prometheus-install.yml

# 干运行（检查模式）
ansible-playbook --check prometheus-install.yml

# 执行安装
ansible-playbook prometheus-install.yml

# 仅安装 Prometheus
ansible-playbook prometheus-install.yml --tags "prometheus"

# 仅安装 Node Exporter
ansible-playbook prometheus-install.yml --tags "node_exporter"

# 仅安装 AlertManager
ansible-playbook prometheus-install.yml --tags "alertmanager"
```

**功能特性：**
- Prometheus 2.45.0 监控系统
- Node Exporter 系统指标收集
- Blackbox Exporter 探测监控
- AlertManager 告警管理
- 丰富的告警规则
- 支持多种通知方式
- Web UI 界面
- 高可用配置支持

### 2. ELK 栈部署

```bash
# 语法检查
ansible-playbook --syntax-check elk-stack-install.yml

# 干运行
ansible-playbook --check elk-stack-install.yml

# 执行安装
ansible-playbook elk-stack-install.yml

# 仅安装 Elasticsearch
ansible-playbook elk-stack-install.yml --tags "elasticsearch"

# 仅安装 Logstash
ansible-playbook elk-stack-install.yml --tags "logstash"

# 仅安装 Kibana
ansible-playbook elk-stack-install.yml --tags "kibana"

# 仅安装 Filebeat
ansible-playbook elk-stack-install.yml --tags "filebeat"
```

**功能特性：**
- Elasticsearch 8.8.0 搜索引擎
- Logstash 8.8.0 日志处理
- Kibana 8.8.0 数据可视化
- Filebeat 8.8.0 日志收集
- 多种输入源支持
- 实时日志分析
- 仪表板和可视化
- 索引生命周期管理

## ⚙️ 配置说明

### 主要变量配置

编辑 `vars/default.yml` 文件来自定义监控配置：

```yaml
# Prometheus 配置
prometheus_version: "2.45.0"
prometheus_port: "9090"
prometheus_retention: "30d"

# AlertManager 配置
alertmanager_port: "9093"

# Node Exporter 配置
node_exporter_port: "9100"

# Blackbox Exporter 配置
blackbox_exporter_port: "9115"

# ELK 栈配置
elasticsearch_version: "8.8.0"
logstash_version: "8.8.0"
kibana_version: "8.8.0"
filebeat_version: "8.8.0"

# Elasticsearch 配置
elasticsearch_http_port: 9200
elasticsearch_cluster_name: "elk-cluster"

# Kibana 配置
kibana_port: 5601

# Logstash 配置
logstash_port: 5044
```

### 告警规则配置

Prometheus 包含丰富的预定义告警规则：

- **系统监控**：CPU、内存、磁盘、网络
- **服务监控**：实例宕机、服务异常
- **网络监控**：HTTP 探测、ICMP 探测、TCP 连接
- **Prometheus 监控**：配置重载、存储空间

### 日志收集配置

Filebeat 支持多种日志类型：

- **系统日志**：syslog、auth.log
- **Web 日志**：Nginx、Apache
- **应用日志**：JSON 格式、自定义格式
- **数据库日志**：MySQL、PostgreSQL

## 🖥️ 操作系统支持

| 操作系统 | 版本 | 支持状态 |
|---------|------|----------|
| Ubuntu | 20.04 LTS | ✅ 完全支持 |
| Ubuntu | 22.04 LTS | ✅ 完全支持 |
| Debian | 10 (Buster) | ✅ 完全支持 |
| Debian | 11 (Bullseye) | ✅ 完全支持 |
| CentOS | 7 | ⚠️ 部分支持 |
| CentOS | 8 | ⚠️ 部分支持 |

## 📦 依赖要求

### Ansible 要求
- Ansible >= 2.9
- Python >= 3.6

### Ansible Collections
```bash
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.mysql
ansible-galaxy collection install community.general
```

### 系统要求
- **最小内存**：4GB RAM（推荐 8GB）
- **磁盘空间**：50GB 可用空间（推荐 100GB）
- **网络**：互联网连接（用于软件包下载）
- **Java**：OpenJDK 11+（ELK 栈要求）

## 🏷️ 标签使用

所有 playbooks 都支持标签进行选择性执行：

| 标签 | 描述 |
|------|------|
| `prometheus` | Prometheus 相关任务 |
| `node_exporter` | Node Exporter 安装配置 |
| `blackbox_exporter` | Blackbox Exporter 安装配置 |
| `alertmanager` | AlertManager 安装配置 |
| `elasticsearch` | Elasticsearch 安装配置 |
| `logstash` | Logstash 安装配置 |
| `kibana` | Kibana 安装配置 |
| `filebeat` | Filebeat 安装配置 |
| `packages` | 软件包安装 |
| `config` | 配置文件部署 |
| `service` | 服务管理 |
| `verify` | 验证和测试 |
| `firewall` | 防火墙配置 |
| `java` | Java 环境配置 |
| `system` | 系统配置 |

## 🔧 故障排除

### 常见问题

1. **Prometheus 启动失败**
   ```bash
   # 检查配置文件语法
   /opt/prometheus/promtool check config /etc/prometheus/prometheus.yml
   
   # 检查服务状态
   systemctl status prometheus
   
   # 查看日志
   journalctl -u prometheus -f
   ```

2. **Elasticsearch 内存不足**
   ```bash
   # 检查 JVM 堆内存设置
   cat /etc/elasticsearch/jvm.options.d/custom.options
   
   # 调整内存限制
   echo "-Xms2g" >> /etc/elasticsearch/jvm.options.d/custom.options
   echo "-Xmx2g" >> /etc/elasticsearch/jvm.options.d/custom.options
   ```

3. **Logstash 处理缓慢**
   ```bash
   # 检查管道配置
   /usr/share/logstash/bin/logstash --config.test_and_exit -f /etc/logstash/conf.d/main.conf
   
   # 调整工作线程数
   echo "pipeline.workers: 4" >> /etc/logstash/logstash.yml
   ```

4. **Kibana 连接 Elasticsearch 失败**
   ```bash
   # 检查网络连接
   curl -X GET "localhost:9200/_cluster/health"
   
   # 验证配置文件
   /usr/share/kibana/bin/kibana --allow-root --config /etc/kibana/kibana.yml
   ```

### 调试技巧

```bash
# 详细输出模式
ansible-playbook prometheus-install.yml -vvv

# 仅在特定主机执行
ansible-playbook elk-stack-install.yml --limit elk01.example.com

# 跳过错误继续执行
ansible-playbook prometheus-install.yml --skip-tags "verify"

# 使用自定义变量文件
ansible-playbook elk-stack-install.yml -e @custom_vars.yml
```

## 📊 监控指标

### Prometheus 指标

- **系统指标**：CPU、内存、磁盘、网络使用率
- **服务指标**：服务可用性、响应时间、错误率
- **应用指标**：自定义业务指标
- **网络指标**：连通性、延迟、丢包率

### ELK 指标

- **日志量**：每日/每小时日志处理量
- **索引大小**：索引存储使用情况
- **查询性能**：搜索响应时间
- **节点状态**：集群健康状态

## 🔒 安全配置

### 访问控制

- 配置防火墙规则限制端口访问
- 启用 HTTPS/TLS 加密通信
- 设置用户认证和授权
- 定期更新安全补丁

### 数据保护

- 配置数据备份策略
- 启用数据加密
- 设置访问日志审计
- 实施网络隔离

## 📚 最佳实践

1. **监控配置**
   - 合理设置采集间隔和保留时间
   - 配置适当的告警阈值
   - 定期检查和维护监控指标
   - 建立监控数据备份机制

2. **日志管理**
   - 合理配置日志轮转策略
   - 设置索引生命周期管理
   - 优化日志解析和过滤规则
   - 建立日志归档机制

3. **性能优化**
   - 根据系统资源调整进程数和内存
   - 配置适当的缓存策略
   - 监控系统资源使用情况
   - 定期清理过期数据

4. **高可用性**
   - 配置集群模式部署
   - 设置负载均衡
   - 实施故障转移机制
   - 建立灾难恢复方案

## 📞 支持与反馈

如果遇到问题或有改进建议，请：

1. 检查日志文件获取详细错误信息
2. 参考本文档的故障排除部分
3. 在测试环境验证配置
4. 提交详细的问题报告

---

**⚠️ 重要提醒：** 本套 playbooks 主要用于教学和学习目的，在生产环境使用前请进行充分测试并根据实际需求调整配置。