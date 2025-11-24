# 系统初始化套件 (System Init Suite)

## 概述

本系统初始化套件提供了一套完整的 Ansible Playbooks，用于自动化初始化和加固 Linux 系统。支持 RHEL/CentOS 和 Ubuntu/Debian 两大主流发行版，包含系统基础配置、安全加固、用户管理、防火墙配置等功能。

## 目录结构

```
system-init/
├── rhel-centos-init.yml          # RHEL/CentOS 系统初始化
├── ubuntu-debian-init.yml        # Ubuntu/Debian 系统初始化
├── common-security-hardening.yml # 通用安全加固
├── vars/
│   └── default.yml               # 变量配置文件
├── handlers/
│   └── main.yml                 # 处理器定义
├── roles/                       # 可重用角色
│   ├── baseline_packages/       # 基础软件包安装
│   ├── users_hardening/         # 用户安全加固
│   ├── firewall/                # 防火墙配置
│   └── security_baseline/      # 安全基线配置
├── templates/                   # 配置模板文件
│   ├── sshd_config.j2          # SSH 配置模板
│   ├── chrony.conf.j2          # 时间同步配置模板
│   ├── limits.conf.j2           # 系统限制配置模板
│   ├── motd.j2                 # 登录横幅模板
│   ├── network-ifcfg.j2        # RHEL/CentOS 网络配置模板
│   ├── netplan-config.j2       # Ubuntu Netplan 配置模板
│   └── network-interfaces.j2   # Ubuntu 传统网络配置模板
└── README.md                    # 本文档
```

## 支持的操作系统和版本

### RHEL/CentOS
- RHEL 7, 8, 9
- CentOS 7, 8, 9
- Rocky Linux 8, 9
- AlmaLinux 8, 9

### Ubuntu/Debian
- Ubuntu 18.04 LTS, 20.04 LTS, 22.04 LTS
- Debian 9, 10, 11, 12

## 主要功能

### 1. 系统基础配置
- 时区和语言环境设置
- 基础软件包安装
- 网络接口配置
- 时间同步服务配置

### 2. 安全加固
- SSH 安全配置
- 防火墙规则配置
- SELinux/AppArmor 配置
- 系统审计配置
- 内核参数加固

### 3. 用户管理
- 系统用户创建
- 用户权限配置
- SSH 密钥管理
- 密码策略配置

### 4. 服务配置
- 必要服务启用
- 不必要服务禁用
- 服务安全配置
- 日志轮转配置

## 使用方法

### 1. 准备工作

#### 安装 Ansible
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible

# RHEL/CentOS
sudo yum install ansible
```

#### 安装必要的 Ansible 集合
```bash
ansible-galaxy collection install community.general
ansible-galaxy collection install ansible.posix
```

### 2. 配置 Inventory

创建 inventory 文件：
```ini
[all:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no'

[rhel_centos_hosts]
rhel-server-01 ansible_host=192.168.1.100
centos-server-01 ansible_host=192.168.1.101

[ubuntu_debian_hosts]
ubuntu-server-01 ansible_host=192.168.1.200
debian-server-01 ansible_host=192.168.1.201

[all:vars]
ansible_user=root
ansible_ssh_private_key_file=~/.ssh/id_rsa
```

### 3. 执行 Playbook

#### RHEL/CentOS 系统初始化
```bash
# 语法检查
ansible-playbook -i inventory rhel-centos-init.yml --syntax-check

# 检查模式运行
ansible-playbook -i inventory rhel-centos-init.yml --check

# 实际执行
ansible-playbook -i inventory rhel-centos-init.yml

# 指定标签执行
ansible-playbook -i inventory rhel-centos-init.yml --tags "packages,ssh"
```

#### Ubuntu/Debian 系统初始化
```bash
# 语法检查
ansible-playbook -i inventory ubuntu-debian-init.yml --syntax-check

# 检查模式运行
ansible-playbook -i inventory ubuntu-debian-init.yml --check

# 实际执行
ansible-playbook -i inventory ubuntu-debian-init.yml
```

#### 通用安全加固
```bash
# 对所有主机执行安全加固
ansible-playbook -i inventory common-security-hardening.yml

# 只对特定组执行
ansible-playbook -i inventory common-security-hardening.yml --limit rhel_centos_hosts
```

## 变量配置

### 主要变量说明

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `system_timezone` | string | "Asia/Shanghai" | 系统时区 |
| `system_locale` | string | "zh_CN.UTF-8" | 系统语言环境 |
| `firewall_enabled` | boolean | true | 是否启用防火墙 |
| `ssh_hardening_enabled` | boolean | true | 是否启用 SSH 加固 |
| `selinux_configure` | boolean | true | 是否配置 SELinux (RHEL/CentOS) |
| `audit_enabled` | boolean | true | 是否启用系统审计 |
| `security_hardening_level` | string | "standard" | 安全加固级别 |

### 网络配置示例
```yaml
network_interfaces:
  - name: "eth0"
    method: "static"
    address: "192.168.1.100"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
    dns_servers:
      - "8.8.8.8"
      - "114.114.114.114"
```

### 用户配置示例
```yaml
baseline_users:
  - name: "admin"
    comment: "系统管理员"
    shell: "/bin/bash"
    groups:
      - "sudo"
      - "adm"
    sudo_access: true
    vault_ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2E..."
```

### 防火墙配置示例
```yaml
firewall_ports:
  - "22"    # SSH
  - "80"    # HTTP
  - "443"   # HTTPS

firewall_services:
  - "ssh"
  - "http"
  - "https"
```

## 标签说明

### 通用标签
- `info` - 显示信息任务
- `check` - 检查和验证任务
- `verify` - 验证配置结果

### 功能标签
- `packages` - 软件包安装
- `network` - 网络配置
- `ssh` - SSH 配置
- `firewall` - 防火墙配置
- `users` - 用户管理
- `security` - 安全加固
- `audit` - 审计配置
- `selinux` - SELinux 配置 (RHEL/CentOS)

## 执行流程

### 1. 系统初始化流程
1. 收集系统事实信息
2. 更新包管理器缓存
3. 安装基础软件包
4. 配置时区和语言环境
5. 配置网络接口
6. 配置防火墙规则
7. SSH 安全加固
8. 配置系统审计
9. 创建系统用户
10. 配置系统限制
11. 设置登录横幅

### 2. 安全加固流程
1. 应用安全基线角色
2. 应用用户加固角色
3. 应用防火墙角色
4. 内核参数加固
5. 文件系统安全加固
6. 日志和监控加固
7. 服务安全加固
8. 定时任务安全加固
9. 网络安全加固
10. 应用程序安全加固

## 处理器说明

### 网络服务处理器
- `重新加载网络配置` - 重新加载网络服务
- `应用网络配置` - 应用 Netplan 配置 (Ubuntu)

### 时间同步处理器
- `重启 chronyd 时间同步服务` - 重启时间同步服务
- `重新加载 chronyd 配置` - 重新加载时间同步配置

### SSH 服务处理器
- `重启 SSH 服务` - 重启 SSH 服务
- `重新加载 SSH 配置` - 重新加载 SSH 配置

### 防火墙处理器
- `重新加载 firewalld 防火墙` - 重新加载 firewalld 配置 (RHEL/CentOS)
- `重新加载 UFW 防火墙` - 重新加载 UFW 配置 (Ubuntu/Debian)

### 日志服务处理器
- `重启 rsyslog 服务` - 重启系统日志服务
- `重新加载 rsyslog 配置` - 重新加载日志配置

### 审计服务处理器
- `重启 auditd 审计服务` - 重启审计服务
- `重新加载审计规则` - 重新加载审计规则

## 示例命令

### 基础使用
```bash
# 对所有主机执行完整初始化
ansible-playbook -i inventory rhel-centos-init.yml ubuntu-debian-init.yml

# 只执行软件包安装
ansible-playbook -i inventory rhel-centos-init.yml --tags "packages"

# 只执行安全加固
ansible-playbook -i inventory common-security-hardening.yml --tags "security"
```

### 高级使用
```bash
# 使用自定义变量文件
ansible-playbook -i inventory rhel-centos-init.yml -e @custom_vars.yml

# 限制执行范围
ansible-playbook -i inventory rhel-centos-init.yml --limit "rhel-server-*"

# 并行执行
ansible-playbook -i inventory rhel-centos-init.yml --forks 10

# 详细输出
ansible-playbook -i inventory rhel-centos-init.yml -v
```

### 调试和故障排除
```bash
# 只显示将要执行的任务，不实际执行
ansible-playbook -i inventory rhel-centos-init.yml --list-tasks

# 显示主机变量
ansible-playbook -i inventory rhel-centos-init.yml --list-hosts

# 单步执行模式
ansible-playbook -i inventory rhel-centos-init.yml --step

# 从指定任务开始执行
ansible-playbook -i inventory rhel-centos-init.yml --start-at-task "配置 SSH 安全设置"
```

## 常见问题 (FAQ)

### Q1: 执行时提示权限不足
**A:** 确保使用具有 sudo 权限的用户执行，或者直接使用 root 用户执行。

### Q2: 网络配置不生效
**A:** 检查网络接口名称是否正确，配置后可能需要重启网络服务或系统。

### Q3: SSH 配置后无法登录
**A:** 检查 SSH 配置文件语法，确保公钥已正确配置，可以保留一个备用登录方式。

### Q4: 防火墙配置导致服务无法访问
**A:** 检查防火墙规则，确保必要的端口已开放，可以使用 `--check` 模式预先验证。

### Q5: SELinux 配置导致服务异常
**A:** 检查 SELinux 日志，使用 `setenforce 0` 临时设置为宽容模式进行调试。

### Q6: 时间同步失败
**A:** 检查网络连接和防火墙规则，确保 NTP 端口 (123/UDP) 已开放。

### Q7: 用户创建失败
**A:** 检查用户名是否已存在，确保符合系统命名规范。

### Q8: 软件包安装失败
**A:** 检查网络连接和软件源配置，确保包管理器缓存已更新。

## 安全注意事项

1. **敏感数据管理**：生产环境中请使用 Ansible Vault 加密敏感数据
2. **备份重要配置**：执行前备份重要的系统配置文件
3. **测试环境验证**：在生产环境应用前，请在测试环境充分验证
4. **权限最小化**：遵循最小权限原则，只授予必要的权限
5. **审计跟踪**：启用系统审计，记录所有重要操作
6. **定期更新**：定期更新系统软件包和安全补丁

## 贡献指南

1. Fork 本项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。

## 联系方式

- 项目维护者：系统管理团队
- 邮箱：admin@company.com
- 技术支持：support@company.com

---

**重要提醒**：本套件主要用于学习和测试环境，在生产环境使用前请进行充分的测试和验证。