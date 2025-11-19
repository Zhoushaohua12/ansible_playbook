# postgresql_user 模块使用指南

## 模块用途
`community.postgresql.postgresql_user` 模块用于管理 PostgreSQL 数据库的用户账号（也称为角色），包括创建、删除用户，设置密码，以及授予或撤销数据库权限。适用于自动化数据库用户生命周期管理、应用部署中的权限配置等场景。

## 主要参数

### 连接参数
- `login_host`：PostgreSQL 服务器地址（默认 localhost）
- `login_port`：PostgreSQL 服务器端口（默认 5432）
- `login_user`：管理员用户名（用于连接和执行操作）
- `login_password`：管理员密码（建议使用 Ansible Vault 加密）
- `login_unix_socket`：Unix socket 目录路径（替代 TCP 连接）

### 用户管理参数
- `name`：要创建或管理的用户名（必需）
- `password`：用户密码（明文或加密 hash）
- `encrypted`：密码是否已加密（true/false，默认 true）
- `state`：用户状态（present 创建，absent 删除）
- `expires`：用户密码过期时间（ISO 8601 格式）

### 权限参数
- `role_attr_flags`：角色属性标志（SUPERUSER、CREATEDB、CREATEROLE、LOGIN 等）
- `db`：授予权限的数据库名称
- `priv`：权限列表（如 ALL、SELECT、INSERT、UPDATE、DELETE）
- `grant_option`：是否允许用户授予权限给其他用户

### 其他参数
- `conn_limit`：用户最大连接数限制（-1 表示无限制）
- `session_role`：执行操作时切换到的角色
- `trust_input`：信任输入参数，避免 SQL 注入检查（仅内部使用）

## 返回值
- `changed`：用户或权限是否发生变更
- `user`：被管理的用户名
- `queries`：执行的 SQL 语句列表（调试模式）

## 常见字段说明
- `role_attr_flags` 角色属性：
  - `SUPERUSER` - 超级用户权限（慎用）
  - `CREATEDB` - 允许创建数据库
  - `CREATEROLE` - 允许创建其他角色
  - `LOGIN` - 允许登录（默认）
  - `REPLICATION` - 允许流复制
  - `NOSUPERUSER`、`NOCREATEDB` - 撤销对应权限

- `priv` 权限格式：
  - 格式：`table:priv1,priv2/function:priv1/sequence:priv1`
  - 示例：`ALL` - 所有权限
  - 示例：`SELECT,INSERT,UPDATE` - 读写权限

## 适用场景

### 应用部署场景
- 为新应用创建专用数据库用户
- 配置应用所需的最小权限集合
- 分离读写用户（读从库用户、写主库用户）

### 权限管理场景
- 定期更新用户密码并设置过期时间
- 撤销离职人员的数据库访问权限
- 按环境（开发/测试/生产）创建不同权限的用户

### 安全加固场景
- 限制用户连接数防止资源耗尽
- 禁用不需要的角色属性（SUPERUSER、CREATEDB）
- 为每个应用创建独立的数据库用户

## 安全注意事项

### 凭证安全
1. **禁止硬编码密码**：使用 Ansible Vault 加密 `login_password` 和 `password` 参数
2. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志文件
3. **密码复杂度**：确保生成的密码满足强度要求（长度、特殊字符）
4. **定期轮换**：建立定期更新数据库密码的流程，配置 `expires` 参数

### 权限最小化
1. **精细化授权**：避免授予 SUPERUSER 权限，按需授予具体权限
2. **读写分离**：为只读操作创建仅有 SELECT 权限的用户
3. **连接限制**：使用 `conn_limit` 限制用户最大连接数
4. **撤销测试账号**：生产环境删除所有测试和示例账号

### 连接安全
1. **使用 SSL**：生产环境配置 `ssl_mode` 参数启用加密连接
2. **配置 pg_hba.conf**：通过主机白名单限制用户连接来源
3. **防火墙规则**：配合系统防火墙限制 5432 端口访问
4. **使用 Unix Socket**：本地连接优先使用 Unix socket 而非 TCP

### 操作审计
1. **版本控制**：将用户管理 playbook 纳入 Git 管理
2. **变更记录**：在 playbook 中添加详细的任务名称和注释
3. **使用 check_mode**：重要操作前先用 `--check` 预览变更

## 最佳实践

### 创建应用用户示例
```yaml
- name: 创建应用数据库用户
  community.postgresql.postgresql_user:
    login_host: localhost
    login_user: postgres
    login_password: "{{ postgres_admin_password }}"
    name: app_user
    password: "{{ app_user_password }}"
    role_attr_flags: LOGIN,NOCREATEDB,NOCREATEROLE
    db: appdb
    priv: ALL
    state: present
  no_log: true
```

### 创建只读用户示例
```yaml
- name: 创建只读用户
  community.postgresql.postgresql_user:
    login_host: localhost
    login_user: postgres
    login_password: "{{ postgres_admin_password }}"
    name: readonly_user
    password: "{{ readonly_user_password }}"
    role_attr_flags: LOGIN,NOCREATEDB,NOCREATEROLE
    db: appdb
    priv: SELECT
    conn_limit: 10
    state: present
  no_log: true
```

### 设置密码过期示例
```yaml
- name: 更新用户密码并设置过期时间
  community.postgresql.postgresql_user:
    name: app_user
    password: "{{ new_app_user_password }}"
    expires: "2025-12-31"
  no_log: true
```

### 删除用户示例
```yaml
- name: 删除离职人员数据库账号
  community.postgresql.postgresql_user:
    name: old_user
    state: absent
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置数据库连接信息和用户参数
2. 使用 `--check` 模式预览用户创建和权限授予
3. 执行 playbook 创建用户
4. 使用 `psql` 命令验证用户权限：`\du username` 和 `\dp`
5. 测试用户连接和操作权限

## 常见问题
- **连接失败**：检查 `login_host`、`login_port`、`pg_hba.conf` 和防火墙规则
- **权限不足**：确认 `login_user` 具有 SUPERUSER 或 CREATEROLE 权限
- **密码无法设置**：检查 PostgreSQL 密码策略配置和 `pg_hba.conf` 认证方式
- **用户已存在**：模块默认会更新现有用户，检查 `encrypted` 参数设置

## 依赖说明
- **Ansible Collection**: `community.postgresql`（使用 `ansible-galaxy collection install community.postgresql` 安装）
- **Python 库**: psycopg2 或 psycopg2-binary（在目标主机安装：`pip install psycopg2-binary`）
- **数据库权限**: 管理用户需要 SUPERUSER 或 CREATEROLE 权限

## 相关示例
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
- [postgresql_privs 模块](../postgresql_privs/README.md) - PostgreSQL 权限管理
- [mysql_user 模块](../mysql_user/README.md) - MySQL 用户管理
- [监控模块](../../monitoring/README.md) - 配合数据库监控使用
