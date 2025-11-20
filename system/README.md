# 系统管理模块指南

## 章节概述

本章收录了面向系统管理与运维的核心 Ansible 模块，覆盖用户与组管理、服务生命周期控制、主机配置、以及防火墙规则管理等日常运维需求。

## 所含模块

| 模块 | 集合 | 主要用途 | 依赖 |
|------|------|--------|------|
| [user](#user-用户管理) | ansible.builtin | 创建、修改、删除用户账号，管理 SSH 密钥与权限 | - |
| [group](#group-组管理) | ansible.builtin | 创建、修改、删除用户组 | - |
| [service](#service-服务管理) | ansible.builtin | 管理 systemd 或 init 服务的启动状态 | systemd/init 系统 |
| [systemd](#systemd-单元管理) | ansible.posix | 管理 systemd 单元文件、reload 配置、启用定时器 | systemd |
| [hostname](#hostname-主机名配置) | ansible.builtin | 设置主机名，修改 hostname 配置文件 | - |
| [timezone](#timezone-时区配置) | ansible.builtin | 设置系统时区，支持多种时区与硬件时钟同步 | 时区数据库 |
| [locale](#locale-地区设置) | community.general | 生成与管理系统区域设置，支持多语言环境 | glibc-langpack/locales |
| [firewalld](#firewalld-防火墙管理) | community.general | RHEL/CentOS 系统的动态防火墙规则管理 | firewalld 服务 |
| [iptables](#iptables-防火墙与-nat-规则) | community.general | 内核级防火墙规则与 NAT 规则管理 | iptables 工具 |
| [selinux](#selinux-安全增强) | ansible.posix | 管理 SELinux 安全策略与访问控制 | selinux-policy 包 |
| [auditd](#auditd-审计系统) | ansible.builtin | 配置 Linux 审计守护进程，提供系统级安全审计功能 | audit 软件包 |
| [pam_hardening](#pam_hardening-pam安全加固) | community.general | 配置可插拔认证模块安全策略，支持密码复杂度、账户锁定等 | libpwquality |
| [kernel_tuning](#kernel_tuning-内核调优) | ansible.posix | 配置 Linux 内核参数，优化系统性能和安全性 | sysctl 工具 |
| [cron](#cron-定时任务管理) | ansible.builtin | 管理 cron 定时任务，支持创建、修改、删除用户的定时任务 | cron 服务 |
| [authorized_key](#authorized-key-ssh密钥管理) | ansible.builtin | 管理用户的 SSH 授权密钥，支持添加、删除和更新 SSH 公钥 | OpenSSH |
| [reboot](#reboot-系统重启管理) | ansible.builtin | 重启远程主机，支持等待系统重启完成、验证重启状态 | reboot 命令 |

## 学习路线

1. **基础系统配置** → `user` & `group`：创建运维账号与权限隔离
2. **访问控制管理** → `authorized_key`：配置 SSH 密钥认证与访问权限
3. **主机标识与本地化** → `hostname`、`timezone`、`locale`：设置主机名、时区与地区设置
4. **服务生命周期** → `service` & `systemd`：启动、停止、启用服务与单元管理
5. **定时任务管理** → `cron`：配置自动化任务与定期维护
6. **系统维护** → `reboot`：安全重启系统与验证重启状态
7. **安全增强** → `selinux`：启用强制访问控制与安全策略
8. **审计监控** → `auditd`：配置系统审计与日志收集
9. **认证加固** → `pam_hardening`：配置 PAM 认证安全策略
10. **内核优化** → `kernel_tuning`：调优内核参数提升性能
11. **网络防护** → `firewalld` 与 `iptables`：配置防火墙规则与安全策略

## 与其他章节的关系

### network 章节的区别
- **network 章节** 主要涵盖网络连接与连通性检查（如 wait_for 监控端口可用性）
- **system 章节** 重点在本地系统配置与安全策略（防火墙、服务管理）
- 在微服务部署时常结合使用：network 用于服务就绪检查，system 用于防火墙配置

### applications 章节的协同
- **applications 章节** 专注于软件包与应用部署（包管理、容器、源码）
- **system 章节** 负责基础系统环境准备（用户、组、服务启动）
- 通常部署流程是：system 创建应用账号 → applications 部署软件包 → system 启动服务

### advanced 章节的融合
- 系统模块可与 `block/rescue`、`when` 条件、`handler` 等高级特性结合
- 示例：创建用户失败时的回滚策略（rescue），条件判断特定环境是否创建账号（when）

## 常用场景

### 场景 1: 新建运维账号与权限隔离
```yaml
# 使用 user 模块创建运维账号
# 使用 group 模块为其分配权限组
# 添加 sudoers 配置允许无密码提权
```

### 场景 2: 应用服务自动启动与健康检查
```yaml
# 使用 systemd 模块启用并启动应用服务
# 使用 service 模块兼容不同 init 系统
# 与 network 的 wait_for 结合检查服务就绪
```

### 场景 3: 分层防火墙策略
```yaml
# DMZ 层（对外）：firewalld 开放 80/443
# 应用层（对内）：firewalld 开放应用端口
# 管理层（管理）：iptables 限制管理端口源 IP
```

### 场景 4: 容器化主机基线配置
```yaml
# 创建容器运行用户（user 模块）
# 配置容器网络防火墙规则（firewalld/iptables 模块）
# 启用容器时间同步服务（systemd 模块）
```

## 安全最佳实践

1. **用户与权限隔离**：为不同应用创建专用账号，避免权限提升
2. **最小化防火墙规则**：默认 DROP，仅允许必需端口与源 IP
3. **服务自动启动**：确保关键服务在系统启动时自动运行
4. **备份与验证**：修改系统配置前做好备份，应用后验证规则生效
5. **审计日志**：启用 auditd 追踪用户创建、防火墙规则变更等关键操作
6. **认证安全**：通过 pam_hardening 配置密码策略、账户锁定、会话限制
7. **内核安全**：使用 kernel_tuning 禁用危险网络功能、启用防护机制

## 测试与验证

- 每个模块都包含独立的 `playbook.yml` 和 `README.md`
- `vars/example_vars.yml` 提供可配置的参数与默认值
- 运行前使用 `--syntax-check` 检查语法
- 使用 `--check` 模式预览变更，确认无误后正式执行
- 查看 `tests/system/test_system.py` 了解结构验证测试

## 快速导航

- [user 用户管理](user/README.md)
- [group 组管理](group/README.md)
- [service 服务管理](service/README.md)
- [systemd 单元管理](systemd/README.md)
- [hostname 主机名配置](hostname/README.md)
- [timezone 时区配置](timezone/README.md)
- [locale 地区设置](locale/README.md)
- [firewalld 防火墙管理](firewalld/README.md)
- [iptables 防火墙与 NAT 规则](iptables/README.md)
- [selinux 安全增强](selinux/README.md)
- [auditd 审计系统](auditd/README.md)
- [pam_hardening PAM 安全加固](pam_hardening/README.md)
- [kernel_tuning 内核调优](kernel_tuning/README.md)
- [authorized_key SSH密钥管理](authorized_key/README.md)
- [reboot 系统重启管理](reboot/README.md)
