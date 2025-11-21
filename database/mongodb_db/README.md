# MongoDB 数据库管理模块使用指南

## 模块用途
`community.mongodb.mongodb_db` 模块用于管理 MongoDB 数据库，支持创建、删除数据库等操作。适用于应用部署、数据库初始化、环境清理等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `name` | str | 数据库名称（必需） | `mydb`、`app_database` 等 |
| `state` | str | 数据库状态（present 创建，absent 删除） | present、absent |
| `login_host` | str | MongoDB 主机 | `localhost`、`127.0.0.1` |
| `login_port` | int | MongoDB 端口 | 27017 |
| `login_user` | str | 登录用户 | `admin`、管理员用户 |
| `login_password` | str | 登录密码 | 密码字符串 |
| `login_database` | str | 认证数据库 | `admin` |

## 高级参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `ssl` | bool | 是否使用 SSL 连接 | true、false |
| `ssl_cert_reqs` | str | SSL 证书要求 | `CERT_NONE`、`CERT_REQUIRED` |
| `replica_set` | str | 副本集名称 | `rs0`、`replica_set_name` |
| `auth_mechanism` | str | 认证机制 | `SCRAM-SHA-1`、`SCRAM-SHA-256` |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了修改 | true/false |
| `db` | 数据库名称 | mydb |

## 使用情境

### 应用部署
- **数据库初始化**：应用部署时创建所需数据库
- **多环境管理**：开发、测试、生产环境数据库管理
- **微服务部署**：为每个微服务创建独立数据库
- **自动化部署**：CI/CD 流程中的数据库准备

### 环境管理
- **测试环境**：创建临时测试数据库
- **开发环境**：开发人员独立数据库
- **环境清理**：删除不再使用的数据库
- **数据隔离**：多租户环境数据库隔离

### 数据库运维
- **数据库备份**：备份前创建临时数据库
- **数据迁移**：数据迁移时创建目标数据库
- **灾难恢复**：恢复时重建数据库
- **性能测试**：性能测试环境数据库

## 安全注意事项

### 数据安全
1. **备份优先**：删除数据库前必须确认已备份
2. **权限控制**：使用专门的管理账号，限制权限范围
3. **审计日志**：记录数据库创建和删除操作
4. **确认机制**：删除操作前需要明确确认

### 访问安全
1. **密码管理**：使用 Ansible Vault 加密存储密码
2. **SSL 连接**：生产环境使用 SSL 加密连接
3. **IP 白名单**：限制管理操作的来源 IP
4. **认证机制**：使用强认证机制（SCRAM-SHA-256）

### 操作安全
1. **测试优先**：在测试环境验证操作
2. **check_mode**：使用 --check 模式预览变更
3. **变更窗口**：在维护窗口期执行变更
4. **监控告警**：监控数据库创建和删除操作

## 环境依赖

### 必需
- MongoDB 3.6+
- Python pymongo 库
- community.mongodb collection
- MongoDB 管理员权限

### 推荐
- pymongo >= 3.12.0
- MongoDB SSL 配置
- 副本集配置（生产环境）

### 外部依赖
- **Ansible Collection**: `community.mongodb` (版本 >= 1.6.0)
- **Python 库**: pymongo >= 3.12.0
- **MongoDB 权限**: 需要 root 或 dbAdminAnyDatabase 角色

## 常见问题

### 1. 数据库创建失败
**解决方案**：
```bash
# 检查 MongoDB 服务状态
systemctl status mongod

# 检查用户权限
mongo admin -u admin -p --eval "db.runCommand({usersInfo: 'admin'})"

# 检查现有数据库
mongo admin -u admin -p --eval "show dbs"

# 检查连接
mongo --host localhost --port 27017 -u admin -p
```

### 2. 认证失败
**排查方法**：
```bash
# 检查认证配置
cat /etc/mongod.conf | grep security

# 测试认证
mongo admin -u admin -p password --authenticationDatabase admin

# 检查用户角色
mongo admin -u admin -p --eval "db.getUser('admin')"
```

## 最佳实践

### 创建数据库示例
```yaml
- name: 创建应用数据库
  community.mongodb.mongodb_db:
    name: "{{ mongodb_database_name }}"
    state: present
    login_host: "{{ mongodb_host }}"
    login_port: "{{ mongodb_port }}"
    login_user: "{{ mongodb_admin_user }}"
    login_password: "{{ mongodb_admin_password }}"
    login_database: "{{ mongodb_admin_database }}"
  no_log: true
  delegate_to: "{{ mongodb_host }}"
```

### 批量创建数据库示例
```yaml
- name: 批量创建应用数据库
  community.mongodb.mongodb_db:
    name: "{{ item }}"
    state: present
    login_host: "{{ mongodb_host }}"
    login_user: "{{ mongodb_admin_user }}"
    login_password: "{{ mongodb_admin_password }}"
    login_database: "admin"
  no_log: true
  loop:
    - app_db
    - reporting_db
    - analytics_db
  delegate_to: "{{ mongodb_host }}"
```

### 删除数据库示例
```yaml
- name: 删除废弃的测试数据库
  community.mongodb.mongodb_db:
    name: "{{ item }}"
    state: absent
    login_host: "{{ mongodb_host }}"
    login_user: "{{ mongodb_admin_user }}"
    login_password: "{{ mongodb_admin_password }}"
    login_database: "admin"
  no_log: true
  loop: "{{ mongodb_databases_to_delete }}"
  when: delete_databases | default(false) | bool
  delegate_to: "{{ mongodb_host }}"
```

### 副本集环境创建数据库示例
```yaml
- name: 在副本集环境创建数据库
  community.mongodb.mongodb_db:
    name: "{{ mongodb_database_name }}"
    state: present
    login_host: "{{ mongodb_host }}"
    login_user: "{{ mongodb_admin_user }}"
    login_password: "{{ mongodb_admin_password }}"
    login_database: "admin"
    replica_set: "{{ mongodb_replica_set }}"
  no_log: true
  delegate_to: "{{ mongodb_host }}"
```

### SSL 连接创建数据库示例
```yaml
- name: 使用 SSL 连接创建数据库
  community.mongodb.mongodb_db:
    name: "{{ mongodb_database_name }}"
    state: present
    login_host: "{{ mongodb_host }}"
    login_user: "{{ mongodb_admin_user }}"
    login_password: "{{ mongodb_admin_password }}"
    login_database: "admin"
    ssl: yes
    ssl_cert_reqs: CERT_REQUIRED
  no_log: true
  delegate_to: "{{ mongodb_host }}"
```

### 条件创建数据库示例
```yaml
- name: 检查数据库是否存在
  ansible.builtin.shell: |
    mongo admin -u {{ mongodb_admin_user }} -p {{ mongodb_admin_password }} --eval "db.getMongo().getDBNames().indexOf('{{ mongodb_database_name }}')"
  register: db_exists
  changed_when: false
  no_log: true

- name: 创建数据库（如果不存在）
  community.mongodb.mongodb_db:
    name: "{{ mongodb_database_name }}"
    state: present
    login_host: "{{ mongodb_host }}"
    login_user: "{{ mongodb_admin_user }}"
    login_password: "{{ mongodb_admin_password }}"
    login_database: "admin"
  no_log: true
  when: db_exists.stdout | int == -1
  delegate_to: "{{ mongodb_host }}"
```

## 相关示例
- [mongodb_user 模块](../mongodb_user/README.md) - MongoDB 用户权限管理
- [监控模块](../../monitoring/README.md) - 数据库监控配置
