# 数据库操作包 (Database Operations Pack)

⚠️ **教学声明**：本目录包含用于学习和演示的数据库自动化 playbook，涵盖 MySQL/MariaDB 和 PostgreSQL 的安装、配置、复制和备份。请在测试环境充分验证后再应用于生产。

## 目录结构

```
database/
├── README.md                      # 本文档
├── vars/
│   └── default.yml               # 变量配置文件
├── templates/                    # Jinja2 模板文件
│   ├── my.cnf.j2                # MySQL/MariaDB 配置模板
│   ├── replication.cnf.j2       # MySQL 复制配置模板
│   ├── mysql_backup.sh.j2       # MySQL 备份脚本模板
│   ├── postgresql.conf.j2       # PostgreSQL 配置模板
│   ├── pg_hba.conf.j2          # PostgreSQL 认证配置模板
│   ├── postgresql_backup.sh.j2  # PostgreSQL 备份脚本模板
│   ├── postgresql_backup_cleanup.sh.j2  # 备份清理脚本
│   ├── pgpass.j2               # PostgreSQL 密码文件
│   └── recovery.conf.j2        # PostgreSQL 恢复配置（<12）
├── handlers/
│   └── main.yml                # 服务处理程序
├── roles/                      # Ansible 角色
│   ├── mysql_common/          # MySQL 通用安装角色
│   ├── mysql_replication/     # MySQL 复制角色
│   ├── postgresql_common/     # PostgreSQL 通用安装角色
│   └── postgresql_backup/     # PostgreSQL 备份角色
├── mysql-5.7-install.yml      # MySQL 5.7 安装 playbook
├── mysql-8.0-install.yml      # MySQL 8.0 安装 playbook
├── mysql-master-slave.yml     # MySQL 主从复制 playbook
├── postgresql-install.yml     # PostgreSQL 安装 playbook
└── postgresql-backup.yml      # PostgreSQL 备份 playbook
```

## 功能特性

### MySQL/MariaDB 支持
- ✅ MySQL 5.7 和 8.0 安装
- ✅ MariaDB 兼容支持
- ✅ 主从复制（传统和 GTID 模式）
- ✅ 逻辑备份（mysqldump）
- ✅ 用户和数据库管理
- ✅ 性能调优配置
- ✅ SSL/TLS 加密支持

### PostgreSQL 支持
- ✅ PostgreSQL 12-16 安装
- ✅ 流复制配置
- ✅ 逻辑备份（pg_dump）
- ✅ 物理备份（pg_basebackup）
- ✅ WAL 归档
- ✅ 用户和数据库管理
- ✅ 性能调优配置
- ✅ SSL/TLS 加密支持

## 支持的操作系统

| 操作系统 | 版本 | MySQL 5.7 | MySQL 8.0 | MariaDB | PostgreSQL |
|---------|------|-----------|-----------|---------|------------|
| CentOS/RHEL | 7, 8, 9 | ✅ | ✅ | ✅ | ✅ |
| Ubuntu | 20.04, 22.04 | ✅ | ✅ | ✅ | ✅ |
| Debian | 10, 11, 12 | ✅ | ✅ | ✅ | ✅ |

## 快速开始

### 前置要求

1. **Ansible 版本**：>= 2.9
2. **必需的 Ansible Collections**：
   ```bash
   ansible-galaxy collection install community.mysql
   ansible-galaxy collection install community.postgresql
   ansible-galaxy collection install community.general
   ansible-galaxy collection install ansible.posix
   ```

3. **目标主机要求**：
   - Python 3.6+
   - sudo 权限
   - 至少 2GB RAM（推荐 4GB+）
   - 至少 20GB 磁盘空间

### 安装 MySQL 8.0

1. 配置主机清单文件 (`inventory/hosts.ini`)：
   ```ini
   [mysql_servers]
   mysql01 ansible_host=192.168.1.10
   ```

2. 编辑变量文件 `vars/default.yml`：
   ```yaml
   mysql_enabled: true
   mysql_version: "8.0"
   mysql_root_password: "YourSecurePassword123!"
   ```

3. 运行 playbook：
   ```bash
   # 语法检查
   ansible-playbook -i inventory/hosts.ini mysql-8.0-install.yml --syntax-check
   
   # 检查模式（不实际执行）
   ansible-playbook -i inventory/hosts.ini mysql-8.0-install.yml --check
   
   # 实际执行
   ansible-playbook -i inventory/hosts.ini mysql-8.0-install.yml
   ```

### 配置 MySQL 主从复制

1. 配置主机清单：
   ```ini
   [mysql_replication_servers]
   mysql-master ansible_host=192.168.1.10
   mysql-slave1 ansible_host=192.168.1.11
   mysql-slave2 ansible_host=192.168.1.12
   ```

2. 配置变量：
   ```yaml
   mysql_replication_enabled: true
   mysql_gtid_mode: "ON"
   
   # 主服务器变量
   mysql_server_id: 1
   mysql_replication_role: "master"
   
   # 从服务器变量（在 host_vars 或 group_vars 中设置）
   # mysql_server_id: 2  # 每台从服务器使用不同的 ID
   # mysql_replication_role: "slave"
   # mysql_replication_master_host: "192.168.1.10"
   ```

3. 运行复制配置：
   ```bash
   # 仅配置主服务器
   ansible-playbook -i inventory/hosts.ini mysql-master-slave.yml --limit mysql-master
   
   # 配置从服务器
   ansible-playbook -i inventory/hosts.ini mysql-master-slave.yml --limit mysql-slave1
   
   # 使用标签仅执行复制相关任务
   ansible-playbook -i inventory/hosts.ini mysql-master-slave.yml --tags replication
   ```

### 安装 PostgreSQL

1. 配置主机清单：
   ```ini
   [postgresql_servers]
   pg01 ansible_host=192.168.1.20
   ```

2. 配置变量：
   ```yaml
   postgresql_enabled: true
   postgresql_version: "15"
   postgresql_admin_password: "YourSecurePassword123!"
   ```

3. 运行 playbook：
   ```bash
   ansible-playbook -i inventory/hosts.ini postgresql-install.yml
   ```

### 配置 PostgreSQL 备份

```bash
# 配置备份策略
ansible-playbook -i inventory/hosts.ini postgresql-backup.yml

# 手动执行备份测试
ansible -i inventory/hosts.ini postgresql_servers -m command \
  -a "/usr/local/bin/postgresql_backup.sh test" -b
```

## 配置参数说明

### MySQL/MariaDB 配置

#### 基础配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `mysql_enabled` | `true` | 是否启用 MySQL |
| `mysql_version` | `"8.0"` | MySQL 版本（5.7/8.0） |
| `mariadb_enabled` | `false` | 是否使用 MariaDB 替代 MySQL |
| `mysql_port` | `3306` | MySQL 监听端口 |
| `mysql_bind_address` | `"0.0.0.0"` | 监听地址 |
| `mysql_data_dir` | `"/var/lib/mysql"` | 数据目录 |
| `mysql_character_set` | `"utf8mb4"` | 默认字符集 |

#### 性能调优参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `mysql_max_connections` | `200` | 最大连接数 |
| `mysql_innodb_buffer_pool_size` | `"1G"` | InnoDB 缓冲池大小 |
| `mysql_innodb_log_file_size` | `"256M"` | InnoDB 日志文件大小 |
| `mysql_query_cache_size` | `0` | 查询缓存大小（8.0 已移除） |

#### 复制配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `mysql_replication_enabled` | `false` | 是否启用复制 |
| `mysql_replication_role` | `"master"` | 服务器角色（master/slave） |
| `mysql_server_id` | `1` | 服务器唯一 ID |
| `mysql_gtid_mode` | `"ON"` | 是否启用 GTID |
| `mysql_binlog_format` | `"ROW"` | 二进制日志格式 |

#### 备份配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `mysql_backup_enabled` | `true` | 是否启用备份 |
| `mysql_backup_dir` | `"/backup/mysql"` | 备份目录 |
| `mysql_backup_retention_days` | `7` | 备份保留天数 |
| `mysql_backup_cron_hour` | `"2"` | 备份执行时间（小时） |
| `mysql_backup_compress` | `true` | 是否压缩备份 |

### PostgreSQL 配置

#### 基础配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `postgresql_enabled` | `true` | 是否启用 PostgreSQL |
| `postgresql_version` | `"15"` | PostgreSQL 版本 |
| `postgresql_port` | `5432` | PostgreSQL 监听端口 |
| `postgresql_listen_addresses` | `"*"` | 监听地址 |
| `postgresql_encoding` | `"UTF8"` | 默认编码 |

#### 性能调优参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `postgresql_max_connections` | `200` | 最大连接数 |
| `postgresql_shared_buffers` | `"256MB"` | 共享缓冲区大小 |
| `postgresql_effective_cache_size` | `"1GB"` | 有效缓存大小 |
| `postgresql_work_mem` | `"4MB"` | 工作内存 |

#### 复制配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `postgresql_replication_enabled` | `false` | 是否启用复制 |
| `postgresql_replication_role` | `"primary"` | 服务器角色 |
| `postgresql_wal_level` | `"replica"` | WAL 级别 |
| `postgresql_max_wal_senders` | `10` | 最大 WAL 发送进程数 |

#### 备份配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `postgresql_backup_enabled` | `true` | 是否启用备份 |
| `postgresql_backup_dir` | `"/backup/postgresql"` | 备份目录 |
| `postgresql_backup_type` | `"logical"` | 备份类型（logical/basebackup） |
| `postgresql_backup_format` | `"custom"` | 备份格式 |
| `postgresql_wal_archive_enabled` | `false` | 是否启用 WAL 归档 |

## 安全最佳实践

### 密码管理

**强烈建议**使用 Ansible Vault 加密敏感变量：

1. 创建加密的变量文件：
   ```bash
   ansible-vault create vars/vault.yml
   ```

2. 添加敏感变量：
   ```yaml
   vault_mysql_root_password: "YourSecurePassword123!"
   vault_postgresql_admin_password: "YourSecurePassword456!"
   ```

3. 在 playbook 中引用：
   ```bash
   ansible-playbook -i inventory/hosts.ini mysql-8.0-install.yml --ask-vault-pass
   ```

### 防火墙配置

playbook 会自动配置防火墙规则（如果启用）：

- MySQL/MariaDB: 端口 3306
- PostgreSQL: 端口 5432

**生产环境建议**：
- 限制数据库访问的 IP 范围
- 使用内网 IP 进行数据库通信
- 启用 SSL/TLS 加密

### SSL/TLS 配置

启用 SSL/TLS 加密：

```yaml
# MySQL
mysql_ssl_enabled: true
mysql_ssl_ca: "/etc/mysql/ssl/ca-cert.pem"
mysql_ssl_cert: "/etc/mysql/ssl/server-cert.pem"
mysql_ssl_key: "/etc/mysql/ssl/server-key.pem"

# PostgreSQL
postgresql_ssl_enabled: true
postgresql_ssl_cert_file: "/etc/postgresql/ssl/server.crt"
postgresql_ssl_key_file: "/etc/postgresql/ssl/server.key"
```

## 使用标签

playbook 支持多个标签，可以选择性执行任务：

```bash
# 仅执行安装任务
ansible-playbook mysql-8.0-install.yml --tags packages

# 仅执行配置任务
ansible-playbook mysql-8.0-install.yml --tags config

# 仅执行复制相关任务
ansible-playbook mysql-master-slave.yml --tags replication

# 跳过防火墙配置
ansible-playbook postgresql-install.yml --skip-tags firewall

# 仅执行验证任务
ansible-playbook mysql-8.0-install.yml --tags verify
```

可用标签：
- `mysql`, `mariadb`, `postgresql` - 数据库类型
- `packages` - 包安装
- `config` - 配置文件
- `service` - 服务管理
- `databases` - 数据库创建
- `users` - 用户管理
- `replication` - 复制配置
- `backup` - 备份配置
- `firewall` - 防火墙配置
- `verify` - 验证测试

## 故障排查

### MySQL 常见问题

#### 1. 服务启动失败

```bash
# 检查服务状态
systemctl status mysqld

# 查看错误日志
tail -f /var/log/mysql/error.log

# 验证配置文件
mysqld --validate-config
```

#### 2. 复制延迟

```bash
# 在从服务器上检查复制状态
mysql -u root -p -e "SHOW SLAVE STATUS\G"

# 检查复制延迟
mysql -u root -p -e "SHOW SLAVE STATUS\G" | grep Seconds_Behind_Master
```

#### 3. 连接问题

检查事项：
- 防火墙规则是否正确
- `bind_address` 配置
- 用户权限和主机匹配
- SELinux 设置（RedHat/CentOS）

### PostgreSQL 常见问题

#### 1. 服务启动失败

```bash
# 检查服务状态
systemctl status postgresql-15

# 查看日志
tail -f /var/lib/pgsql/15/data/log/postgresql-*.log
```

#### 2. 认证失败

检查 `pg_hba.conf` 配置：
```bash
# 查看配置
cat /var/lib/pgsql/15/data/pg_hba.conf

# 重新加载配置
sudo -u postgres psql -c "SELECT pg_reload_conf();"
```

#### 3. 连接限制

```bash
# 检查当前连接数
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# 检查最大连接数
sudo -u postgres psql -c "SHOW max_connections;"
```

### SELinux 问题（RedHat/CentOS）

如果遇到 SELinux 相关问题：

```bash
# 检查 SELinux 状态
getenforce

# 临时禁用 SELinux（仅用于测试）
setenforce 0

# 查看 SELinux 拒绝日志
ausearch -m avc -ts recent

# 允许数据库服务
setsebool -P mysql_connect_any 1
setsebool -P postgresql_selinux_transmit_client_label 1
```

## MariaDB 支持说明

本 playbook 完全支持 MariaDB。要使用 MariaDB 而非 MySQL：

```yaml
# 在 vars/default.yml 中设置
mariadb_enabled: true
mysql_enabled: false
mariadb_version: "10.11"
```

主要区别：
- 包名不同（自动处理）
- 服务名称为 `mariadb`
- 配置文件位置相同
- 复制和备份功能完全兼容

## 监控建议

### MySQL 监控指标

- 连接数：`SHOW STATUS LIKE 'Threads_connected';`
- QPS：`SHOW STATUS LIKE 'Questions';`
- 复制延迟：`SHOW SLAVE STATUS;`
- InnoDB 缓冲池：`SHOW STATUS LIKE 'Innodb_buffer_pool%';`

### PostgreSQL 监控指标

- 连接数：`SELECT count(*) FROM pg_stat_activity;`
- 数据库大小：`SELECT pg_size_pretty(pg_database_size('database_name'));`
- 复制延迟：`SELECT pg_last_wal_receive_lsn() - pg_last_wal_replay_lsn();`
- 缓存命中率：`SELECT sum(blks_hit)*100/sum(blks_hit+blks_read) FROM pg_stat_database;`

## 备份和恢复

### MySQL 备份恢复

```bash
# 恢复单个数据库
mysql -u root -p dbname < backup_file.sql

# 恢复所有数据库
mysql -u root -p < all_databases.sql

# 恢复压缩备份
gunzip < backup_file.sql.gz | mysql -u root -p dbname
```

### PostgreSQL 备份恢复

```bash
# 恢复 plain 格式备份
psql -U postgres dbname < backup_file.sql

# 恢复 custom 格式备份
pg_restore -U postgres -d dbname backup_file.dump

# 恢复物理备份（需要停止服务）
systemctl stop postgresql-15
rm -rf /var/lib/pgsql/15/data/*
tar -xzf basebackup.tar.gz -C /var/lib/pgsql/15/data/
systemctl start postgresql-15
```

## 性能调优建议

### MySQL 调优

1. **InnoDB 缓冲池**：设置为可用内存的 70-80%
2. **连接数**：根据实际并发调整 `max_connections`
3. **二进制日志**：生产环境启用，开发环境可禁用
4. **慢查询日志**：启用以识别性能问题

### PostgreSQL 调优

1. **共享缓冲区**：设置为可用内存的 25%
2. **有效缓存**：设置为可用内存的 50-75%
3. **工作内存**：根据查询复杂度调整
4. **检查点**：调整以平衡性能和恢复时间

## 扩展阅读

- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [MariaDB 官方文档](https://mariadb.com/kb/en/)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Ansible MySQL Collection](https://docs.ansible.com/ansible/latest/collections/community/mysql/)
- [Ansible PostgreSQL Collection](https://docs.ansible.com/ansible/latest/collections/community/postgresql/)

## 许可证

MIT License

## 贡献

欢迎提交问题报告和改进建议！

---

**最后更新**: 2024
**维护者**: Ansible Automation Team
