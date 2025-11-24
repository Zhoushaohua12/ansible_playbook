# Ansible Playbooks - 应用监控套件

本目录包含完整的 Ansible playbooks，用于自动化部署应用部署、监控系统和维护策略。涵盖了从应用部署到监控告警再到备份恢复的完整运维生命周期。

为满足“Playbook Hub”请求，我们在此目录中落地了一个**完整的工作区**，统一收录系统初始化、Web 服务、数据库、应用部署、监控与维护场景，配套 Inventory、group_vars、共享角色空间与 Quick Start 文档，方便贡献者按需拼装与扩展。

## 🧭 工作区范围

- **system-init/**：跨 Linux 发行版的基线配置、用户/权限、安全加固 Playbook。
- **web-services/**：Nginx/Apache/SSL 相关部署与高可用样例（含 vars/templates/handlers/roles）。
- **database/**：MySQL、PostgreSQL、备份与复制实践。
- **application-deploy/**：容器、LAMP/LNMP/Node.js 等应用交付场景。
- **monitoring/**：Prometheus、ELK、告警与可视化栈。
- **maintenance/**：备份、巡检、自动化维护策略。
- **inventory/**：统一的 `hosts` 清单与 `group_vars/*.yml` 示例（含中文警告与 `vault_` 占位符）。
- **roles/**：跨场景复用的共享角色命名空间，便于在 `ansible.cfg` 中一次性声明。

## 🖥️ 操作系统覆盖矩阵

| 场景 | Ubuntu 20.04/22.04 | Debian 11/12 | RHEL 8/9 | CentOS 7 | Rocky 9 | 说明 |
|------|---------------------|--------------|---------|---------|---------|------|
| system-init | ✅ | ✅ | ✅ | ✅ | ✅ | 统一硬件驱动、基础包、SSH 与防火墙基线 |
| web-services | ✅ | ✅ | ✅ | ⚠️ (需 EPEL) | ✅ | Nginx/Apache/HAProxy/SSL 自动化 |
| database | ✅ | ⚠️ (需 backports) | ✅ | ✅ | ✅ | 覆盖 MySQL 8、PostgreSQL 14、备份 & 复制 |
| application-deploy | ✅ | ✅ | ✅ | ✅ | ✅ | LAMP/LNMP、Docker、Node.js、滚动更新 |
| monitoring | ✅ | ✅ | ✅ | ✅ | ✅ | Prometheus + Alertmanager + ELK/Logstack |
| maintenance | ✅ | ✅ | ✅ | ✅ | ✅ | 计划任务、备份策略、巡检模板 |

> 表格中的 ✅ 表示已在 Playbook 中覆盖；⚠️ 表示需要额外仓库或兼容性验证。

## 🗂️ 目录导航与链接

- [system-init/](./system-init/README.md)
- [web-services/](./web-services/README.md)
- [database/](./database/README.md)
- [application-deploy/](./application-deploy/README.md)
- [monitoring/](./monitoring/README.md)
- [maintenance/](./maintenance/README.md)
- [inventory/hosts](./inventory/hosts) 与 [inventory/group_vars/](./inventory/group_vars)
- [roles/README.md](./roles/README.md)（共享角色说明）
- [QUICK_START.md](./QUICK_START.md)（快速上手指南）

## 🗄️ 变量 / Handlers / 模板组织

1. **Inventory & group_vars**：`inventory/hosts` 提供场景化 host 组（init/nginx/db/app/monitoring/backup），每个组在 `inventory/group_vars/<group>.yml` 中定义推荐默认值和 `vault_` 占位符，文件顶部包含中文警示语。
2. **场景目录结构**：每个子目录下均按照 `vars/`、`templates/`、`handlers/`、`roles/` 划分，Playbook 通过 `vars_files` 与 `import_role` 关联，确保可复用。
3. **共享角色**：通用逻辑可放入根目录 `roles/` 并通过 `ansible.cfg` 中的 `roles_path` 暴露给所有 Playbook。
4. **Handlers 命名**：约定中文动词 + 名词（例如 “重启 Nginx 服务”），并通过 `listen` 聚合，便于 `--tags handler` 调用。

## 🧑‍💻 FQCN / 标签 / Check 模式规范

- **FQCN**：所有任务必须显式使用完全限定集合名称，例如 `ansible.builtin.package`、`ansible.builtin.service`、`community.mysql.mysql_user`。这样可以清晰表达依赖并避免不同版本带来的兼容性问题。
- **标签体系**：Playbook 按模块（`system_init`、`web`、`db`）、操作类型（`install`、`config`、`verify`、`cleanup`）与影响面（`critical`、`optional`）设置标签，在执行时可组合：
  ```bash
  ansible-playbook -i inventory/hosts web-services/nginx-install.yml --tags "packages,config"
  ansible-playbook -i inventory/hosts maintenance/backup-strategy.yml --skip-tags verify
  ```
- **检查模式**：所有 Playbook 在 PR 及生产前必须依次执行 `--syntax-check` 与 `--check --diff`，示例：
  ```bash
  ansible-playbook --syntax-check system-init/ubuntu-debian-init.yml
  ansible-playbook -i inventory/hosts system-init/ubuntu-debian-init.yml --check --diff
  ansible-playbook -i inventory/hosts application-deploy/nodejs-app-deploy.yml -l app_servers --tags deploy
  ```

## ⚙️ 工作区配置

- 默认 `ansible.cfg` 已在本目录提供，设置 `inventory = inventory/hosts`、`roles_path = roles:system-init/roles:...`、禁用 `host_key_checking` 并启用 `ansible.posix.profile_tasks` callback。
- 所有示例命令均假设在 `ansible-playbooks/` 目录下执行，可结合 `ANSIBLE_CONFIG`、`ANSIBLE_INVENTORY` 环境变量覆盖。
- 快速上手、依赖安装、Inventory 定制与故障排除说明请参考 [QUICK_START.md](./QUICK_START.md)。

---

## 📋 目录结构

```
ansible-playbooks/
├── ansible.cfg                  # 工作区配置（inventory、roles_path、callbacks）
├── QUICK_START.md               # 快速上手指南（依赖安装、Inventory、故障排查）
├── README.md                    # 主文档（本文件）
│
├── system-init/                 # 系统初始化 Playbooks
│   ├── rhel-centos-init.yml    # RHEL/CentOS 初始化
│   ├── ubuntu-debian-init.yml  # Ubuntu/Debian 初始化
│   ├── common-security-hardening.yml # 通用安全加固
│   ├── vars/
│   ├── templates/
│   ├── roles/
│   └── README.md
│
├── web-services/                # Web 服务器 Playbooks
│   ├── nginx-install.yml       # Nginx 安装与配置
│   ├── apache-install.yml      # Apache 安装与配置
│   ├── ssl-certificate-setup.yml # SSL/TLS 证书部署
│   ├── vars/
│   ├── templates/
│   ├── handlers/
│   ├── roles/
│   └── README.md
│
├── database/                    # 数据库 Playbooks
│   ├── mysql-5.7-install.yml   # MySQL 5.7 安装
│   ├── mysql-8.0-install.yml   # MySQL 8.0 安装
│   ├── mysql-master-slave.yml  # MySQL 主从复制
│   ├── postgresql-install.yml  # PostgreSQL 安装
│   ├── postgresql-backup.yml   # PostgreSQL 备份
│   ├── vars/
│   ├── templates/
│   ├── handlers/
│   ├── roles/
│   └── README.md
│
├── application-deploy/          # 应用部署 Playbooks
│   ├── docker-install.yml      # Docker 引擎与 Compose 安装
│   ├── lamp-stack-deploy.yml   # LAMP 栈（Apache/PHP/MySQL）部署
│   ├── lnmp-stack-deploy.yml   # LNMP 栈（Nginx/PHP-FPM/MySQL）部署
│   ├── nodejs-app-deploy.yml   # Node.js 应用服务部署
│   ├── vars/
│   ├── templates/
│   ├── handlers/
│   ├── roles/
│   └── README.md
│
├── monitoring/                  # 监控系统 Playbooks
│   ├── prometheus-install.yml  # Prometheus 监控栈安装
│   ├── elk-stack-install.yml   # ELK 栈安装配置
│   ├── vars/
│   ├── templates/
│   ├── handlers/
│   ├── roles/
│   │   ├── prometheus/
│   │   └── elk/
│   └── README.md
│
├── maintenance/                 # 维护策略 Playbooks
│   ├── backup-strategy.yml     # 备份策略配置与执行
│   ├── vars/
│   ├── templates/
│   ├── handlers/
│   ├── roles/
│   │   ├── filesystem_backup/
│   │   ├── database_backup/
│   │   └── cloud_sync/
│   └── README.md
│
├── inventory/                   # 统一主机清单与变量
│   ├── hosts                   # 主机清单示例（分组：init/nginx/db/app/monitoring/backup）
│   └── group_vars/
│       ├── all.yml             # 全局变量（⚠️ 中文警告 + vault_* 占位符）
│       ├── init_servers.yml    # 系统初始化组变量
│       ├── nginx_servers.yml   # Nginx 组变量
│       ├── database_servers.yml # 数据库组变量
│       ├── app_servers.yml     # 应用服务器组变量
│       ├── monitoring_servers.yml # 监控组变量
│       └── backup_servers.yml  # 备份组变量
│
└── roles/                       # 共享角色命名空间
    └── README.md               # 共享角色说明
```

## 🚀 快速开始

### 系统要求

- **Ansible**: >= 2.9
- **Python**: >= 3.6
- **操作系统**: Ubuntu 20.04+, Debian 10+, CentOS 7+
- **内存**: 最小 4GB（推荐 8GB）
- **磁盘**: 最小 50GB（推荐 100GB）

### 安装依赖

```bash
# 安装 Ansible
pip install ansible

# 安装必要的 Ansible Collections
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.mysql
ansible-galaxy collection install community.general
ansible-galaxy collection install community.postgresql
```

### 主机清单配置

创建 `inventory` 文件：

```ini
[web_servers]
web01.example.com
web02.example.com

[database_servers]
db01.example.com

[monitoring_servers]
monitor01.example.com

[backup_servers]
backup01.example.com

[all:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/id_rsa
```

### 执行 Playbooks

#### 1. 应用部署

```bash
# 部署 Docker 环境
ansible-playbook -i inventory application-deploy/docker-install.yml

# 部署 LAMP 栈
ansible-playbook -i inventory application-deploy/lamp-stack-deploy.yml

# 部署 LNMP 栈
ansible-playbook -i inventory application-deploy/lnmp-stack-deploy.yml

# 部署 Node.js 应用
ansible-playbook -i inventory application-deploy/nodejs-app-deploy.yml
```

#### 2. 监控系统

```bash
# 部署 Prometheus 监控栈
ansible-playbook -i inventory monitoring/prometheus-install.yml

# 部署 ELK 日志栈
ansible-playbook -i inventory monitoring/elk-stack-install.yml
```

#### 3. 维护策略

```bash
# 配置备份策略
ansible-playbook -i inventory maintenance/backup-strategy.yml
```

## 📦 功能特性

### 应用部署套件

- **Docker 部署**: Docker 引擎 + Compose 安装配置
- **LAMP 栈**: Apache + PHP + MySQL 完整 Web 环境
- **LNMP 栈**: Nginx + PHP-FPM + MySQL 高性能 Web 环境
- **Node.js 应用**: Node.js 应用服务部署与管理

### 监控系统套件

- **Prometheus 监控**: 时序数据库 + 告警管理
- **ELK 日志栈**: Elasticsearch + Logstash + Kibana
- **指标收集**: Node Exporter + Blackbox Exporter
- **告警通知**: 邮件 + Webhook + 钉钉

### 维护策略套件

- **文件系统备份**: rsync + tar + dd 多种备份方式
- **数据库备份**: MySQL + PostgreSQL + MongoDB 支持
- **云同步**: AWS S3 + 阿里云 OSS + Azure Blob
- **自动化管理**: 定时任务 + 验证 + 清理 + 监控

## ⚙️ 配置管理

### 变量文件结构

每个套件都有独立的 `vars/default.yml` 文件：

```yaml
# 应用部署配置
docker_enabled: true
lamp_mysql_root_password: "secure_password"
nodejs_app_port: "3000"

# 监控系统配置
prometheus_version: "2.45.0"
elasticsearch_version: "8.8.0"
alertmanager_port: "9093"

# 维护策略配置
backup_retention_days: 30
filesystem_backup_enabled: true
cloud_sync_providers: [...]
```

### 使用 Ansible Vault

保护敏感配置信息：

```bash
# 创建加密变量文件
ansible-vault create vault_secrets.yml

# 编辑加密文件
ansible-vault edit vault_secrets.yml

# 使用加密文件执行
ansible-playbook -i inventory playbook.yml -e @vault_secrets.yml --ask-vault-pass
```

## 🏷️ 标签系统

所有 playbooks 都支持标签进行选择性执行：

| 标签分类 | 标签示例 | 描述 |
|---------|---------|------|
| 功能模块 | `docker`, `prometheus`, `backup` | 按功能模块分类 |
| 任务类型 | `packages`, `config`, `service` | 按任务类型分类 |
| 组件类型 | `nginx`, `mysql`, `elasticsearch` | 按组件类型分类 |
| 操作类型 | `install`, `verify`, `cleanup` | 按操作类型分类 |

### 标签使用示例

```bash
# 仅安装软件包
ansible-playbook playbook.yml --tags "packages"

# 仅配置服务
ansible-playbook playbook.yml --tags "config,service"

# 跳过验证步骤
ansible-playbook playbook.yml --skip-tags "verify"

# 多标签组合
ansible-playbook playbook.yml --tags "install,mysql"
```

## 🔧 故障排除

### 常见问题

1. **SSH 连接失败**
   ```bash
   # 检查 SSH 连接
   ansible all -i inventory -m ping
   
   # 使用详细模式调试
   ansible-playbook -i inventory playbook.yml -vvv
   ```

2. **权限问题**
   ```bash
   # 检查 sudo 权限
   ansible all -i inventory -m command -a "whoami"
   
   # 使用 become 提权
   ansible-playbook -i inventory playbook.yml --become --ask-become-pass
   ```

3. **网络连接问题**
   ```bash
   # 检查网络连通性
   ansible all -i inventory -m command -a "curl -I http://google.com"
   
   # 使用代理
   ansible-playbook -i inventory playbook.yml -e "http_proxy=http://proxy:8080"
   ```

4. **软件包安装失败**
   ```bash
   # 更新包缓存
   ansible all -i inventory -m apt -a "update_cache=yes"
   
   # 检查包可用性
   ansible all -i inventory -m apt -a "name=vim state=present" --check
   ```

### 调试技巧

```bash
# 语法检查
ansible-playbook --syntax-check playbook.yml

# 干运行模式
ansible-playbook --check playbook.yml

# 详细输出
ansible-playbook -vvv playbook.yml

# 限制主机范围
ansible-playbook -l host01,host02 playbook.yml

# 单步执行
ansible-playbook --step playbook.yml
```

## 🔒 安全最佳实践

### 访问控制

- 使用 SSH 密钥认证，禁用密码认证
- 配置防火墙规则，限制端口访问
- 使用专用的服务账户运行应用
- 定期更新系统和软件包

### 数据保护

- 使用 Ansible Vault 加密敏感数据
- 配置数据库连接加密
- 启用备份文件加密
- 实施网络传输加密

### 监控审计

- 配置系统日志收集
- 启用操作审计日志
- 设置异常行为告警
- 定期检查安全配置

## 📊 监控指标

### 应用监控

- **服务可用性**: HTTP 端点检查
- **性能指标**: 响应时间、吞吐量
- **资源使用**: CPU、内存、磁盘
- **错误监控**: 错误率、异常统计

### 基础设施监控

- **系统指标**: 负载、内存、磁盘、网络
- **服务状态**: 进程状态、端口监听
- **日志分析**: 错误日志、访问日志
- **告警通知**: 邮件、短信、即时通讯

### 备份监控

- **备份成功率**: 备份任务执行状态
- **数据完整性**: 校验和验证结果
- **存储使用**: 备份存储空间监控
- **恢复测试**: 定期恢复演练结果

## 📚 文档结构

每个套件都有详细的文档：

- **README.md**: 总体介绍和快速开始
- **vars/default.yml**: 变量配置说明
- **templates/**: 配置文件模板
- **roles/**: 角色化任务组织

### 文档导航

```bash
# 应用部署文档
cat application-deploy/README.md

# 监控系统文档
cat monitoring/README.md

# 维护策略文档
cat maintenance/README.md

# 变量配置说明
cat */vars/default.yml
```

## 🔄 CI/CD 集成

### GitLab CI 示例

```yaml
stages:
  - validate
  - deploy
  - test

validate:
  stage: validate
  script:
    - ansible-playbook --syntax-check application-deploy/docker-install.yml
    - ansible-playbook --syntax-check monitoring/prometheus-install.yml

deploy:
  stage: deploy
  script:
    - ansible-playbook -i inventory application-deploy/docker-install.yml --tags "packages"
  only:
    - main

test:
  stage: test
  script:
    - ansible-playbook -i inventory application-deploy/docker-install.yml --tags "verify"
  dependencies:
    - deploy
```

### GitHub Actions 示例

```yaml
name: Ansible Playbooks

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Validate playbooks
      run: |
        ansible-playbook --syntax-check application-deploy/docker-install.yml
        ansible-playbook --syntax-check monitoring/prometheus-install.yml
```

## 📞 支持与反馈

### 获取帮助

1. **查看文档**: 阅读各套件的 README 文件
2. **检查日志**: 查看详细的执行日志和错误信息
3. **测试环境**: 在测试环境中验证配置
4. **社区支持**: 提交 Issue 或 Pull Request

### 贡献指南

1. **Fork 项目**: 创建个人分支
2. **功能开发**: 在新分支中开发功能
3. **测试验证**: 确保所有测试通过
4. **提交 PR**: 提交 Pull Request

### 版本管理

- **主分支**: `main` 稳定版本
- **开发分支**: `develop` 开发版本
- **功能分支**: `feature/*` 新功能开发
- **修复分支**: `hotfix/*` 紧急修复

---

**⚠️ 重要提醒**: 本套 playbooks 主要用于教学和学习目的，在生产环境使用前请进行充分测试并根据实际需求调整配置。请务必阅读各套件的详细文档，了解具体的使用方法和注意事项。