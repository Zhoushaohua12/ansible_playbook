# mysql_db 模块使用指南

## 模块用途
`community.mysql.mysql_db` 模块用于管理 MySQL 和 MariaDB 数据库，包括创建、删除数据库，导入导出 SQL 文件，设置字符集和排序规则。适用于应用部署、数据库初始化、备份恢复等场景。

## 主要参数

### 连接参数
- `login_host`：MySQL 服务器地址（默认 localhost）
- `login_port`：MySQL 服务器端口（默认 3306）
- `login_user`：管理员用户名（用于连接和执行操作）
- `login_password`：管理员密码（建议使用 Ansible Vault 加密）
- `login_unix_socket`：Unix socket 文件路径（替代 TCP 连接）

### 数据库管理参数
- `name`：数据库名称（必需），可以是单个数据库或列表
- `state`：数据库状态
  - `present`：创建数据库（如不存在）
  - `absent`：删除数据库
  - `dump`：导出数据库到 SQL 文件
  - `import`：从 SQL 文件导入数据

### 字符集和排序规则
- `encoding`：数据库字符集（如 utf8mb4、utf8、latin1）
- `collation`：排序规则（如 utf8mb4_unicode_ci、utf8mb4_general_ci）

### 导入导出参数
- `target`：SQL 文件路径（用于 dump 或 import 操作）
- `single_transaction`：使用单事务导出（适合 InnoDB，保证一致性）
- `quick`：快速导出，减少内存占用

## 返回值
- `changed`：数据库是否发生变更
- `db`：被管理的数据库名称
- `db_list`：当前所有数据库列表（部分操作返回）
- `msg`：操作结果消息

## 常见字段说明
- `encoding` 常用字符集：
  - `utf8mb4`：支持完整 Unicode（包括 emoji），推荐使用
  - `utf8`：旧版 UTF-8（不支持 4 字节字符）
  - `latin1`：西欧字符集（不推荐）
- `collation` 常用排序规则：
  - `utf8mb4_unicode_ci`：Unicode 标准排序（推荐）
  - `utf8mb4_general_ci`：简化排序（性能更好）
  - `utf8mb4_bin`：二进制排序（区分大小写）

## 适用场景

### 应用部署场景
- 自动创建应用所需的数据库
- 初始化数据库结构（导入 schema.sql）
- 设置统一的字符集和排序规则

### 数据迁移场景
- 导出生产数据库到测试环境
- 跨服务器数据库复制
- 数据库版本升级前的备份

### 开发测试场景
- 快速创建开发环境数据库
- 重置测试数据库到初始状态
- 清理废弃的测试数据库

## 安全注意事项

### 数据备份
1. **删除前备份**：执行 `state: absent` 前务必先导出数据
2. **测试恢复流程**：定期验证备份文件可以正常恢复
3. **版本控制**：将重要的 schema.sql 纳入版本控制
4. **异地备份**：备份文件存储在不同于数据库的服务器

### 凭证安全
1. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志
2. **Ansible Vault**：加密存储 `login_password`
3. **文件权限**：导出的 SQL 文件应设置严格的权限（600）

### 操作审计
1. **check_mode 预览**：重要操作前先用 `--check` 预览
2. **命名规范**：数据库命名遵循统一规范，避免冲突
3. **变更记录**：在 playbook 中添加详细的任务名称和注释

### 性能影响
1. **业务低峰期操作**：大型数据库导入导出建议在业务低峰期进行
2. **单事务导出**：使用 `single_transaction: true` 避免锁表
3. **分批处理**：超大数据库考虑分表分批导出

## 最佳实践

### 创建数据库示例
```yaml
- name: 创建应用数据库
  community.mysql.mysql_db:
    login_host: localhost
    login_user: root
    login_password: "{{ mysql_root_password }}"
    name: webapp_db
    encoding: utf8mb4
    collation: utf8mb4_unicode_ci
    state: present
  no_log: true
```

### 导入初始数据示例
```yaml
- name: 导入数据库 schema
  community.mysql.mysql_db:
    name: webapp_db
    state: import
    target: /path/to/schema.sql
  no_log: true
```

### 导出数据库示例
```yaml
- name: 导出数据库到备份文件
  community.mysql.mysql_db:
    name: webapp_db
    state: dump
    target: /backups/webapp_db_{{ ansible_date_time.iso8601_basic_short }}.sql
    single_transaction: true
    quick: true
  no_log: true
```

### 批量创建数据库示例
```yaml
- name: 创建多个测试数据库
  community.mysql.mysql_db:
    name: "{{ item }}"
    encoding: utf8mb4
    state: present
  loop:
    - test_db_1
    - test_db_2
    - test_db_3
  no_log: true
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置数据库连接信息和数据库名称
2. 使用 `--check` 模式预览数据库创建
3. 执行 playbook 创建数据库
4. 使用 `SHOW DATABASES;` 验证数据库已创建
5. 检查字符集：`SHOW CREATE DATABASE database_name;`
6. 测试导入导出功能

## 常见问题
- **连接失败**：检查 `login_host`、`login_port` 和防火墙规则
- **权限不足**：确认 `login_user` 具有 CREATE、DROP 权限
- **字符集不支持**：检查 MySQL 版本是否支持 utf8mb4
- **导入失败**：验证 SQL 文件格式和路径是否正确
- **导出文件过大**：考虑使用 `quick: true` 或分表导出

## 依赖说明
- **Ansible Collection**: `community.mysql`（使用 `ansible-galaxy collection install community.mysql` 安装）
- **Python 库**: PyMySQL 或 mysqlclient（在目标主机安装：`pip install PyMySQL`）
- **数据库权限**: 管理用户需要 CREATE、DROP、SELECT、INSERT 权限
- **mysqldump 工具**: 导出操作需要目标主机安装 mysqldump（通常随 MySQL 客户端安装）

## 相关示例
- [mysql_user 模块](../mysql_user/README.md) - MySQL 用户管理
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
- [存储模块](../../storage/README.md) - 数据库文件系统管理
- [备份策略](../../advanced/handlers_notify/README.md) - 自动化备份流程
