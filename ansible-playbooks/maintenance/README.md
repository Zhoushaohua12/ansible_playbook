# 维护策略 Ansible Playbooks

本目录包含用于系统维护和备份策略的 Ansible playbooks，提供完整的自动化备份、恢复和监控解决方案。

## 📋 目录结构

```
maintenance/
├── backup-strategy.yml         # 备份策略配置与执行
├── vars/
│   └── default.yml             # 默认变量配置
├── templates/
│   ├── filesystem_backup.sh.j2 # 文件系统备份脚本
│   ├── database_backup.sh.j2   # 数据库备份脚本
│   ├── cloud_sync.sh.j2        # 云同步脚本
│   ├── backup_verify.sh.j2     # 备份验证脚本
│   ├── backup_cleanup.sh.j2     # 备份清理脚本
│   ├── backup_monitor.sh.j2     # 备份监控脚本
│   ├── backup_notify.sh.j2      # 备份通知脚本
│   ├── backup_restore.sh.j2     # 备份恢复脚本
│   └── ...                     # 其他配置模板
├── roles/
│   ├── filesystem_backup/       # 文件系统备份角色
│   │   ├── tasks/             # 任务文件
│   │   ├── templates/         # 模板文件
│   │   └── handlers/          # 处理程序
│   ├── database_backup/        # 数据库备份角色
│   │   ├── tasks/             # 任务文件
│   │   ├── templates/         # 模板文件
│   │   └── handlers/          # 处理程序
│   └── cloud_sync/             # 云同步角色
│       ├── tasks/             # 任务文件
│       ├── templates/         # 模板文件
│       └── handlers/          # 处理程序
└── README.md                  # 本文档
```

## 🚀 快速开始

### 1. 备份策略部署

```bash
# 语法检查
ansible-playbook --syntax-check backup-strategy.yml

# 干运行（检查模式）
ansible-playbook --check backup-strategy.yml

# 执行备份策略部署
ansible-playbook backup-strategy.yml

# 仅配置文件系统备份
ansible-playbook backup-strategy.yml --tags "filesystem"

# 仅配置数据库备份
ansible-playbook backup-strategy.yml --tags "database"

# 仅配置云同步
ansible-playbook backup-strategy.yml --tags "cloud_sync"

# 仅配置定时任务
ansible-playbook backup-strategy.yml --tags "cron"
```

**功能特性：**
- 文件系统增量备份
- 多数据库引擎支持（MySQL、PostgreSQL、MongoDB）
- 多云平台同步（AWS S3、阿里云 OSS、Azure Blob）
- 自动备份验证和清理
- 灵活的保留策略
- 备份监控和通知
- 加密和压缩支持

## ⚙️ 配置说明

### 主要变量配置

编辑 `vars/default.yml` 文件来自定义备份策略：

```yaml
# 通用备份配置
backup_enabled: true
backup_base_dir: "/opt/backups"
backup_retention_days: 30
backup_compression: true
backup_encryption: false

# 文件系统备份配置
filesystem_backup_enabled: true
filesystem_backup_sources:
  - path: "/etc"
    description: "系统配置文件"
    retention_days: 90
  - path: "/home"
    description: "用户目录"
    retention_days: 30

# 数据库备份配置
database_backup_enabled: true
database_backup_engines:
  - engine: "mysql"
    enabled: true
    databases: ["--all-databases"]
    retention_days: 30

# 云同步配置
cloud_sync_enabled: true
cloud_sync_providers:
  - provider: "aws_s3"
    enabled: false
    bucket_name: "my-backup-bucket"
    retention_days: 90
```

### 文件系统备份配置

支持多种备份方法：

- **rsync**：增量同步，适合大文件
- **tar**：压缩归档，适合小文件
- **dd**：块级备份，适合整个磁盘

```yaml
filesystem_backup_sources:
  - path: "/var/www"
    description: "Web 应用目录"
    exclude_patterns:
      - "*.log"
      - "cache/*"
    retention_days: 60
```

### 数据库备份配置

支持多种数据库引擎：

- **MySQL**：mysqldump 工具
- **PostgreSQL**：pg_dump 工具
- **MongoDB**：mongodump 工具

```yaml
database_backup_engines:
  - engine: "mysql"
    enabled: true
    databases: ["wordpress", "mediawiki"]
    username: "backup_user"
    password: "{{ vault_mysql_password }}"
    options: "--single-transaction --routines"
    compression: true
```

### 云同步配置

支持多个云服务提供商：

- **AWS S3**：对象存储服务
- **阿里云 OSS**：对象存储服务
- **Azure Blob**：块存储服务

```yaml
cloud_sync_providers:
  - provider: "aws_s3"
    enabled: true
    bucket_name: "my-backup-bucket"
    region: "us-east-1"
    access_key: "{{ vault_aws_access_key }}"
    secret_key: "{{ vault_aws_secret_key }}"
    storage_class: "STANDARD_IA"
```

## 🖥️ 操作系统支持

| 操作系统 | 版本 | 支持状态 |
|---------|------|----------|
| Ubuntu | 20.04 LTS | ✅ 完全支持 |
| Ubuntu | 22.04 LTS | ✅ 完全支持 |
| Debian | 10 (Buster) | ✅ 完全支持 |
| Debian | 11 (Bullseye) | ✅ 完全支持 |
| CentOS | 7 | ✅ 完全支持 |
| CentOS | 8 | ✅ 完全支持 |
| RHEL | 8 | ✅ 完全支持 |

## 📦 依赖要求

### Ansible 要求
- Ansible >= 2.9
- Python >= 3.6

### 系统依赖
```bash
# Ubuntu/Debian
apt-get install rsync tar gzip openssl bc jq awscli python3-pip

# CentOS/RHEL
yum install rsync tar gzip openssl bc jq awscli python3-pip
```

### Python 依赖
```bash
pip3 install boto3 botocore aliyun-oss2 azure-storage-blob requests
```

### 数据库客户端
```bash
# MySQL
apt-get install mysql-client

# PostgreSQL
apt-get install postgresql-client

# MongoDB
apt-get install mongodb-clients
```

## 🏷️ 标签使用

所有 playbooks 都支持标签进行选择性执行：

| 标签 | 描述 |
|------|------|
| `filesystem` | 文件系统备份相关任务 |
| `database` | 数据库备份相关任务 |
| `cloud_sync` | 云同步相关任务 |
| `verification` | 备份验证相关任务 |
| `cleanup` | 备份清理相关任务 |
| `monitoring` | 备份监控相关任务 |
| `notification` | 通知相关任务 |
| `cron` | 定时任务配置 |
| `packages` | 软件包安装 |
| `scripts` | 脚本部署 |
| `config` | 配置文件部署 |
| `test` | 测试和验证 |
| `aws` | AWS 相关配置 |
| `aliyun` | 阿里云相关配置 |
| `azure` | Azure 相关配置 |

## 🔧 故障排除

### 常见问题

1. **备份脚本执行失败**
   ```bash
   # 检查脚本权限
   ls -la /opt/backups/scripts/
   
   # 手动执行测试
   sudo -u backup /opt/backups/scripts/filesystem_backup.sh --test
   
   # 查看日志
   tail -f /var/log/backups/filesystem_backup_*.log
   ```

2. **数据库连接失败**
   ```bash
   # 测试数据库连接
   mysql -h localhost -u backup_user -p -e "SELECT 1"
   
   # 检查配置文件
   cat /opt/backups/config/database_mysql.json
   ```

3. **云同步认证失败**
   ```bash
   # 测试 AWS 连接
   aws s3 ls s3://my-backup-bucket
   
   # 检查凭证配置
   cat ~/.aws/credentials
   ```

4. **磁盘空间不足**
   ```bash
   # 检查磁盘使用情况
   df -h /opt/backups
   
   # 清理过期备份
   sudo -u backup /opt/backups/scripts/backup_cleanup.sh
   ```

### 调试技巧

```bash
# 详细输出模式
ansible-playbook backup-strategy.yml -vvv

# 仅在特定主机执行
ansible-playbook backup-strategy.yml --limit backup01.example.com

# 跳过错误继续执行
ansible-playbook backup-strategy.yml --skip-tags "verification"

# 使用自定义变量文件
ansible-playbook backup-strategy.yml -e @custom_vars.yml
```

## 📊 备份监控

### 监控指标

- **备份成功率**：备份任务执行成功率
- **备份大小**：每日备份文件大小
- **备份时长**：备份任务执行时间
- **存储使用率**：备份存储空间使用情况

### 监控脚本

```bash
# 查看备份状态
sudo -u backup /opt/backups/scripts/backup_monitor.sh --status

# 检查备份完整性
sudo -u backup /opt/backups/scripts/backup_verify.sh

# 生成备份报告
sudo -u backup /opt/backups/scripts/backup_monitor.sh --report
```

### 通知配置

支持多种通知方式：

- **邮件通知**：SMTP 邮件发送
- **Webhook 通知**：HTTP 接口调用
- **钉钉通知**：钉钉机器人

```yaml
backup_notification_methods:
  - method: "email"
    enabled: true
    smtp_server: "smtp.example.com"
    to_addresses: ["admin@example.com"]
  - method: "webhook"
    enabled: true
    url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
```

## 🔄 备份恢复

### 文件系统恢复

```bash
# 恢复整个目录
sudo -u backup /opt/backups/scripts/filesystem_restore.sh /etc 20231201_020000

# 恢复单个文件
sudo -u backup /opt/backups/scripts/filesystem_restore.sh /etc/passwd 20231201_020000
```

### 数据库恢复

```bash
# 恢复 MySQL 数据库
sudo -u backup /opt/backups/scripts/database_restore.sh mysql wordpress 20231201_030000

# 恢复 PostgreSQL 数据库
sudo -u backup /opt/backups/scripts/database_restore.sh postgresql mydb 20231201_030000
```

### 云下载恢复

```bash
# 从 AWS S3 下载备份
aws s3 sync s3://my-backup-bucket/backups/ /opt/backups/download/

# 从阿里云 OSS 下载备份
ossutil sync oss://my-backup-bucket/backups/ /opt/backups/download/
```

## 🔒 安全配置

### 访问控制

- 配置适当的文件权限
- 使用专用备份用户
- 限制网络访问
- 定期更新密码

### 数据加密

- 启用备份文件加密
- 使用强加密算法
- 安全管理加密密钥
- 传输过程加密

```yaml
backup_security:
  encrypt_backups: true
  encryption_algorithm: "AES256"
  secure_delete: true
  permission_mode: "0600"
  directory_mode: "0700"
```

### Vault 加密

使用 Ansible Vault 保护敏感信息：

```bash
# 创建加密变量文件
ansible-vault create vault_vars.yml

# 编辑加密变量文件
ansible-vault edit vault_vars.yml

# 使用加密变量文件
ansible-playbook backup-strategy.yml -e @vault_vars.yml --ask-vault-pass
```

## 📚 最佳实践

1. **备份策略**
   - 制定 3-2-1 备份原则
   - 定期测试备份恢复
   - 监控备份执行状态
   - 建立备份验证机制

2. **存储管理**
   - 合理配置保留策略
   - 监控存储空间使用
   - 实施分层存储策略
   - 定期清理过期数据

3. **安全加固**
   - 启用数据加密
   - 限制访问权限
   - 定期更新密钥
   - 审计访问日志

4. **灾难恢复**
   - 制定恢复计划
   - 建立异地备份
   - 定期演练恢复流程
   - 文档化操作流程

## 📞 支持与反馈

如果遇到问题或有改进建议，请：

1. 检查日志文件获取详细错误信息
2. 参考本文档的故障排除部分
3. 在测试环境验证配置
4. 提交详细的问题报告

---

**⚠️ 重要提醒：** 本套 playbooks 主要用于教学和学习目的，在生产环境使用前请进行充分测试并根据实际需求调整配置。请务必测试备份恢复流程，确保数据安全。