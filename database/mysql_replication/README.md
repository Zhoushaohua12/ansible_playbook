# mysql_replication 模块使用指南

## 模块用途
`community.mysql.mysql_replication` 模块用于管理 MySQL 和 MariaDB 的主从复制配置。可以启动、停止、重置复制，获取主服务器和从服务器状态，配置复制参数等。适用于自动化搭建主从复制、故障切换、读写分离架构等场景。

## 主要参数

### 连接参数
- `login_host`：MySQL 服务器地址（默认 localhost）
- `login_port`：MySQL 服务器端口（默认 3306）
- `login_user`：管理员用户名（用于连接和执行操作）
- `login_password`：管理员密码（建议使用 Ansible Vault 加密）
- `login_unix_socket`：Unix socket 文件路径（替代 TCP 连接）

### 复制模式参数
- `mode`：操作模式（必需）
  - `getprimary` / `getmaster` - 获取主服务器状态
  - `getreplica` / `getslave` - 获取从服务器状态
  - `changeprimary` / `changemaster` - 配置从服务器连接到主服务器
  - `startreplica` / `startslave` - 启动复制
  - `stopreplica` / `stopslave` - 停止复制
  - `resetprimary` / `resetmaster` - 重置主服务器
  - `resetreplica` / `resetslave` - 重置从服务器

### 主服务器配置参数
- `master_host`：主服务器地址
- `master_user`：复制用户名
- `master_password`：复制用户密码
- `master_port`：主服务器端口（默认 3306）
- `master_log_file`：主服务器 binlog 文件名
- `master_log_pos`：主服务器 binlog 位置
- `master_connect_retry`：连接失败重试间隔（秒）
- `master_ssl`：是否使用 SSL 连接主服务器
- `master_ssl_ca`：SSL CA 证书路径
- `master_ssl_cert`：SSL 客户端证书路径
- `master_ssl_key`：SSL 客户端密钥路径

### GTID 复制参数
- `master_auto_position`：是否使用 GTID 自动定位（true/false）
- `master_use_gtid`：GTID 模式（current_pos、slave_pos、no，MariaDB 专用）

### 其他参数
- `relay_log_file`：中继日志文件名
- `relay_log_pos`：中继日志位置
- `master_delay`：复制延迟时间（秒，用于延迟复制）

## 返回值
- `changed`：复制配置是否发生变更
- `queries`：执行的 SQL 语句列表
- 主服务器状态（mode=getprimary）：
  - `File`：当前 binlog 文件名
  - `Position`：当前 binlog 位置
  - `Binlog_Do_DB`：需要复制的数据库
  - `Binlog_Ignore_DB`：忽略复制的数据库
- 从服务器状态（mode=getreplica）：
  - `Slave_IO_Running`：IO 线程状态
  - `Slave_SQL_Running`：SQL 线程状态
  - `Seconds_Behind_Master`：复制延迟（秒）
  - `Master_Log_File`：主服务器 binlog 文件
  - `Read_Master_Log_Pos`：读取的主服务器位置
  - `Exec_Master_Log_Pos`：执行的主服务器位置

## 常见字段说明
- `mode` 操作模式：
  - `getprimary` - 在主服务器上执行，获取 binlog 位置信息
  - `getreplica` - 在从服务器上执行，获取复制状态
  - `changeprimary` - 在从服务器上执行，配置主服务器信息
  - `startreplica` - 在从服务器上执行，启动复制线程
  - `stopreplica` - 在从服务器上执行，停止复制线程

- GTID vs 传统复制：
  - 传统复制：需要指定 `master_log_file` 和 `master_log_pos`
  - GTID 复制：设置 `master_auto_position: true`，无需指定位置

## 适用场景

### 主从复制搭建
- 自动化配置 MySQL 主从复制环境
- 批量部署多个从服务器
- 实现读写分离架构

### 高可用架构
- 主从切换和故障转移
- 配置半同步复制提高数据可靠性
- 实现多层级复制拓扑

### 数据备份
- 使用延迟复制（master_delay）实现时间点恢复
- 从服务器用于备份，减轻主服务器负载
- 实现跨数据中心数据同步

### 监控和维护
- 定期检查复制状态
- 监控复制延迟
- 自动修复复制错误

## 安全注意事项

### 凭证安全
1. **禁止硬编码密码**：使用 Ansible Vault 加密 `login_password` 和 `master_password`
2. **使用 no_log**：设置 `no_log: true` 防止密码记录到日志文件
3. **复制用户权限**：复制用户仅需 REPLICATION SLAVE 权限
4. **定期更新密码**：建立定期更新复制用户密码的流程

### 连接安全
1. **使用 SSL**：生产环境配置 `master_ssl` 加密复制连接
2. **限制访问源**：在主服务器防火墙限制从服务器 IP
3. **专用复制用户**：创建专门的复制用户，限制连接来源
4. **绑定地址**：配置 bind-address 限制监听地址

### 数据一致性
1. **GTID 复制**：推荐使用 GTID 模式，避免位置错误
2. **半同步复制**：关键业务启用半同步复制
3. **检查延迟**：定期监控 `Seconds_Behind_Master`
4. **避免写从库**：从服务器配置为只读（read_only=1）

### 操作审计
1. **版本控制**：将复制配置 playbook 纳入 Git 管理
2. **变更记录**：在 playbook 中添加详细的任务名称和注释
3. **测试先行**：在测试环境验证复制配置

## 最佳实践

### 获取主服务器状态示例
```yaml
- name: 获取主服务器 binlog 位置
  community.mysql.mysql_replication:
    login_host: master.example.com
    login_user: root
    login_password: "{{ mysql_root_password }}"
    mode: getprimary
  no_log: true
  register: master_status
```

### 配置从服务器（传统复制）示例
```yaml
- name: 配置从服务器连接到主服务器
  community.mysql.mysql_replication:
    login_host: slave.example.com
    login_user: root
    login_password: "{{ mysql_root_password }}"
    mode: changeprimary
    master_host: master.example.com
    master_user: replicator
    master_password: "{{ replication_password }}"
    master_log_file: "{{ master_status.File }}"
    master_log_pos: "{{ master_status.Position }}"
  no_log: true
```

### 配置从服务器（GTID 复制）示例
```yaml
- name: 配置从服务器使用 GTID 复制
  community.mysql.mysql_replication:
    login_host: slave.example.com
    login_user: root
    login_password: "{{ mysql_root_password }}"
    mode: changeprimary
    master_host: master.example.com
    master_user: replicator
    master_password: "{{ replication_password }}"
    master_auto_position: true
  no_log: true
```

### 启动复制示例
```yaml
- name: 启动从服务器复制
  community.mysql.mysql_replication:
    login_host: slave.example.com
    login_user: root
    login_password: "{{ mysql_root_password }}"
    mode: startreplica
  no_log: true
```

### 检查复制状态示例
```yaml
- name: 检查从服务器复制状态
  community.mysql.mysql_replication:
    login_host: slave.example.com
    login_user: root
    login_password: "{{ mysql_root_password }}"
    mode: getreplica
  no_log: true
  register: replica_status

- name: 验证复制线程运行正常
  ansible.builtin.assert:
    that:
      - replica_status.Slave_IO_Running == "Yes"
      - replica_status.Slave_SQL_Running == "Yes"
    fail_msg: "复制线程未运行，请检查错误日志"
```

### 配置 SSL 复制示例
```yaml
- name: 配置 SSL 加密复制
  community.mysql.mysql_replication:
    login_host: slave.example.com
    login_user: root
    login_password: "{{ mysql_root_password }}"
    mode: changeprimary
    master_host: master.example.com
    master_user: replicator
    master_password: "{{ replication_password }}"
    master_ssl: true
    master_ssl_ca: /etc/mysql/ssl/ca.pem
    master_ssl_cert: /etc/mysql/ssl/client-cert.pem
    master_ssl_key: /etc/mysql/ssl/client-key.pem
    master_auto_position: true
  no_log: true
```

## 测试步骤
1. 在主服务器创建复制用户
2. 获取主服务器 binlog 位置或确保 GTID 已启用
3. 在从服务器配置复制参数
4. 启动复制并检查状态
5. 在主服务器写入测试数据，验证从服务器同步
6. 监控复制延迟和错误日志

## 常见问题
- **连接失败**：检查主从服务器网络连通性和防火墙规则
- **复制用户权限不足**：确认复制用户具有 REPLICATION SLAVE 权限
- **位置错误**：使用 GTID 复制避免位置问题，或重新获取正确位置
- **复制延迟**：检查从服务器性能、网络带宽、慢查询
- **SSL 连接失败**：验证证书路径和权限，检查主服务器 SSL 配置

## 依赖说明
- **Ansible Collection**: `community.mysql`（使用 `ansible-galaxy collection install community.mysql` 安装）
- **Python 库**: PyMySQL 或 mysqlclient（在目标主机安装：`pip install PyMySQL`）
- **数据库权限**: 主服务器需要 REPLICATION MASTER 权限，从服务器需要 SUPER 或 REPLICATION CLIENT 权限
- **MySQL 配置**: 主服务器启用 binlog，从服务器配置 server-id

## 相关示例
- [mysql_user 模块](../mysql_user/README.md) - MySQL 用户管理（创建复制用户）
- [mysql_db 模块](../mysql_db/README.md) - MySQL 数据库管理
- [postgresql_db 模块](../postgresql_db/README.md) - PostgreSQL 数据库管理
- [监控模块](../../monitoring/README.md) - 配合复制监控使用
