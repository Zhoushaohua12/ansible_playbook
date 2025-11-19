# mysql_user 模块使用指南

## 模块用途
`community.mysql.mysql_user` 模块用于管理 MySQL 和 MariaDB 数据库的用户账号，包括创建、删除用户，设置密码，以及授予或撤销数据库权限。适用于自动化数据库用户生命周期管理、应用部署中的权限配置等场景。

## 主要参数

### 连接参数
- `login_host`：MySQL 服务器地址（默认 localhost）
- `login_port`：MySQL 服务器端口（默认 3306）
- `login_user`：管理员用户名（用于连接和执行操作）
- `login_password`：管理员密码（建议使用 Ansible Vault 加密）
- `login_unix_socket`：Unix socket 文件路径（替代 TCP 连接）

### 用户管理参数
- `name`：要创建或管理的用户名（必需）
- `password`：用户密码（明文或加密 hash）
- `host`：用户允许连接的主机（默认 localhost，可用 % 表示所有主机）
- `state`：用户状态（present 创建，absent 删除）

### 权限参数
- `priv`：用户权限，格式为 `数据库.表:权限列表`，例如 `mydb.*:ALL`
- `append_privs`：是否追加权限（true）还是替换权限（false，默认）

### 其他参数
- `encrypted`：密码是否已加密（true/false）
- `check_implicit_admin`：自动检测是否具有管理员权限
- `update_password`：密码更新策略（always 总是更新，on_create 仅创建时设置）

## 返回值
- `changed`：用户或权限是否发生变更
- `user`：被管理的用户名
- `msg`：操作结果消息

## 常见字段说明
- `priv` 权限格式：`database.table:privileges`
  - `*.*:ALL` - 所有数据库的所有权限（超级用户）
  - `mydb.*:ALL` - mydb 数据库的所有权限
  - `mydb.users:SELECT,INSERT,UPDATE` - mydb.users 表的读写权限
  - `mydb.*:SELECT` - mydb 数据库的只读权限

## 适用场景

### 应用部署场景
- 为新应用创建专用数据库用户
- 配置应用所需的最小权限集合
- 分离读写用户（读从库用户、写主库用户）

### 权限管理场景
- 定期更新用户密码
- 撤销离职人员的数据库访问权限
- 按环境（开发/测试/生产）创建不同权限的用户

### 安全加固场景
- 删除默认的匿名用户和测试账号
- 限制 root 用户仅允许本地连接
- 为每个应用创建独立的数据库用户

## 安全注意事项

### 凭证安全
1. **禁止硬编码密码**：使用 Ansible Vault 加密 `login_password` 和 `password` 参数
2. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志文件
3. **密码复杂度**：确保生成的密码满足强度要求（长度、特殊字符）
4. **定期轮换**：建立定期更新数据库密码的流程

### 权限最小化
1. **精细化授权**：避免使用 `*.*:ALL`，按需授予具体数据库和表的权限
2. **读写分离**：为只读操作创建 SELECT 权限用户
3. **禁止远程 root**：root 用户应限制为 `host: localhost`
4. **删除测试账号**：生产环境删除所有测试和示例账号

### 连接安全
1. **使用 SSL**：生产环境配置 `ca_cert`、`client_cert`、`client_key` 参数启用加密连接
2. **限制来源 IP**：通过 `host` 参数限制用户连接来源
3. **防火墙规则**：配合系统防火墙限制 3306 端口访问

### 操作审计
1. **版本控制**：将用户管理 playbook 纳入 Git 管理
2. **变更记录**：在 playbook 中添加详细的任务名称和注释
3. **使用 check_mode**：重要操作前先用 `--check` 预览变更

## 最佳实践

### 创建应用用户示例
```yaml
- name: 创建应用数据库用户
  community.mysql.mysql_user:
    login_host: localhost
    login_user: root
    login_password: "{{ mysql_root_password }}"
    name: app_user
    password: "{{ app_user_password }}"
    host: "192.168.1.%"
    priv: "appdb.*:SELECT,INSERT,UPDATE,DELETE"
    state: present
  no_log: true
```

### 权限追加示例
```yaml
- name: 为现有用户追加权限
  community.mysql.mysql_user:
    name: app_user
    host: "%"
    priv: "logdb.*:INSERT"
    append_privs: true
  no_log: true
```

### 删除用户示例
```yaml
- name: 删除离职人员数据库账号
  community.mysql.mysql_user:
    name: old_user
    host: "%"
    state: absent
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置数据库连接信息和用户参数
2. 使用 `--check` 模式预览用户创建和权限授予
3. 执行 playbook 创建用户
4. 使用 `mysql` 命令验证用户权限：`SHOW GRANTS FOR 'username'@'host';`
5. 测试用户连接和操作权限

## 常见问题
- **连接失败**：检查 `login_host`、`login_port` 和防火墙规则
- **权限不足**：确认 `login_user` 具有 GRANT 权限
- **密码无法设置**：检查 MySQL 密码策略配置（validate_password 插件）
- **用户已存在**：使用 `update_password: always` 更新密码

## 依赖说明
- **Ansible Collection**: `community.mysql`（使用 `ansible-galaxy collection install community.mysql` 安装）
- **Python 库**: PyMySQL 或 mysqlclient（在目标主机安装：`pip install PyMySQL`）
- **数据库权限**: 管理用户需要 GRANT 权限和 CREATE USER 权限

## 相关示例
- [mysql_db 模块](../mysql_db/README.md) - MySQL 数据库管理
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
- [监控模块](../../monitoring/README.md) - 配合数据库监控使用
