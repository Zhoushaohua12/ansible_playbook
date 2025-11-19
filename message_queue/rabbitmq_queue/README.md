# RabbitMQ 队列管理

本模块提供 RabbitMQ 队列和交换机的自动化管理功能，支持创建队列、配置参数、绑定交换机和设置路由规则。

## 模块用途

- 创建和删除队列
- 配置队列参数（持久化、自动删除、TTL等）
- 创建和管理交换机
- 绑定队列到交换机
- 配置死信队列和延迟队列

## 主要参数

### 队列参数
- `name`: 队列名称（必需）
- `vhost`: 虚拟主机（默认：`/`）
- `durable`: 是否持久化（默认：`true`）
- `auto_delete`: 是否自动删除（默认：`false`）
- `arguments`: 队列参数（TTL、最大长度等）

### 交换机参数
- `name`: 交换机名称
- `type`: 交换机类型（`direct`, `fanout`, `topic`, `headers`）
- `durable`: 是否持久化
- `auto_delete`: 是否自动删除

### 绑定参数
- `source`: 源交换机
- `destination`: 目标队列或交换机
- `routing_key`: 路由键
- `arguments`: 绑定参数

## 返回值

- `changed`: 配置是否发生变更
- `msg`: 操作结果信息
- `queue`: 队列信息
- `exchange`: 交换机信息

## 常见使用场景

### 1. 创建基础队列
```yaml
- name: 创建工作队列
  community.rabbitmq.rabbitmq_queue:
    name: "app.tasks"
    vhost: "/app"
    durable: true
    auto_delete: false
    state: present
```

### 2. 创建延迟队列
```yaml
- name: 创建延迟队列
  community.rabbitmq.rabbitmq_queue:
    name: "app.delayed"
    vhost: "/app"
    arguments:
      x-message-ttl: 60000  # 60秒
      x-dead-letter-exchange: "app.dlx"
      x-dead-letter-routing-key: "app.tasks"
```

### 3. 创建交换机并绑定
```yaml
- name: 创建 Topic 交换机
  community.rabbitmq.rabbitmq_exchange:
    name: "app.logs"
    type: topic
    vhost: "/app"
    durable: true

- name: 绑定队列到交换机
  community.rabbitmq.rabbitmq_binding:
    name: "app.logs"
    destination: "app.error_logs"
    destination_type: queue
    routing_key: "error.*"
    vhost: "/app"
```

## 安全提示

### ⚠️ 敏感信息处理

1. **访问控制**
   - 使用虚拟主机隔离不同应用
   - 配置用户权限限制队列访问
   - 使用 Ansible Vault 加密管理员凭证

2. **队列安全**
   - 避免公开暴露队列名称
   - 使用命名约定标识敏感队列
   - 配置队列长度限制防止内存耗尽
   - 启用持久化保护重要消息

3. **消息安全**
   - 敏感消息应用层加密
   - 使用 SSL/TLS 保护传输
   - 配置消息 TTL 自动清理

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

## 队列参数说明

### 常用参数
- `x-message-ttl`: 消息TTL（毫秒）
- `x-expires`: 队列过期时间（毫秒）
- `x-max-length`: 最大队列长度
- `x-max-length-bytes`: 最大队列字节数
- `x-dead-letter-exchange`: 死信交换机
- `x-dead-letter-routing-key`: 死信路由键
- `x-max-priority`: 最大优先级
- `x-queue-mode`: 队列模式（`default`或`lazy`）

## 交换机类型

- **direct**: 精确匹配路由键
- **fanout**: 广播到所有绑定队列
- **topic**: 模式匹配路由键（`*`匹配一个词，`#`匹配零个或多个词）
- **headers**: 根据消息头匹配

## 最佳实践

1. **命名规范**: 使用清晰的命名约定（如：`app.service.queue`）
2. **持久化**: 重要队列启用持久化
3. **资源限制**: 配置队列长度和TTL
4. **死信队列**: 配置DLQ处理失败消息
5. **监控**: 监控队列深度和消费速率
