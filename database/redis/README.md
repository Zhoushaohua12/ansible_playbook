# redis 模块使用指南

## 模块用途
`community.general.redis` 和 `community.general.redis_data` 模块用于管理 Redis 键值存储系统。`redis` 模块用于管理 Redis 服务器配置，而 `redis_data` 模块用于管理 Redis 中的键值对数据。适用于缓存初始化、配置管理、数据预置等场景。

## 主要参数

### redis_data 模块参数

#### 连接参数
- `login_host`：Redis 服务器地址（默认 localhost）
- `login_port`：Redis 服务器端口（默认 6379）
- `login_password`：Redis 认证密码（建议使用 Ansible Vault 加密）
- `login_user`：Redis ACL 用户名（Redis 6.0+ 支持）
- `tls`：是否使用 TLS 连接（true/false）
- `validate_certs`：是否验证 TLS 证书（true/false）

#### 数据管理参数
- `key`：Redis 键名称（必需）
- `value`：键对应的值
- `state`：键状态（present 设置，absent 删除）
- `expiration`：键过期时间（秒）
- `existing_value`：仅当键值为指定值时才执行操作
- `non_existing`：仅当键不存在时才设置（类似 SETNX）

#### 数据库参数
- `db`：Redis 数据库编号（0-15，默认 0）

### redis 模块参数
- `command`：Redis 命令（config、save、slaveof、flush 等）
- `login_host`：Redis 服务器地址
- `login_port`：Redis 服务器端口
- `login_password`：Redis 认证密码

## 返回值
- `changed`：数据是否发生变更
- `key`：操作的键名称
- `value`：键的当前值
- `msg`：操作结果消息

## 常见字段说明
- `state` 状态值：
  - `present` - 设置键值对（存在则覆盖）
  - `absent` - 删除键

- `expiration` 过期时间：
  - 单位为秒
  - 设置为 -1 表示永不过期
  - 适用于会话缓存、临时数据等场景

- `non_existing` 条件设置：
  - 设置为 true 时，仅当键不存在时才设置值
  - 类似于 Redis 的 SETNX 命令
  - 用于分布式锁、唯一性保证等场景

## 适用场景

### 缓存管理场景
- 应用启动时预置缓存数据
- 批量设置配置参数到 Redis
- 清理过期或无效的缓存键

### 应用部署场景
- 初始化应用配置到 Redis
- 部署时设置功能开关和特性标志
- 预热常用数据缓存

### 运维管理场景
- 定期清理测试数据
- 设置全局配置参数
- 执行 SAVE 或 BGSAVE 持久化操作

### 分布式系统场景
- 设置分布式锁
- 管理会话存储
- 配置消息队列

## 安全注意事项

### 凭证安全
1. **禁止硬编码密码**：使用 Ansible Vault 加密 `login_password` 参数
2. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志文件
3. **启用 Redis 认证**：生产环境必须配置 `requirepass`
4. **使用 ACL**：Redis 6.0+ 推荐使用 ACL 进行细粒度权限控制

### 数据安全
1. **敏感数据加密**：存储敏感信息前先加密
2. **设置过期时间**：临时数据应设置 `expiration` 避免无限堆积
3. **备份策略**：配置 RDB 或 AOF 持久化机制
4. **数据隔离**：使用不同的 `db` 编号隔离不同应用数据

### 连接安全
1. **使用 TLS**：生产环境启用 `tls` 加密连接
2. **绑定地址**：配置 `bind` 限制 Redis 监听地址
3. **防火墙规则**：配合系统防火墙限制 6379 端口访问
4. **禁用危险命令**：使用 `rename-command` 禁用 FLUSHALL、KEYS 等命令

### 操作审计
1. **版本控制**：将 Redis 管理 playbook 纳入 Git 管理
2. **变更记录**：在 playbook 中添加详细的任务名称和注释
3. **使用 check_mode**：重要操作前先用 `--check` 预览变更

## 最佳实践

### 设置单个键值对示例
```yaml
- name: 设置应用配置参数
  community.general.redis_data:
    login_host: localhost
    login_password: "{{ redis_password }}"
    key: "app:config:max_connections"
    value: "1000"
    state: present
  no_log: true
```

### 批量设置键值对示例
```yaml
- name: 批量初始化应用配置
  community.general.redis_data:
    login_host: localhost
    login_password: "{{ redis_password }}"
    key: "{{ item.key }}"
    value: "{{ item.value }}"
    state: present
  loop:
    - { key: "app:feature:new_ui", value: "enabled" }
    - { key: "app:config:timeout", value: "30" }
    - { key: "app:config:retry", value: "3" }
  no_log: true
```

### 设置带过期时间的键示例
```yaml
- name: 设置会话缓存（1小时过期）
  community.general.redis_data:
    login_host: localhost
    login_password: "{{ redis_password }}"
    key: "session:{{ session_id }}"
    value: "{{ session_data }}"
    expiration: 3600
    state: present
  no_log: true
```

### 条件设置键（分布式锁）示例
```yaml
- name: 获取分布式锁
  community.general.redis_data:
    login_host: localhost
    login_password: "{{ redis_password }}"
    key: "lock:deployment"
    value: "{{ ansible_hostname }}"
    non_existing: true
    expiration: 300
    state: present
  no_log: true
  register: lock_result
```

### 删除键示例
```yaml
- name: 清理测试数据
  community.general.redis_data:
    login_host: localhost
    login_password: "{{ redis_password }}"
    key: "test:*"
    state: absent
  no_log: true
  when: environment == "development"
```

### 使用 TLS 连接示例
```yaml
- name: 通过 TLS 设置安全配置
  community.general.redis_data:
    login_host: redis.example.com
    login_password: "{{ redis_password }}"
    tls: true
    validate_certs: true
    key: "secure:config"
    value: "{{ secure_value }}"
    state: present
  no_log: true
```

### 使用 Redis ACL 用户示例
```yaml
- name: 使用 ACL 用户设置数据
  community.general.redis_data:
    login_host: localhost
    login_user: "app_user"
    login_password: "{{ app_user_password }}"
    key: "app:data:counter"
    value: "0"
    state: present
  no_log: true
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置 Redis 连接信息和键值对
2. 使用 `--check` 模式预览数据设置操作
3. 执行 playbook 设置键值对
4. 使用 `redis-cli` 命令验证：`GET key_name` 和 `TTL key_name`
5. 验证过期时间和数据持久化

## 常见问题
- **连接失败**：检查 `login_host`、`login_port` 和防火墙规则
- **认证失败**：确认 `login_password` 正确，检查 `requirepass` 配置
- **无法设置键**：确认用户权限，检查 Redis 内存是否充足
- **键未过期**：检查 `expiration` 参数，使用 `TTL` 命令验证
- **TLS 连接失败**：检查 Redis TLS 配置和证书路径

## 依赖说明
- **Ansible Collection**: `community.general`（使用 `ansible-galaxy collection install community.general` 安装）
- **Python 库**: redis 或 redis-py（在目标主机或控制节点安装：`pip install redis`）
- **Redis 版本**: 建议 Redis 5.0 或更高版本，ACL 功能需要 Redis 6.0+
- **Redis 配置**: 启用 `requirepass` 认证，配置持久化机制

## 相关示例
- [mongodb_db 模块](../mongodb_db/README.md) - MongoDB 数据库管理
- [mysql_db 模块](../mysql_db/README.md) - MySQL 数据库管理
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
- [监控模块](../../monitoring/README.md) - 配合 Redis 监控使用
