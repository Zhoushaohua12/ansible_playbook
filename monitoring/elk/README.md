# ELK Stack 日志聚合集成

本模块提供 ELK (Elasticsearch, Logstash, Kibana) Stack 日志聚合和分析平台的自动化配置功能，支持日志收集、索引管理、可视化和告警。

## 模块用途

- 自动部署和配置 Filebeat/Logstash 日志收集器
- 管理 Elasticsearch 索引和索引生命周期策略
- 配置 Logstash Pipeline 和数据转换
- 设置 Kibana Dashboard 和可视化
- 管理 Elasticsearch 用户和角色权限
- 配置日志解析和过滤规则

## 主要参数

### Elasticsearch 连接参数
- `elasticsearch_hosts`: Elasticsearch 集群节点列表
- `elasticsearch_port`: Elasticsearch 端口（默认：`9200`）
- `elasticsearch_username`: Elasticsearch 用户名
- `elasticsearch_password`: Elasticsearch 密码
- `elasticsearch_api_key`: Elasticsearch API Key（可选）
- `elasticsearch_ca_cert`: CA 证书路径（SSL）

### Filebeat 配置参数
- `filebeat_config_file`: Filebeat 配置文件路径
- `filebeat_inputs`: 日志输入源配置列表
- `filebeat_modules`: 启用的 Filebeat 模块列表
- `filebeat_output_type`: 输出类型（elasticsearch, logstash）
- `filebeat_index_name`: 目标索引名称模式

### Logstash 配置参数
- `logstash_config_dir`: Logstash 配置目录
- `logstash_pipeline_config`: Pipeline 配置文件路径
- `logstash_input_beats_port`: Beats 输入端口（默认：`5044`）
- `logstash_filter_plugins`: 过滤插件配置
- `logstash_patterns_dir`: Grok 模式文件目录

### Kibana 配置参数
- `kibana_url`: Kibana 访问地址
- `kibana_elasticsearch_hosts`: Kibana 连接的 ES 节点
- `kibana_username`: Kibana 用户名
- `kibana_password`: Kibana 密码

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `filebeat_status`: Filebeat 服务状态
- `logstash_status`: Logstash 服务状态
- `elasticsearch_health`: Elasticsearch 集群健康状态
- `index_status`: 索引创建和管理状态

## 常见使用场景

### 1. 配置 Filebeat 日志收集
```yaml
- name: 配置 Filebeat 收集 Nginx 日志
  community.elastic.filebeat:
    inputs:
      - type: "log"
        enabled: true
        paths:
          - "/var/log/nginx/*.log"
        fields:
          log_type: "nginx"
          environment: "production"
```

### 2. 配置 Logstash Pipeline
```yaml
- name: 配置 Logstash 日志解析
  ansible.builtin.template:
    src: logstash-pipeline.conf.j2
    dest: /etc/logstash/conf.d/app-logs.conf
    content: |
      input {
        beats {
          port => 5044
        }
      }
      filter {
        grok {
          match => { "message" => "%{COMBINEDAPACHELOG}" }
        }
      }
      output {
        elasticsearch {
          hosts => ["http://localhost:9200"]
          index => "app-logs-%{+YYYY.MM.dd}"
        }
      }
```

### 3. 创建 Elasticsearch 索引模板
```yaml
- name: 创建日志索引模板
  community.elastic.elasticsearch_index_template:
    name: "app-logs"
    body:
      index_patterns: ["app-logs-*"]
      settings:
        number_of_shards: 3
        number_of_replicas: 1
      mappings:
        properties:
          timestamp:
            type: "date"
          level:
            type: "keyword"
          message:
            type: "text"
```

### 4. 配置索引生命周期策略
```yaml
- name: 配置 ILM 策略
  uri:
    url: "{{ elasticsearch_url }}/_ilm/policy/logs-policy"
    method: PUT
    user: "{{ elasticsearch_username }}"
    password: "{{ elasticsearch_password }}"
    body_format: json
    body:
      policy:
        phases:
          hot:
            actions:
              rollover:
                max_size: "50GB"
                max_age: "7d"
          warm:
            min_age: "7d"
            actions:
              forcemerge:
                max_num_segments: 1
          delete:
            min_age: "30d"
            actions:
              delete: {}
  no_log: true  # 保护凭证
```

## 安全提示

### ⚠️ 敏感信息处理

1. **Elasticsearch 认证管理**
   - 使用 Ansible Vault 加密 `elasticsearch_username` 和 `elasticsearch_password`
   - 优先使用 API Key 而非基本认证
   - 为不同应用创建独立的用户和角色
   - 启用 Elasticsearch 安全特性（X-Pack Security）
   - 使用 TLS/SSL 加密集群通信

2. **日志数据安全**
   - 配置字段级安全控制敏感数据访问
   - 使用 Logstash 过滤器脱敏敏感信息
   - 实施基于角色的访问控制（RBAC）
   - 加密静态数据（Encryption at Rest）
   - 审计日志访问和查询操作

3. **网络安全**
   - 限制 Elasticsearch 端口（9200）访问
   - 使用防火墙保护 Logstash Beats 端口（5044）
   - 配置 IP 白名单限制访问
   - 启用 SSL/TLS 加密所有连接
   - 使用 VPN 或专用网络传输日志

### 变量占位符示例
```yaml
# 不要这样写！
elasticsearch_password: "changeme123"
elasticsearch_api_key: "VnVhQ2ZHY0JDZGJrUW0tZTVhT3g6dWkybHAyYXhUTm1zeWFrdzl0dk5udw=="

# 推荐方式
elasticsearch_password: "{{ vault_elasticsearch_password }}"
elasticsearch_api_key: "{{ vault_elasticsearch_api_key }}"

# 或使用环境变量
elasticsearch_password: "{{ lookup('env', 'ELASTICSEARCH_PASSWORD') }}"
elasticsearch_api_key: "{{ lookup('env', 'ELASTICSEARCH_API_KEY') }}"
```

### Logstash 脱敏过滤器示例
```ruby
filter {
  # 脱敏密码
  mutate {
    gsub => [
      "message", "(password|passwd|pwd)=[^\s&]+", "\1=***MASKED***"
    ]
  }
  
  # 脱敏信用卡号
  mutate {
    gsub => [
      "message", "\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "****-****-****-****"
    ]
  }
  
  # 删除敏感字段
  mutate {
    remove_field => ["password", "secret_key", "api_token"]
  }
}
```

## 依赖要求

- Ansible collection: `community.elastic` (可选)
- Python 库: `elasticsearch`, `requests`
- Elasticsearch: 7.x 或 8.x 版本
- Logstash: 与 Elasticsearch 版本匹配
- Filebeat/Metricbeat: 与 Elasticsearch 版本匹配
- Kibana: 与 Elasticsearch 版本匹配
- Java: Logstash 和 Elasticsearch 依赖 Java 运行时

## 安装步骤

1. 安装 Ansible collection（如可用）：
```bash
ansible-galaxy collection install community.elastic
```

2. 安装 Python 依赖：
```bash
pip install elasticsearch requests
```

3. 安装 Elasticsearch：
```bash
# Ubuntu/Debian
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-8.x.list
apt-get update && apt-get install elasticsearch

# RHEL/CentOS
rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
cat <<EOF > /etc/yum.repos.d/elasticsearch.repo
[elasticsearch]
name=Elasticsearch repository for 8.x packages
baseurl=https://artifacts.elastic.co/packages/8.x/yum
gpgcheck=1
EOF
yum install elasticsearch
```

4. 安装 Filebeat 和 Logstash：
```bash
apt-get install filebeat logstash  # Ubuntu/Debian
yum install filebeat logstash      # RHEL/CentOS
```

5. 启动服务并设置自启动
6. 配置防火墙允许必要端口（9200, 5601, 5044）

## Filebeat 模块

### 常用模块
- `system`: 系统日志（syslog, auth.log）
- `nginx`: Nginx 访问和错误日志
- `apache`: Apache 访问和错误日志
- `mysql`: MySQL 错误和慢查询日志
- `redis`: Redis 日志
- `postgresql`: PostgreSQL 日志
- `docker`: Docker 容器日志
- `kubernetes`: Kubernetes 集群日志

### 启用模块
```bash
filebeat modules enable nginx
filebeat modules enable mysql
filebeat modules list
```

## Logstash Pipeline 配置

### 输入插件
- `beats`: 接收 Filebeat/Metricbeat 数据
- `file`: 读取文件
- `tcp`: TCP 输入
- `http`: HTTP/HTTPS 输入
- `kafka`: Kafka 消息队列
- `syslog`: Syslog 协议

### 过滤插件
- `grok`: 使用模式匹配解析文本
- `mutate`: 修改字段
- `date`: 解析时间戳
- `json`: 解析 JSON
- `geoip`: 地理位置解析
- `useragent`: User-Agent 解析

### 输出插件
- `elasticsearch`: 输出到 Elasticsearch
- `file`: 输出到文件
- `kafka`: 输出到 Kafka
- `stdout`: 控制台输出（调试）

## Elasticsearch 索引管理

### 索引模板
```json
{
  "index_patterns": ["logs-*"],
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index.refresh_interval": "5s"
  },
  "mappings": {
    "properties": {
      "@timestamp": {"type": "date"},
      "message": {"type": "text"},
      "level": {"type": "keyword"}
    }
  }
}
```

### 索引别名
```bash
# 创建别名
POST /_aliases
{
  "actions": [
    { "add": { "index": "logs-2024.01.01", "alias": "logs-current" }}
  ]
}
```

### ILM 生命周期管理
- **Hot Phase**: 活跃写入阶段
- **Warm Phase**: 只读优化阶段
- **Cold Phase**: 长期存储阶段
- **Delete Phase**: 删除过期数据

## 调试方法

- 验证 Filebeat 配置：`filebeat test config`
- 测试 Filebeat 输出：`filebeat test output`
- 检查 Logstash 配置：`/usr/share/logstash/bin/logstash --config.test_and_exit -f /etc/logstash/conf.d/`
- 查看 Elasticsearch 健康：`curl http://localhost:9200/_cluster/health?pretty`
- 查看索引列表：`curl http://localhost:9200/_cat/indices?v`
- Logstash 日志：`tail -f /var/log/logstash/logstash-plain.log`
- Filebeat 日志：`journalctl -u filebeat -f`
- Kibana 开发工具：使用 Dev Tools 测试查询

## 最佳实践

1. **索引设计**: 使用时间序列索引模式（logs-YYYY.MM.dd）
2. **分片策略**: 根据数据量合理设置分片数量
3. **副本配置**: 生产环境至少配置 1 个副本
4. **ILM 策略**: 配置索引生命周期自动管理
5. **监控告警**: 监控集群健康、索引大小和性能指标
6. **数据脱敏**: 在 Logstash 中过滤敏感信息
7. **访问控制**: 使用 RBAC 限制用户权限
8. **备份策略**: 定期快照备份重要数据
9. **性能优化**: 优化查询、使用聚合缓存
10. **容量规划**: 根据日志量规划存储和节点资源

## 性能考虑

### Elasticsearch 优化
- **堆内存**: 设置为物理内存的 50%，不超过 31GB
- **刷新间隔**: 延长 refresh_interval 提高写入性能
- **批量操作**: 使用 bulk API 批量写入
- **段合并**: 配置合理的段合并策略
- **查询缓存**: 启用和优化查询缓存

### Logstash 优化
- **工作线程**: 调整 pipeline.workers 数量
- **批量大小**: 优化 pipeline.batch.size
- **队列类型**: 使用持久化队列避免数据丢失
- **过滤器优化**: 减少不必要的过滤操作

### Filebeat 优化
- **批量发送**: 配置合理的 bulk_max_size
- **队列大小**: 调整内存队列大小
- **多行合并**: 合理配置多行日志处理
- **扫描频率**: 优化日志文件扫描频率
