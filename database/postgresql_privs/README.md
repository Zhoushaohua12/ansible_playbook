# PostgreSQL 权限管理模块使用指南

## 模块用途
`community.postgresql.postgresql_privs` 模块用于管理 PostgreSQL 数据库对象的权限（GRANT/REVOKE），支持数据库、表、序列、函数、模式等多种对象类型的权限授予和撤销。适用于权限最小化、安全加固、多租户环境、合规审计等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `database` | str | 数据库名称（必需） | `mydb`、`postgres` 等 |
| `roles` | str/list | 角色名称（必需，用户或组） | `app_user`、`readonly_user` 等 |
| `type` | str | 对象类型（可选） | `database`、`table`、`sequence`、`function`、`schema` 等 |
| `objs` | str/list | 对象名称（type 为 table/sequence 等时必需） | `users`、`orders`、`ALL_IN_SCHEMA` 等 |
| `privs` | str/list | 权限列表（可选，默认 ALL） | `SELECT`、`INSERT`、`UPDATE`、`DELETE`、`ALL` 等 |
| `state` | str | 权限状态（present 授予，absent 撤销） | present、absent |
| `grant_option` | bool | 是否授予 GRANT OPTION 权限 | true、false |
| `schema` | str | 模式名称（type 为 table/sequence 等时可选） | `public`、`app_schema` 等 |

## 高级参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `login_host` | str | PostgreSQL 主机 | `localhost`、`127.0.0.1` |
| `login_port` | int | PostgreSQL 端口 | 5432 |
| `login_user` | str | 登录用户 | `postgres`、管理员用户 |
| `login_password` | str | 登录密码 | 密码字符串 |
| `ssl_mode` | str | SSL 连接模式 | `disable`、`allow`、`prefer`、`require` |

## 权限类型说明

| 对象类型 | 可用权限 | 说明 |
|----------|----------|------|
| database | CREATE, CONNECT, TEMPORARY, TEMP, ALL | 数据库级权限 |
| table | SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER, ALL | 表级权限 |
| sequence | USAGE, SELECT, UPDATE, ALL | 序列权限 |
| function | EXECUTE, ALL | 函数权限 |
| schema | CREATE, USAGE, ALL | 模式权限 |
| tablespace | CREATE, ALL | 表空间权限 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了修改 | true/false |
| `queries` | 执行的 SQL 语句列表 | ["GRANT SELECT ON..."] |

## 使用情境

### 权限最小化
- **应用账号**：应用程序使用专用账号，仅授予必要权限
- **只读账号**：报表和分析使用只读账号
- **备份账号**：备份程序使用专用备份账号
- **审计账号**：审计和监控使用只读审计账号

### 多租户环境
- **租户隔离**：不同租户使用不同模式和账号
- **权限隔离**：租户之间数据完全隔离
- **共享资源**：公共函数和视图的权限管理
- **动态授权**：根据租户需求动态调整权限

### 安全加固
- **最小权限**：遵循最小权限原则
- **权限分离**：读写权限分离
- **定期审计**：定期审计权限配置
- **权限回收**：及时回收不需要的权限

## 安全注意事项

### 权限安全
1. **最小权限原则**：仅授予必要的最小权限
2. **权限分离**：读写权限分离，避免账号权限过大
3. **定期审计**：定期审计和清理不必要的权限
4. **GRANT OPTION**：谨慎授予 GRANT OPTION 权限

### 配置安全
1. **密码管理**：使用 Ansible Vault 加密存储密码
2. **SSL 连接**：生产环境使用 SSL 加密连接
3. **权限文档**：维护权限配置文档
4. **变更审批**：权限变更应经过审批流程

### 操作安全
1. **测试验证**：在测试环境验证权限配置
2. **回滚方案**：准备权限回滚方案
3. **监控告警**：监控权限变更和异常访问
4. **备份配置**：备份权限配置信息

## 环境依赖

### 必需
- PostgreSQL 9.4+
- Python psycopg2 库
- community.postgresql collection
- PostgreSQL 管理员权限

### 推荐
- psycopg2-binary 包
- PostgreSQL SSL 配置
- 权限管理工具

### 外部依赖
- **Ansible Collection**: `community.postgresql` (版本 >= 2.4.0)
- **Python 库**: psycopg2-binary >= 2.8.0
- **PostgreSQL 权限**: 需要 SUPERUSER 或相应的 GRANT 权限

## 常见问题

### 1. 权限授予失败
**解决方案**：
```bash
# 检查用户是否存在
psql -U postgres -d mydb -c "\\du"

# 检查数据库是否存在
psql -U postgres -c "\\l"

# 检查表是否存在
psql -U postgres -d mydb -c "\\dt"

# 检查当前权限
psql -U postgres -d mydb -c "\\dp tablename"
```

### 2. 权限验证失败
**排查方法**：
```bash
# 以目标用户登录测试
psql -U app_user -d mydb -c "SELECT * FROM users LIMIT 1;"

# 检查角色权限
psql -U postgres -d mydb -c "SELECT * FROM information_schema.table_privileges WHERE grantee='app_user';"

# 检查默认权限
psql -U postgres -d mydb -c "\\ddp"
```

## 最佳实践

### 授予表 SELECT 权限示例
```yaml
- name: 授予用户表查询权限
  community.postgresql.postgresql_privs:
    database: "{{ postgres_database }}"
    roles: "{{ postgres_readonly_user }}"
    type: table
    objs: "{{ postgres_table_name }}"
    privs: SELECT
    state: present
    login_host: "{{ postgres_host }}"
    login_user: "{{ postgres_admin_user }}"
    login_password: "{{ postgres_admin_password }}"
  no_log: true
  delegate_to: "{{ postgres_host }}"
```

### 授予多个表权限示例
```yaml
- name: 授予用户多个表的读写权限
  community.postgresql.postgresql_privs:
    database: "{{ postgres_database }}"
    roles: "{{ postgres_app_user }}"
    type: table
    objs: "{{ item }}"
    privs:
      - SELECT
      - INSERT
      - UPDATE
      - DELETE
    state: present
    login_host: "{{ postgres_host }}"
    login_user: "{{ postgres_admin_user }}"
    login_password: "{{ postgres_admin_password }}"
  no_log: true
  loop:
    - users
    - orders
    - products
  delegate_to: "{{ postgres_host }}"
```

### 授予模式所有表权限示例
```yaml
- name: 授予用户模式中所有表的查询权限
  community.postgresql.postgresql_privs:
    database: "{{ postgres_database }}"
    roles: "{{ postgres_readonly_user }}"
    type: table
    objs: ALL_IN_SCHEMA
    schema: "{{ postgres_schema }}"
    privs: SELECT
    state: present
    login_host: "{{ postgres_host }}"
    login_user: "{{ postgres_admin_user }}"
    login_password: "{{ postgres_admin_password }}"
  no_log: true
  delegate_to: "{{ postgres_host }}"
```

### 授予数据库连接权限示例
```yaml
- name: 授予用户数据库连接权限
  community.postgresql.postgresql_privs:
    database: "{{ postgres_database }}"
    roles: "{{ postgres_app_user }}"
    type: database
    privs: CONNECT
    state: present
    login_host: "{{ postgres_host }}"
    login_user: "{{ postgres_admin_user }}"
    login_password: "{{ postgres_admin_password }}"
  no_log: true
  delegate_to: "{{ postgres_host }}"
```

### 授予序列权限示例
```yaml
- name: 授予用户序列使用权限
  community.postgresql.postgresql_privs:
    database: "{{ postgres_database }}"
    roles: "{{ postgres_app_user }}"
    type: sequence
    objs: "{{ postgres_sequence_name }}"
    privs: USAGE, SELECT, UPDATE
    state: present
    login_host: "{{ postgres_host }}"
    login_user: "{{ postgres_admin_user }}"
    login_password: "{{ postgres_admin_password }}"
  no_log: true
  delegate_to: "{{ postgres_host }}"
```

### 撤销权限示例
```yaml
- name: 撤销用户表删除权限
  community.postgresql.postgresql_privs:
    database: "{{ postgres_database }}"
    roles: "{{ postgres_app_user }}"
    type: table
    objs: "{{ postgres_table_name }}"
    privs: DELETE
    state: absent
    login_host: "{{ postgres_host }}"
    login_user: "{{ postgres_admin_user }}"
    login_password: "{{ postgres_admin_password }}"
  no_log: true
  delegate_to: "{{ postgres_host }}"
```

### 授予函数执行权限示例
```yaml
- name: 授予用户函数执行权限
  community.postgresql.postgresql_privs:
    database: "{{ postgres_database }}"
    roles: "{{ postgres_app_user }}"
    type: function
    objs: "{{ postgres_function_name }}"
    privs: EXECUTE
    state: present
    login_host: "{{ postgres_host }}"
    login_user: "{{ postgres_admin_user }}"
    login_password: "{{ postgres_admin_password }}"
  no_log: true
  delegate_to: "{{ postgres_host }}"
```

### 批量权限配置示例
```yaml
- name: 批量配置用户权限
  community.postgresql.postgresql_privs:
    database: "{{ item.database }}"
    roles: "{{ item.role }}"
    type: "{{ item.type }}"
    objs: "{{ item.objs }}"
    privs: "{{ item.privs }}"
    state: present
    login_host: "{{ postgres_host }}"
    login_user: "{{ postgres_admin_user }}"
    login_password: "{{ postgres_admin_password }}"
  no_log: true
  loop: "{{ postgres_privileges }}"
  loop_control:
    label: "{{ item.role }}"
  delegate_to: "{{ postgres_host }}"
```

## 相关示例
- [postgresql_user 模块](../postgresql_user/README.md) - PostgreSQL 用户管理
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
