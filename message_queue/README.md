# 消息队列管理

本章节提供主流消息队列系统（RabbitMQ、Kafka）的 Ansible 自动化管理示例，涵盖用户管理、队列配置、Topic 管理等核心运维场景。

## 章节目标

- 掌握 RabbitMQ 用户、虚拟主机、队列和交换机的自动化管理
- 学习 Kafka Topic、分区和消费者组的配置方法
- 理解消息队列的权限控制和安全最佳实践
- 实现消息队列的监控和性能优化配置

## 模块列表

### RabbitMQ 管理
- **[rabbitmq_user](rabbitmq_user/README.md)**: RabbitMQ 用户管理，支持创建用户、配置权限、管理虚拟主机
- **[rabbitmq_queue](rabbitmq_queue/README.md)**: RabbitMQ 队列管理，支持创建队列、配置参数、绑定交换机

### Kafka 管理
- **[kafka_topic](kafka_topic/README.md)**: Kafka Topic 管理，支持创建 Topic、配置分区、副本和保留策略

## 前置条件

### RabbitMQ 依赖
- Ansible collection: `community.rabbitmq`
- Python 库: `requests`（用于 Management API）
- RabbitMQ Server: 需要安装并启动 RabbitMQ 服务
- RabbitMQ Management Plugin: 需要启用管理插件
- 网络权限: 访问 RabbitMQ Management API（默认端口 15672）

### Kafka 依赖
- Ansible collection: `community.general`（用于 Zookeeper）
- Python 库: `kafka-python`
- Kafka Broker: 需要安装并启动 Kafka 服务
- Zookeeper: Kafka 依赖 Zookeeper（或使用 KRaft 模式）
- 网络权限: 访问 Kafka Broker（默认端口 9092）和 Zookeeper（默认端口 2181）

## 安全最佳实践

### 认证与授权
1. **使用独立的管理凭证**: 不要使用默认 `guest` 用户
2. **最小权限原则**: 为应用分配最小必要权限
3. **Vault 加密**: 所有密码和凭证必须使用 Ansible Vault 加密
4. **定期轮换**: 定期更换管理员密码和应用凭证
5. **审计日志**: 启用审计日志记录所有管理操作

### 网络安全
1. **防火墙配置**: 限制消息队列端口访问
2. **SSL/TLS 加密**: 启用传输加密保护消息内容
3. **IP 白名单**: 限制允许连接的 IP 地址范围
4. **VPN 或专用网络**: 生产环境使用专用网络隔离
5. **端口隔离**: 管理端口与数据端口分离

### 数据安全
1. **消息加密**: 敏感消息在应用层加密
2. **访问控制**: 使用虚拟主机或命名空间隔离不同应用
3. **备份策略**: 定期备份队列配置和持久化消息
4. **监控告警**: 监控队列深度、消费速率和错误率
5. **资源限制**: 配置内存和磁盘限制避免资源耗尽

## 使用指南

### 快速开始

1. **安装依赖**:
```bash
# 安装 Ansible collections
ansible-galaxy collection install community.rabbitmq
ansible-galaxy collection install community.general

# 安装 Python 依赖
pip install requests kafka-python
```

2. **准备环境**:
```bash
# 启动 RabbitMQ（Docker 示例）
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=changeme \
  rabbitmq:3-management

# 启动 Kafka（Docker Compose 示例）
docker-compose up -d zookeeper kafka
```

3. **配置变量**:
```bash
# 复制示例变量文件
cp message_queue/rabbitmq_user/vars/example_vars.yml vars/rabbitmq_vars.yml

# 使用 Vault 加密敏感信息
ansible-vault encrypt_string 'admin_password' --name 'vault_rabbitmq_admin_password'
```

4. **运行 Playbook**:
```bash
# 检查模式运行
ansible-playbook message_queue/rabbitmq_user/playbook.yml --check

# 正式运行
ansible-playbook message_queue/rabbitmq_user/playbook.yml --ask-vault-pass
```

### 学习路径

1. **RabbitMQ 基础**:
   - 从 `rabbitmq_user` 开始，学习用户和权限管理
   - 进入 `rabbitmq_queue`，理解队列和交换机配置

2. **Kafka 基础**:
   - 学习 `kafka_topic`，掌握 Topic 和分区管理

3. **高级场景**:
   - 配置集群和高可用
   - 实施监控和性能优化
   - 设计消息路由和消费策略

## 常见场景

### RabbitMQ 应用场景
- **异步任务处理**: 使用工作队列处理后台任务
- **微服务通信**: 使用 Topic 交换机实现发布/订阅
- **日志聚合**: 使用 Fanout 交换机广播日志
- **延迟队列**: 使用 TTL 和死信队列实现延迟处理
- **优先级队列**: 根据消息优先级调度处理

### Kafka 应用场景
- **实时数据流**: 处理高吞吐量实时数据流
- **事件溯源**: 存储和重放应用事件
- **日志聚合**: 收集和分析分布式日志
- **流处理**: 使用 Kafka Streams 处理数据流
- **CDC (Change Data Capture)**: 捕获数据库变更

## 监控指标

### RabbitMQ 关键指标
- **队列深度**: 未消费消息数量
- **消费速率**: 每秒消费消息数
- **发布速率**: 每秒发布消息数
- **连接数**: 当前活跃连接数
- **内存使用**: 节点内存使用情况
- **磁盘空间**: 持久化消息占用空间

### Kafka 关键指标
- **Broker 延迟**: 消息生产和消费延迟
- **分区数**: Topic 分区数量
- **副本同步**: ISR (In-Sync Replicas) 状态
- **消费者滞后**: Consumer Lag
- **吞吐量**: 每秒消息字节数
- **磁盘使用**: 日志段存储空间

## 性能优化

### RabbitMQ 优化建议
1. **启用惰性队列**: 大量消息时减少内存压力
2. **调整预取计数**: 优化消费者性能
3. **使用多个队列**: 分散负载避免热点
4. **持久化策略**: 平衡可靠性和性能
5. **集群分片**: 使用分片插件分散负载

### Kafka 优化建议
1. **合理分区**: 根据并发需求设置分区数
2. **批量处理**: 调整 batch.size 和 linger.ms
3. **压缩策略**: 启用消息压缩节省带宽
4. **副本因子**: 平衡可靠性和资源消耗
5. **日志清理**: 配置合理的保留策略

## 故障排查

### RabbitMQ 常见问题
- **队列堵塞**: 检查消费者状态和消费速率
- **内存告警**: 调整内存限制或启用惰性队列
- **连接失败**: 检查防火墙和网络配置
- **消息丢失**: 确认持久化配置和发布确认
- **性能下降**: 分析慢查询和资源使用

### Kafka 常见问题
- **副本不同步**: 检查 ISR 状态和网络延迟
- **消费者滞后**: 增加分区或优化消费逻辑
- **磁盘满**: 调整保留策略或扩容存储
- **Rebalance 频繁**: 优化消费者配置
- **吞吐量低**: 调整批量大小和压缩策略

## 相关资源

### 官方文档
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Ansible community.rabbitmq Collection](https://docs.ansible.com/ansible/latest/collections/community/rabbitmq/)

### 最佳实践
- [RabbitMQ Best Practices](https://www.rabbitmq.com/best-practices.html)
- [Kafka Best Practices](https://kafka.apache.org/documentation/#operations)

### 监控工具
- RabbitMQ Management UI
- Prometheus + Grafana for RabbitMQ
- Kafka Manager / CMAK
- Burrow (Kafka Consumer Lag Monitoring)

## 注意事项

### RabbitMQ 注意事项
- ⚠️ 生产环境不要使用 `guest` 用户
- ⚠️ 启用管理插件会增加内存开销
- ⚠️ 持久化队列需要定期清理
- ⚠️ 集群部署需要考虑网络分区问题
- ⚠️ 消息优先级会影响性能

### Kafka 注意事项
- ⚠️ 分区数一旦创建不能减少
- ⚠️ Zookeeper 是单点故障需要集群部署
- ⚠️ 副本因子建议至少为 3
- ⚠️ 消息大小限制需要协调 Broker 和 Producer 配置
- ⚠️ 保留策略需要根据磁盘容量规划
