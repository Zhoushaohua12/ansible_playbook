# postgresql_db 模块使用指南

## 模块用途
`community.postgresql.postgresql_db` 模块用于管理 PostgreSQL 数据库，包括创建、删除数据库，设置 owner、encoding、template 等属性。适用于 PostgreSQL 应用部署、数据库初始化、多租户环境管理等场景。

## 主要参数

### 连接参数
- `login_host`：PostgreSQL 服务器地址（默认 localhost）
- `login_port`：PostgreSQL 服务器端口（默认 5432）
- `login_user`：管理员用户名（默认 postgres）
- `login_password`：管理员密码（建议使用 Ansible Vault 加密）
- `login_unix_socket`：Unix socket 目录路径（替代 TCP 连接）

### 数据库管理参数
- `name`：数据库名称（必需）
- `state`：数据库状态
  - `present`：创建数据库（如不存在）
  - `absent`：删除数据库
  - `dump`：导出数据库到文件
  - `restore`：从文件恢复数据库
- `owner`：数据库所有者用户名
- `template`：创建数据库时使用的模板（默认 template1）

### 字符集和排序规则
- `encoding`：数据库字符编码（如 UTF8、LATIN1、SQL_ASCII）
- `lc_collate`：排序规则（如 en_US.UTF-8、C）
- `lc_ctype`：字符分类（如 en_US.UTF-8、C）

### 连接限制和表空间
- `conn_limit`：最大并发连接数限制（-1 表示无限制）
- `tablespace`：数据库使用的表空间

### 导入导出参数
- `target`：导出或恢复的文件路径
- `target_opts`：pg_dump 或 pg_restore 的额外参数

## 返回值
- `changed`：数据库是否发生变更
- `db`：被管理的数据库名称
- `executed_commands`：执行的 SQL 命令列表

## 常见字段说明
- `encoding` 常用编码：
  - `UTF8`：Unicode 编码（推荐）
  - `LATIN1`：西欧字符集
  - `SQL_ASCII`：7位 ASCII（不推荐）
- `lc_collate` 常用排序规则：
  - `en_US.UTF-8`：美国英语 UTF-8 排序
  - `C`：C locale（字节序排序，性能最好）
  - `zh_CN.UTF-8`：简体中文 UTF-8 排序
- `template` 常用模板：
  - `template0`：原始干净模板（用于指定 encoding 和 locale）
  - `template1`：默认模板（可能包含自定义对象）

## 适用场景

### 应用部署场景
- 为新应用创建 PostgreSQL 数据库
- 设置数据库 owner 和编码
- 初始化多租户环境的独立数据库

### 数据迁移场景
- 导出生产数据库到文件
- 跨环境数据库复制
- 数据库版本升级前备份

### 多租户管理场景
- 为每个租户创建独立数据库
- 设置连接数限制防止资源耗尽
- 按租户分配不同的表空间

## 安全注意事项

### 数据备份
1. **删除前备份**：执行 `state: absent` 前务必先导出数据
2. **测试恢复**：定期验证备份文件可以正常恢复
3. **异地存储**：备份文件存储在不同于数据库的服务器
4. **版本兼容**：确保 pg_dump 版本与 PostgreSQL 版本兼容

### 凭证安全
1. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志
2. **Ansible Vault**：加密存储 `login_password`
3. **pg_hba.conf**：配置严格的访问控制规则
4. **SSL 连接**：生产环境启用 SSL 加密连接

### 权限管理
1. **最小权限**：避免使用 postgres 超级用户，创建专用管理账号
2. **owner 隔离**：不同应用使用不同的数据库 owner
3. **角色管理**：配合 postgresql_user 模块管理角色权限

### 操作审计
1. **check_mode 预览**：重要操作前先用 `--check` 预览
2. **命名规范**：数据库命名遵循统一规范
3. **变更记录**：在 playbook 中添加详细的任务名称和注释

## 最佳实践

### 创建数据库示例
```yaml
- name: 创建应用数据库
  community.postgresql.postgresql_db:
    login_host: localhost
    login_user: postgres
    login_password: "{{ postgres_password }}"
    name: webapp_db
    owner: webapp_user
    encoding: UTF8
    lc_collate: en_US.UTF-8
    lc_ctype: en_US.UTF-8
    template: template0
    state: present
  no_log: true
```

### 设置连接限制示例
```yaml
- name: 创建数据库并限制连接数
  community.postgresql.postgresql_db:
    name: tenant_db
    owner: tenant_user
    conn_limit: 50
    state: present
  no_log: true
```

### 导出数据库示例
```yaml
- name: 导出数据库到备份文件
  community.postgresql.postgresql_db:
    name: webapp_db
    state: dump
    target: /backups/webapp_db_{{ ansible_date_time.iso8601_basic_short }}.dump
  no_log: true
```

### 恢复数据库示例
```yaml
- name: 从备份文件恢复数据库
  community.postgresql.postgresql_db:
    name: webapp_db_restored
    state: restore
    target: /backups/webapp_db_20231201.dump
  no_log: true
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置数据库连接信息
2. 使用 `--check` 模式预览数据库创建
3. 执行 playbook 创建数据库
4. 使用 `\l` 命令验证数据库已创建
5. 检查编码：`\l+ database_name`
6. 验证 owner 和连接限制

## 常见问题
- **连接失败**：检查 pg_hba.conf 是否允许连接，以及防火墙规则
- **权限不足**：确认 `login_user` 具有 CREATEDB 权限
- **编码不支持**：使用 `template: template0` 并指定正确的 encoding 和 locale
- **数据库已存在**：PostgreSQL 不允许修改现有数据库的 encoding，需要先删除
- **locale 不存在**：在操作系统层面生成对应的 locale：`locale-gen en_US.UTF-8`

## 依赖说明
- **Ansible Collection**: `community.postgresql`（使用 `ansible-galaxy collection install community.postgresql` 安装）
- **Python 库**: psycopg2 或 psycopg2-binary（在目标主机安装：`pip install psycopg2-binary`）
- **数据库权限**: 管理用户需要 CREATEDB 权限或 SUPERUSER 权限
- **PostgreSQL 工具**: 导出操作需要 pg_dump，恢复需要 pg_restore（通常随 PostgreSQL 客户端安装）

## 相关示例
- [mysql_db 模块](../mysql_db/README.md) - MySQL 数据库管理
- [mongodb_user 模块](../mongodb_user/README.md) - MongoDB 用户管理
- [应用管理](../../applications/README.md) - 应用部署与数据库集成
