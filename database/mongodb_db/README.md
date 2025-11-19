# mongodb_db 模块使用指南

## 模块用途
`community.mongodb.mongodb_db` 模块用于管理 MongoDB 数据库的创建和删除。适用于应用部署、开发环境搭建、数据库初始化等场景。该模块可以配合 `community.mongodb.mongodb_user` 一起使用，实现完整的数据库和用户管理流程。

## 主要参数

### 连接参数
- `login_host`：MongoDB 服务器地址（默认 localhost）
- `login_port`：MongoDB 服务器端口（默认 27017）
- `login_user`：管理员用户名（用于连接和执行操作）
- `login_password`：管理员密码（建议使用 Ansible Vault 加密）
- `login_database`：用于身份验证的数据库（默认 admin）
- `ssl`：是否使用 SSL 连接（true/false）
- `ssl_cert_reqs`：SSL 证书验证要求（CERT_REQUIRED、CERT_OPTIONAL、CERT_NONE）

### 数据库管理参数
- `name`：要创建或删除的数据库名称（必需）
- `state`：数据库状态（present 创建，absent 删除）

### 副本集参数
- `replica_set`：副本集名称（连接到副本集时使用）

### 认证参数
- `auth_mechanism`：认证机制（SCRAM-SHA-1、SCRAM-SHA-256、MONGODB-CR 等）

## 返回值
- `changed`：数据库是否发生变更
- `db`：被管理的数据库名称

## 常见字段说明
- `state` 状态值：
  - `present` - 确保数据库存在（不存在则创建）
  - `absent` - 确保数据库不存在（存在则删除）

- `login_database` 认证数据库：
  - 默认为 `admin`，这是 MongoDB 管理员用户的认证数据库
  - 如果使用非管理员用户，可能需要指定其他认证数据库

## 适用场景

### 应用部署场景
- 为新应用创建专用 MongoDB 数据库
- 多租户应用为每个租户创建独立数据库
- 开发环境快速初始化数据库

### 开发测试场景
- CI/CD 流水线中创建临时测试数据库
- 集成测试前自动创建和清理数据库
- 开发人员本地环境数据库初始化

### 数据库维护场景
- 删除废弃的数据库释放存储空间
- 数据库重命名（先创建新库，迁移数据，删除旧库）
- 备份前创建临时数据库

## 安全注意事项

### 凭证安全
1. **禁止硬编码密码**：使用 Ansible Vault 加密 `login_password` 参数
2. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志文件
3. **启用认证**：MongoDB 生产环境必须启用 `--auth` 认证
4. **最小权限**：管理数据库的用户应具有 `dbAdminAnyDatabase` 或对应数据库的 `dbAdmin` 角色

### 数据安全
1. **删除前备份**：删除数据库前务必先备份数据
2. **使用 check_mode**：删除操作前使用 `--check` 预览变更
3. **权限控制**：创建数据库后立即配置访问权限和用户
4. **审计日志**：启用 MongoDB 审计功能记录数据库操作

### 连接安全
1. **使用 SSL/TLS**：生产环境启用 SSL 加密连接
2. **绑定地址**：配置 `bindIp` 限制 MongoDB 监听地址
3. **防火墙规则**：配合系统防火墙限制 27017 端口访问
4. **副本集认证**：副本集环境配置 keyFile 认证

### 操作审计
1. **版本控制**：将数据库管理 playbook 纳入 Git 管理
2. **变更记录**：在 playbook 中添加详细的任务名称和注释
3. **审批流程**：生产环境数据库删除操作应经过审批

## 最佳实践

### 创建数据库示例
```yaml
- name: 创建应用数据库
  community.mongodb.mongodb_db:
    login_host: localhost
    login_user: admin
    login_password: "{{ mongodb_admin_password }}"
    login_database: admin
    name: webapp_db
    state: present
  no_log: true
```

### 创建多个数据库示例
```yaml
- name: 批量创建应用数据库
  community.mongodb.mongodb_db:
    login_host: localhost
    login_user: admin
    login_password: "{{ mongodb_admin_password }}"
    login_database: admin
    name: "{{ item }}"
    state: present
  loop:
    - webapp_db
    - analytics_db
    - logs_db
  no_log: true
```

### SSL 连接示例
```yaml
- name: 使用 SSL 创建数据库
  community.mongodb.mongodb_db:
    login_host: mongodb.example.com
    login_user: admin
    login_password: "{{ mongodb_admin_password }}"
    login_database: admin
    name: secure_db
    ssl: true
    ssl_cert_reqs: CERT_REQUIRED
    state: present
  no_log: true
```

### 删除数据库示例（谨慎操作）
```yaml
- name: 删除测试数据库
  community.mongodb.mongodb_db:
    login_host: localhost
    login_user: admin
    login_password: "{{ mongodb_admin_password }}"
    login_database: admin
    name: test_db
    state: absent
  no_log: true
  when: 
    - environment == "development"
    - confirm_delete | default(false) | bool
```

### 副本集环境示例
```yaml
- name: 在副本集中创建数据库
  community.mongodb.mongodb_db:
    login_host: mongo1.example.com
    login_user: admin
    login_password: "{{ mongodb_admin_password }}"
    login_database: admin
    replica_set: "rs0"
    name: replicated_db
    state: present
  no_log: true
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置数据库连接信息和数据库名称
2. 使用 `--check` 模式预览数据库创建操作
3. 执行 playbook 创建数据库
4. 使用 `mongo` 或 `mongosh` 命令验证：`show dbs` 和 `use database_name`
5. 验证数据库访问权限

## 常见问题
- **连接失败**：检查 `login_host`、`login_port` 和防火墙规则
- **认证失败**：确认 `login_user` 和 `login_password` 正确，检查 `login_database`
- **权限不足**：确认管理用户具有 `dbAdminAnyDatabase` 或 `root` 角色
- **数据库未创建**：MongoDB 会在第一次写入数据时才物理创建数据库，可配合 collection 创建
- **无法删除**：检查是否有其他连接正在使用该数据库

## 依赖说明
- **Ansible Collection**: `community.mongodb`（使用 `ansible-galaxy collection install community.mongodb` 安装）
- **Python 库**: pymongo（在目标主机或控制节点安装：`pip install pymongo`）
- **数据库权限**: 管理用户需要 `dbAdminAnyDatabase` 或 `root` 角色
- **MongoDB 版本**: 建议 MongoDB 3.6 或更高版本

## 相关示例
- [mongodb_user 模块](../mongodb_user/README.md) - MongoDB 用户管理
- [mysql_db 模块](../mysql_db/README.md) - MySQL 数据库管理
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
- [监控模块](../../monitoring/README.md) - 配合数据库监控使用
