# postgresql_user 模块使用指南

## 模块用途
`community.postgresql.postgresql_user` 模块用于管理 PostgreSQL 数据库用户（角色），包括创建、删除用户，设置密码，以及授予或撤销数据库权限。适用于自动化数据库用户生命周期管理、应用部署中的权限配置、多租户账号隔离等场景。

## 主要参数

### 连接参数
- `login_host`：PostgreSQL 服务器地址（默认 localhost）
- `login_port`：PostgreSQL 服务器端口（默认 5432）
- `login_user`：管理员用户名（默认 postgres）
- `login_password`：管理员密码（建议使用 Ansible Vault 加密）
- `login_unix_socket`：Unix socket 目录路径（替代 TCP 连接）

### 用户管理参数
- `name`：要创建或管理的用户名（必需）
- `password`：用户密码（明文，Ansible 会自动加密）
- `state`：用户状态（present 创建/修改，absent 删除）

### 权限参数
- `db`：要授予权限的数据库名称
- `privs`：用户权限，格式为 `数据库.模式.对象:权限列表`
  - `ALL PRIVILEGES`：所有权限
  - `CONNECT`：连接数据库权限
  - `CREATE`：创建对象权限
  - `SELECT,INSERT,UPDATE,DELETE`：表操作权限
- `priv`：权限对象，如 `mydb.public.table1:SELECT`

### 角色参数
- `role_attr_flags`：角色属性标志
  - `SUPERUSER`：超级用户权限
  - `CREATEDB`：创建数据库权限
  - `CREATEROLE`：创建角色权限
  - `LOGIN`：允许登录（必须设置）
  - `NOINHERIT`：不继承权限
  - `NOSUPERUSER`、`NOCREATEDB`、`NOCREATEROLE`、`NOLOGIN`：反向标志

### 其他参数
- `expires`：用户过期时间（ISO 8601 格式，如 2025-12-31）
- `fail_on_user`：用户不存在时是否失败（默认 true）

## 返回值
- `changed`：用户或权限是否发生变更
- `user`：被管理的用户名
- `msg`：操作结果消息

## 常见字段说明
- `privs` 权限格式示例：
  - `ALL PRIVILEGES`：所有权限
  - `CONNECT`：连接数据库权限
  - `CREATE`：创建权限
  - `SELECT`：查询权限
  - `INSERT,UPDATE,DELETE`：修改权限
  - `SELECT,INSERT,UPDATE,DELETE`：常用的数据操作权限
  - `EXECUTE`：执行函数权限

- `role_attr_flags` 标志组合示例：
  - `LOGIN`：允许作为账户登录
  - `LOGIN,CREATEDB`：允许登录和创建数据库
  - `LOGIN,CREATEROLE`：允许登录和创建角色
  - `NOLOGIN`：不允许登录（只用于继承权限的角色）

## 适用场景

### 应用部署场景
- 为新应用创建专用 PostgreSQL 用户
- 配置应用所需的最小权限集合
- 分离读写用户（只读用户、读写用户）

### 权限管理场景
- 定期更新用户密码
- 撤销离职人员的数据库访问权限
- 按环境（开发/测试/生产）创建不同权限的用户

### 多租户管理场景
- 为每个租户创建独立数据库用户
- 限制用户只能访问特定数据库
- 实现租户数据隔离

### 安全加固场景
- 删除默认的 postgres 空密码账号
- 限制 postgres 超级用户仅本地连接
- 为每个应用创建独立的数据库用户

## 安全注意事项

### 凭证安全
1. **禁止硬编码密码**：使用 Ansible Vault 加密 `login_password` 和 `password` 参数
2. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志文件
3. **密码复杂度**：确保生成的密码满足强度要求（长度、特殊字符）
4. **定期轮换**：建立定期更新数据库密码的流程

### 权限最小化
1. **精细化授权**：避免使用 SUPERUSER，按需授予具体权限
2. **数据库隔离**：为不同应用分配不同的数据库用户
3. **禁止远程 postgres**：postgres 超级用户应限制为本地连接
4. **删除测试账号**：生产环境删除所有测试和示例账号

### 连接安全
1. **使用 SSL**：生产环境配置 SSL 连接参数
2. **pg_hba.conf 配置**：配置严格的访问控制规则
3. **限制来源 IP**：通过防火墙和 pg_hba.conf 限制访问
4. **防火墙规则**：配合系统防火墙限制 5432 端口访问

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
    db: postgres
    name: app_user
    password: "{{ app_user_password }}"
    role_attr_flags: LOGIN
    state: present
  no_log: true
```

### 授予数据库权限示例
```yaml
- name: 授予用户连接和使用数据库权限
  community.postgresql.postgresql_user:
    login_host: localhost
    login_user: postgres
    login_password: "{{ postgres_admin_password }}"
    db: "{{ target_database }}"
    name: app_user
    privs: CONNECT
    state: present
  no_log: true
```

### 创建只读用户示例
```yaml
- name: 创建只读用户 - 用于报表查询
  community.postgresql.postgresql_user:
    login_host: localhost
    login_user: postgres
    login_password: "{{ postgres_admin_password }}"
    db: postgres
    name: report_user
    password: "{{ report_user_password }}"
    role_attr_flags: LOGIN
    state: present
  no_log: true

- name: 授予报表用户的查询权限
  community.postgresql.postgresql_user:
    login_host: localhost
    login_user: postgres
    login_password: "{{ postgres_admin_password }}"
    db: "{{ target_database }}"
    name: report_user
    privs: "{{ target_database }}.public.*:SELECT"
    state: present
  no_log: true
```

### 删除用户示例
```yaml
- name: 删除离职人员数据库账号
  community.postgresql.postgresql_user:
    login_host: localhost
    login_user: postgres
    login_password: "{{ postgres_admin_password }}"
    db: postgres
    name: old_user
    state: absent
  no_log: true
```

### 创建角色用户（无登录权限）示例
```yaml
- name: 创建权限角色 - 不能直接登录
  community.postgresql.postgresql_user:
    login_host: localhost
    login_user: postgres
    login_password: "{{ postgres_admin_password }}"
    db: postgres
    name: app_role
    role_attr_flags: NOLOGIN
    state: present
  no_log: true
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置数据库连接信息和用户参数
2. 使用 `--check` 模式预览用户创建和权限授予
3. 执行 playbook 创建用户
4. 使用 `\du` 命令验证用户已创建
5. 查看用户权限：`\dp+ table_name`
6. 测试用户连接权限

## 常见问题
- **连接失败**：检查 `login_host`、`login_port` 和防火墙规则
- **权限不足**：确认 `login_user` 具有足够的权限（通常需要 SUPERUSER）
- **密码无法设置**：检查 PostgreSQL 密码策略和密码认证方法
- **用户已存在**：使用 `state: present` 会更新现有用户属性
- **权限授予失败**：确认目标数据库和模式存在，以及 `privs` 格式正确

## 依赖说明
- **Ansible Collection**: `community.postgresql`（使用 `ansible-galaxy collection install community.postgresql` 安装）
- **Python 库**: psycopg2 或 psycopg2-binary（在目标主机安装：`pip install psycopg2-binary`）
- **数据库权限**: 管理用户需要 SUPERUSER 权限或相应的管理权限

## 相关示例
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
- [mysql_user 模块](../mysql_user/README.md) - MySQL 用户管理
- [应用管理](../../applications/README.md) - 应用部署与数据库集成
