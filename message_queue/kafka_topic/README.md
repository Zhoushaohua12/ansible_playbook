# Kafka Topic 管理

本模块提供 Apache Kafka Topic 的自动化管理功能，支持创建 Topic、配置分区、副本和保留策略。

## 模块用途

- 创建和删除 Kafka Topic
- 配置 Topic 分区数和副本因子
- 设置 Topic 配置参数（保留时间、压缩策略等）
- 管理 Topic 权限和 ACL

## 主要参数

### Topic 参数
- `name`: Topic 名称（必需）
- `partitions`: 分区数量
- `replication_factor`: 副本因子
- `state`: Topic 状态（`present` 或 `absent`）

### 配置参数
- `retention.ms`: 消息保留时间（毫秒）
- `retention.bytes`: 分区最大字节数
- `compression.type`: 压缩类型（`gzip`, `snappy`, `lz4`, `zstd`）
- `cleanup.policy`: 清理策略（`delete` 或 `compact`）
- `min.insync.replicas`: 最小同步副本数

### 连接参数
- `bootstrap_servers`: Kafka Broker 地址列表
- `api_version`: Kafka API 版本
- `security_protocol`: 安全协议（`PLAINTEXT`, `SSL`, `SASL_PLAINTEXT`, `SASL_SSL`）
- `sasl_mechanism`: SASL 机制
- `sasl_plain_username`: SASL 用户名
- `sasl_plain_password`: SASL 密码

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `topic`: Topic 信息

## 常见使用场景

### 1. 创建基础 Topic
```yaml
- name: 创建应用日志 Topic
  community.general.kafka_topic:
    name: "app-logs"
    partitions: 3
    replication_factor: 3
    bootstrap_servers: "kafka1:9092,kafka2:9092,kafka3:9092"
    state: present
```

### 2. 创建压缩 Topic
```yaml
- name: 创建用户状态 Topic（日志压缩）
  community.general.kafka_topic:
    name: "user-status"
    partitions: 6
    replication_factor: 3
    options:
      cleanup.policy: "compact"
      compression.type: "lz4"
    bootstrap_servers: "{{ kafka_bootstrap_servers }}"
```

### 3. 配置保留策略
```yaml
- name: 创建短期数据 Topic
  community.general.kafka_topic:
    name: "metrics"
    partitions: 12
    options:
      retention.ms: 86400000  # 1天
      retention.bytes: 10737418240  # 10GB
```

## 安全提示

### ⚠️ 敏感信息处理

1. **认证管理**
   - 使用 Ansible Vault 加密 SASL 凭证
   - 启用 SSL/TLS 加密传输
   - 使用 ACL 控制 Topic 访问权限
   - 定期轮换认证凭证

2. **Topic 安全**
   - 避免公开暴露 Topic 名称
   - 使用命名约定标识敏感数据
   - 配置 min.insync.replicas 保证数据可靠性
   - 启用日志加密保护敏感消息

3. **网络安全**
   - 限制 Broker 端口访问
   - 使用防火墙保护 Zookeeper
   - 配置 IP 白名单
   - 使用专用网络传输数据

### 变量占位符示例
```yaml
# 不要这样写！
kafka_sasl_username: "admin"
kafka_sasl_password: "admin-secret"

# 推荐方式
kafka_sasl_username: "{{ vault_kafka_sasl_username }}"
kafka_sasl_password: "{{ vault_kafka_sasl_password }}"
```

## 依赖要求

- Ansible collection: `community.general`
- Python 库: `kafka-python`
- Kafka Broker: 2.x 或 3.x 版本
- Zookeeper: 3.4+ 版本（或使用 KRaft 模式）

## 安装步骤

1. 安装 Ansible collection：
```bash
ansible-galaxy collection install community.general
```

2. 安装 Python 依赖：
```bash
pip install kafka-python
```

3. 安装 Kafka：
```bash
# 下载并解压
wget https://downloads.apache.org/kafka/3.x.x/kafka_2.13-3.x.x.tgz
tar -xzf kafka_2.13-3.x.x.tgz
cd kafka_2.13-3.x.x

# 启动 Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties &

# 启动 Kafka
bin/kafka-server-start.sh config/server.properties &
```

## Topic 配置说明

### 分区策略
- **低吞吐**: 1-3 个分区
- **中等吞吐**: 3-12 个分区
- **高吞吐**: 12+ 个分区
- **规则**: 分区数 >= 消费者数实现并行消费

### 副本因子
- **开发环境**: 1 个副本
- **测试环境**: 2 个副本
- **生产环境**: 3 个副本（推荐）

### 保留策略
- **时间**: retention.ms（默认 7 天）
- **空间**: retention.bytes（分区级别）
- **压缩**: cleanup.policy=compact（保留最新值）

## 最佳实践

1. **命名规范**: 使用清晰的命名约定（如：`service.event.version`）
2. **分区规划**: 根据吞吐量和并发度规划分区数
3. **副本配置**: 生产环境至少 3 个副本
4. **监控告警**: 监控 Consumer Lag 和 Broker 性能
5. **容量规划**: 根据消息量规划存储容量
6. **压缩策略**: 使用压缩节省存储和带宽
