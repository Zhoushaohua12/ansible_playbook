# MySQL 主从复制管理模块使用指南

## 模块用途
`community.mysql.mysql_replication` 模块用于管理 MySQL 主从复制（Replication）配置和状态，支持启动/停止复制、获取复制状态、配置复制参数等操作。适用于高可用架构部署、数据库容灾、读写分离场景。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `mode` | str | 操作模式（必需） | `changeprimary`、`getprimary`、`getreplica`、`startreplica`、`stopreplica`、`resetprimary`、`resetreplica` 等 |
| `primary_host` | str | 主库主机地址（changeprimary 时必需） | `192.168.1.100`、`master.example.com` |
| `primary_port` | int | 主库端口（可选） | 3306 |
| `primary_user` | str | 复制用户（changeprimary 时必需） | `repl_user`、`replication` |
| `primary_password` | str | 复制密码（changeprimary 时必需） | 密码字符串 |
| `primary_log_file` | str | 主库 binlog 文件（可选） | `mysql-bin.000001` |
| `primary_log_pos` | int | 主库 binlog 位置（可选） | 154 |
| `login_host` | str | 目标 MySQL 主机 | `localhost`、`127.0.0.1` |
| `login_port` | int | 目标 MySQL 端口 | 3306 |
| `login_user` | str | 登录用户 | `root`、管理员用户 |
| `login_password` | str | 登录密码 | 密码字符串 |

## 高级参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `primary_ssl` | bool | 是否使用 SSL 连接主库 | true、false |
| `primary_ssl_ca` | str | SSL CA 证书路径 | `/etc/mysql/ca-cert.pem` |
| `primary_connect_retry` | int | 重连间隔秒数 | 60 |
| `primary_auto_position` | bool | 是否使用 GTID 自动定位 | true、false |
| `relay_log_file` | str | 中继日志文件 | `relay-bin.000001` |
| `relay_log_pos` | int | 中继日志位置 | 4 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了修改 | true/false |
| `queries` | 执行的 SQL 语句列表 | ["CHANGE MASTER TO ..."] |
| `Is_Slave` | 是否为从库 | true/false |
| `Master_Host` | 主库地址 | 192.168.1.100 |
| `Master_User` | 复制用户 | repl_user |
| `Master_Log_File` | 主库日志文件 | mysql-bin.000001 |
| `Read_Master_Log_Pos` | 读取主库日志位置 | 154 |
| `Slave_IO_Running` | IO 线程状态 | Yes/No |
| `Slave_SQL_Running` | SQL 线程状态 | Yes/No |
| `Seconds_Behind_Master` | 复制延迟秒数 | 0 |

## 使用情境

### 高可用架构
- **主从复制**：配置 MySQL 主从复制架构
- **故障转移**：主库故障时快速切换到从库
- **数据保护**：实时数据同步保护数据安全
- **灾难恢复**：异地灾备数据库配置

### 读写分离
- **负载均衡**：读操作分散到多个从库
- **性能优化**：减轻主库读压力
- **报表查询**：报表和分析查询使用从库
- **备份优化**：从从库执行备份操作

### 数据分发
- **多地部署**：数据同步到不同地域
- **CDN 源站**：内容分发网络数据源
- **数据仓库**：实时数据同步到分析系统
- **跨机房同步**：不同数据中心数据同步

## 安全注意事项

### 复制安全
1. **专用复制账号**：创建专用复制账号，最小权限原则
2. **SSL 加密传输**：启用 SSL 加密复制流量
3. **密码管理**：使用 Ansible Vault 加密存储复制密码
4. **访问控制**：限制复制账号访问源 IP

### 配置安全
1. **binlog 格式**：选择合适的 binlog 格式（ROW/STATEMENT/MIXED）
2. **GTID 模式**：推荐使用 GTID 模式简化管理
3. **半同步复制**：关键业务使用半同步复制
4. **复制过滤**：配置复制过滤规则避免误操作

### 操作安全
1. **状态监控**：持续监控复制状态和延迟
2. **数据一致性**：定期检查主从数据一致性
3. **binlog 管理**：合理配置 binlog 过期时间
4. **测试验证**：在测试环境验证复制配置

## 环境依赖

### 必需
- MySQL 5.7+ 或 MariaDB 10.2+
- Python MySQL 客户端库（PyMySQL 或 mysqlclient）
- community.mysql collection
- 复制账号和权限（REPLICATION SLAVE 权限）

### 推荐
- MySQL 主库启用 binlog
- 配置 server-id（主从不同）
- 配置 log_bin 和 binlog_format
- 启用 GTID（推荐）

### 外部依赖
- **Ansible Collection**: `community.mysql` (版本 >= 3.0.0)
- **Python 库**: PyMySQL >= 0.9.0 或 mysqlclient >= 1.3.0
- **MySQL 配置**: 主库必须启用 binlog，从库必须配置 server-id

## 常见问题

### 1. 复制无法启动
**可能原因**：
- 主库 binlog 未启用
- 复制账号权限不足
- 网络连接问题
- binlog 文件或位置错误

**解决方案**：
```bash
# 检查主库 binlog 状态
mysql -u root -p -e "SHOW BINARY LOGS;"

# 检查复制账号权限
mysql -u root -p -e "SHOW GRANTS FOR 'repl_user'@'%';"

# 检查从库复制状态
mysql -u root -p -e "SHOW SLAVE STATUS\G"

# 检查网络连接
telnet master_host 3306
```

### 2. 复制延迟过大
**可能原因**：
- 主库写入压力大
- 从库硬件性能不足
- 网络带宽不足
- 大事务导致延迟

**排查方法**：
```bash
# 检查复制延迟
mysql -u root -p -e "SHOW SLAVE STATUS\G" | grep Seconds_Behind_Master

# 检查 binlog 大小
mysql -u root -p -e "SHOW BINARY LOGS;"

# 检查当前执行的事务
mysql -u root -p -e "SHOW PROCESSLIST;"

# 查看复制线程状态
mysql -u root -p -e "SHOW SLAVE STATUS\G" | grep -E "Slave_IO_Running|Slave_SQL_Running"
```

### 3. IO 或 SQL 线程停止
**解决方案**：
```bash
# 查看错误信息
mysql -u root -p -e "SHOW SLAVE STATUS\G" | grep Last_Error

# 跳过一个错误事务
mysql -u root -p -e "SET GLOBAL sql_slave_skip_counter = 1; START SLAVE;"

# 重置复制配置
mysql -u root -p -e "STOP SLAVE; RESET SLAVE; CHANGE MASTER TO ..."

# 重启复制
mysql -u root -p -e "START SLAVE;"
```

### 4. 主从数据不一致
**解决方案**：
```bash
# 使用 pt-table-checksum 检查一致性
pt-table-checksum --host=master_host --databases=mydb

# 使用 pt-table-sync 修复不一致
pt-table-sync --execute --sync-to-master slave_host

# 重新初始化从库
mysqldump --master-data=2 --single-transaction --all-databases > dump.sql
# 在从库导入并配置复制
```

## 最佳实践

### 配置主从复制示例
```yaml
- name: 配置从库连接到主库
  community.mysql.mysql_replication:
    mode: changeprimary
    primary_host: "{{ mysql_master_host }}"
    primary_port: "{{ mysql_master_port }}"
    primary_user: "{{ mysql_repl_user }}"
    primary_password: "{{ mysql_repl_password }}"
    primary_log_file: "{{ mysql_binlog_file }}"
    primary_log_pos: "{{ mysql_binlog_pos }}"
    login_host: "{{ mysql_slave_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  no_log: true
  delegate_to: "{{ mysql_slave_host }}"
```

### 启动复制示例
```yaml
- name: 启动从库复制
  community.mysql.mysql_replication:
    mode: startreplica
    login_host: "{{ mysql_slave_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  no_log: true
  delegate_to: "{{ mysql_slave_host }}"
```

### 停止复制示例
```yaml
- name: 停止从库复制
  community.mysql.mysql_replication:
    mode: stopreplica
    login_host: "{{ mysql_slave_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  no_log: true
  delegate_to: "{{ mysql_slave_host }}"
```

### 获取复制状态示例
```yaml
- name: 获取从库复制状态
  community.mysql.mysql_replication:
    mode: getreplica
    login_host: "{{ mysql_slave_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  register: replica_status
  no_log: true
  delegate_to: "{{ mysql_slave_host }}"

- name: 显示复制状态
  ansible.builtin.debug:
    msg: |
      IO 线程状态: {{ replica_status.Slave_IO_Running }}
      SQL 线程状态: {{ replica_status.Slave_SQL_Running }}
      复制延迟: {{ replica_status.Seconds_Behind_Master }} 秒
```

### 获取主库状态示例
```yaml
- name: 获取主库 binlog 位置
  community.mysql.mysql_replication:
    mode: getprimary
    login_host: "{{ mysql_master_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  register: master_status
  no_log: true
  delegate_to: "{{ mysql_master_host }}"

- name: 显示主库状态
  ansible.builtin.debug:
    msg: |
      Binlog 文件: {{ master_status.File }}
      Binlog 位置: {{ master_status.Position }}
```

### 使用 GTID 模式配置复制示例
```yaml
- name: 配置从库使用 GTID 模式
  community.mysql.mysql_replication:
    mode: changeprimary
    primary_host: "{{ mysql_master_host }}"
    primary_user: "{{ mysql_repl_user }}"
    primary_password: "{{ mysql_repl_password }}"
    primary_auto_position: yes
    login_host: "{{ mysql_slave_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  no_log: true
  delegate_to: "{{ mysql_slave_host }}"
```

### 复制状态监控示例
```yaml
- name: 检查复制状态
  community.mysql.mysql_replication:
    mode: getreplica
    login_host: "{{ mysql_slave_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  register: repl_status
  no_log: true
  delegate_to: "{{ mysql_slave_host }}"

- name: 告警复制异常
  ansible.builtin.fail:
    msg: "复制异常: IO={{ repl_status.Slave_IO_Running }}, SQL={{ repl_status.Slave_SQL_Running }}"
  when: 
    - repl_status.Slave_IO_Running != "Yes"
    - repl_status.Slave_SQL_Running != "Yes"

- name: 告警复制延迟
  ansible.builtin.debug:
    msg: "警告: 复制延迟 {{ repl_status.Seconds_Behind_Master }} 秒"
  when: repl_status.Seconds_Behind_Master | int > 60
```

### 重置复制配置示例
```yaml
- name: 停止从库复制
  community.mysql.mysql_replication:
    mode: stopreplica
    login_host: "{{ mysql_slave_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  no_log: true
  delegate_to: "{{ mysql_slave_host }}"

- name: 重置从库复制配置
  community.mysql.mysql_replication:
    mode: resetreplica
    login_host: "{{ mysql_slave_host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  no_log: true
  delegate_to: "{{ mysql_slave_host }}"
```

### 批量配置多从库示例
```yaml
- name: 批量配置从库复制
  community.mysql.mysql_replication:
    mode: changeprimary
    primary_host: "{{ mysql_master_host }}"
    primary_user: "{{ mysql_repl_user }}"
    primary_password: "{{ mysql_repl_password }}"
    primary_log_file: "{{ mysql_binlog_file }}"
    primary_log_pos: "{{ mysql_binlog_pos }}"
    login_host: "{{ item.host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  no_log: true
  loop: "{{ mysql_slaves }}"
  loop_control:
    label: "{{ item.host }}"
  delegate_to: "{{ item.host }}"

- name: 批量启动从库复制
  community.mysql.mysql_replication:
    mode: startreplica
    login_host: "{{ item.host }}"
    login_user: "{{ mysql_admin_user }}"
    login_password: "{{ mysql_admin_password }}"
  no_log: true
  loop: "{{ mysql_slaves }}"
  loop_control:
    label: "{{ item.host }}"
  delegate_to: "{{ item.host }}"
```

## 相关示例
- [mysql_user 模块](../mysql_user/README.md) - MySQL 用户权限管理
- [mysql_db 模块](../mysql_db/README.md) - MySQL 数据库管理
- [监控模块](../../monitoring/README.md) - 数据库监控配置
