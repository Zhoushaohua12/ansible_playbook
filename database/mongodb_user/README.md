# mongodb_user 模块使用指南

## 模块用途
`community.mongodb.mongodb_user` 模块用于管理 MongoDB 数据库的用户账号，包括创建、删除用户，配置角色和权限。适用于 MongoDB 应用部署、用户权限管理、安全加固等场景。

## 主要参数

### 连接参数
- `login_host`：MongoDB 服务器地址（默认 localhost）
- `login_port`：MongoDB 服务器端口（默认 27017）
- `login_user`：管理员用户名
- `login_password`：管理员密码（建议使用 Ansible Vault 加密）
- `login_database`：认证数据库（默认 admin）

### 用户管理参数
- `name`：要创建或管理的用户名（必需）
- `password`：用户密码（明文）
- `database`：用户所属的数据库（必需）
- `state`：用户状态（present 创建，absent 删除）

### 角色和权限参数
- `roles`：用户角色列表，可以是字符串或字典格式
  - 字符串格式：`["readWrite", "dbAdmin"]`
  - 字典格式：`[{"db": "mydb", "role": "readWrite"}]`

### 更新策略
- `update_password`：密码更新策略（always 总是更新，on_create 仅创建时设置）

## 返回值
- `changed`：用户或角色是否发生变更
- `user`：被管理的用户名
- `msg`：操作结果消息

## 常见字段说明

### MongoDB 内置角色
- **数据库用户角色**：
  - `read`：只读权限（查询数据）
  - `readWrite`：读写权限（查询和修改数据）
- **数据库管理角色**：
  - `dbAdmin`：数据库管理权限（索引、统计、schema）
  - `dbOwner`：数据库所有者（read + readWrite + dbAdmin）
  - `userAdmin`：用户管理权限（创建和管理用户）
- **集群管理角色**：
  - `clusterAdmin`：集群管理权限
  - `clusterManager`：集群操作权限
  - `clusterMonitor`：集群监控权限
- **备份恢复角色**：
  - `backup`：备份权限
  - `restore`：恢复权限
- **超级用户角色**：
  - `root`：所有权限（仅用于紧急情况）

## 适用场景

### 应用部署场景
- 为新应用创建 MongoDB 用户
- 配置应用所需的读写权限
- 分离读库用户和写库用户

### 权限管理场景
- 定期更新用户密码
- 撤销离职人员的数据库访问权限
- 按环境（开发/测试/生产）创建不同权限的用户

### 安全加固场景
- 启用认证并创建管理员账号
- 为每个应用创建独立的数据库用户
- 配置最小权限原则

## 安全注意事项

### 凭证安全
1. **禁止硬编码密码**：使用 Ansible Vault 加密 `login_password` 和 `password` 参数
2. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志文件
3. **密码复杂度**：确保生成的密码满足强度要求
4. **定期轮换**：建立定期更新数据库密码的流程

### 权限最小化
1. **精细化授权**：避免使用 `root` 角色，按需授予具体权限
2. **读写分离**：为只读操作创建 `read` 权限用户
3. **数据库隔离**：不同应用使用不同数据库和用户
4. **删除默认账号**：生产环境删除所有测试账号

### 认证安全
1. **启用认证**：MongoDB 配置文件中启用 `security.authorization`
2. **使用 SSL/TLS**：生产环境配置加密连接
3. **限制绑定地址**：配置 `net.bindIp` 限制访问来源
4. **防火墙规则**：限制 27017 端口访问

### 操作审计
1. **版本控制**：将用户管理 playbook 纳入 Git 管理
2. **变更记录**：在 playbook 中添加详细的任务名称和注释
3. **使用 check_mode**：重要操作前先用 `--check` 预览变更
4. **审计日志**：启用 MongoDB 审计日志记录用户操作

## 最佳实践

### 创建应用用户示例
```yaml
- name: 创建应用数据库用户
  community.mongodb.mongodb_user:
    login_host: localhost
    login_user: admin
    login_password: "{{ mongodb_admin_password }}"
    login_database: admin
    name: app_user
    password: "{{ app_user_password }}"
    database: webapp_db
    roles:
      - db: webapp_db
        role: readWrite
    state: present
  no_log: true
```

### 创建只读用户示例
```yaml
- name: 创建只读报表用户
  community.mongodb.mongodb_user:
    name: report_user
    password: "{{ report_user_password }}"
    database: webapp_db
    roles:
      - db: webapp_db
        role: read
    state: present
  no_log: true
```

### 创建多数据库权限用户示例
```yaml
- name: 创建跨数据库用户
  community.mongodb.mongodb_user:
    name: multi_db_user
    password: "{{ multi_db_password }}"
    database: admin
    roles:
      - db: webapp_db
        role: readWrite
      - db: log_db
        role: read
      - db: session_db
        role: readWrite
    state: present
  no_log: true
```

### 创建管理员用户示例
```yaml
- name: 创建数据库管理员
  community.mongodb.mongodb_user:
    name: db_admin
    password: "{{ admin_password }}"
    database: admin
    roles:
      - userAdminAnyDatabase
      - dbAdminAnyDatabase
      - readWriteAnyDatabase
    state: present
  no_log: true
```

### 删除用户示例
```yaml
- name: 删除离职人员账号
  community.mongodb.mongodb_user:
    name: old_user
    database: webapp_db
    state: absent
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置数据库连接信息和用户参数
2. 使用 `--check` 模式预览用户创建和角色配置
3. 执行 playbook 创建用户
4. 使用 `mongo` 命令验证用户权限：
   ```javascript
   use webapp_db
   db.auth("app_user", "password")
   db.getUser("app_user")
   ```
5. 测试用户连接和操作权限

## 常见问题
- **连接失败**：检查 MongoDB 是否启用认证，以及防火墙规则
- **权限不足**：确认 `login_user` 具有 userAdmin 或 userAdminAnyDatabase 角色
- **用户已存在**：使用 `update_password: always` 更新密码
- **角色不存在**：检查 MongoDB 版本是否支持该角色
- **认证数据库错误**：确保 `login_database` 和用户的认证数据库一致

## 依赖说明
- **Ansible Collection**: `community.mongodb`（使用 `ansible-galaxy collection install community.mongodb` 安装）
- **Python 库**: pymongo（在目标主机安装：`pip install pymongo`）
- **MongoDB 配置**: 需要启用认证（配置文件中设置 `security.authorization: enabled`）
- **管理员权限**: 需要具有 userAdmin 或 userAdminAnyDatabase 角色的用户

## 相关示例
- [mysql_user 模块](../mysql_user/README.md) - MySQL 用户管理
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
- [监控模块](../../monitoring/README.md) - 配合数据库监控使用
- [应用管理](../../applications/README.md) - 应用部署与数据库集成
