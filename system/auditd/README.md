# auditd 审计系统模块使用指南

## 模块用途
`auditd` 模块用于配置 Linux 审计守护进程，提供系统级的安全审计功能。通过配置审计规则，可以监控文件访问、系统调用、用户登录等关键安全事件，满足合规性要求（如 PCI DSS、HIPAA）和安全基线标准。适用于安全加固、入侵检测、合规审计等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `audit_rules` | list | 审计规则列表，包含文件、系统调用、用户操作监控 | 文件路径、系统调用号、用户ID |
| `auditd_config` | dict | auditd 守护进程配置参数 | 日志轮转、磁盘空间、失败策略 |
| `remote_server` | str | 远程审计日志服务器地址 | IP地址或域名 |
| `max_log_file` | int | 单个审计日志文件最大大小（MB） | 20-100 |
| `max_log_file_action` | str | 日志文件达到最大时的处理方式 | rotate、suspend、ignore |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `audit_rules_loaded` | 是否成功加载审计规则 | true/false |
| `auditd_status` | auditd 服务状态 | active/inactive |
| `audit_log_size` | 当前审计日志大小 | 15MB |
| `remote_forwarding` | 远程转发状态 | enabled/disabled |
| `changed` | 是否修改了审计配置 | true/false |

## 使用情境

### 生产环境安全审计
**场景**：在生产服务器上启用全面的系统审计，监控关键文件和系统调用
- 监控 `/etc/passwd`、`/etc/shadow` 等敏感文件访问
- 记录用户登录、sudo 使用、权限变更操作
- 配置日志轮转和远程转发，防止日志篡改

### 合规性审计
**场景**：满足 PCI DSS、SOX、HIPAA 等合规性要求的审计配置
- 监控数据库访问和配置变更
- 记录管理员操作和权限变更
- 配置审计日志的完整性保护和长期存储

### 入侵检测
**场景**：通过审计日志检测可疑活动和潜在入侵
- 监控异常的系统调用模式
- 检测未授权的文件访问尝试
- 配置实时告警机制

### 集中化日志管理
**场景**：将多台服务器的审计日志集中到中央服务器
- 配置远程审计日志转发
- 实现日志的统一分析和存储
- 确保审计日志的完整性和可用性

## 安全注意事项

1. **审计规则最小化原则**：
   - 只审计必要的安全相关事件
   - 避免过度审计导致性能下降和日志爆炸
   - 定期评估和优化审计规则

2. **日志存储安全**：
   - 配置审计日志的只读权限
   - 实施日志轮转和备份策略
   - 考虑使用远程日志服务器防止本地篡改

3. **性能影响评估**：
   - 审计规则过多可能影响系统性能
   - 监控审计系统的资源使用情况
   - 在生产环境部署前进行充分测试

4. **合规性要求**：
   - 根据具体合规标准配置审计规则
   - 确保审计日志的完整性和不可篡改性
   - 建立审计日志的定期审查机制

## 环境依赖

### 必需
- 目标主机支持 auditd（Linux 内核 2.6+）
- auditd 软件包（audit、audit-libs）
- auditctl 工具（audit 软件包的一部分）
- 需要 root 或 sudo 权限配置审计规则

### 推荐
- audispd-plugins（远程转发插件）
- rsyslog 或 syslog-ng（日志转发）
- logrotate（日志轮转）
- aide 或 tripwire（文件完整性检查）

### 系统支持
- RHEL/CentOS 6/7/8/9：全面支持
- Ubuntu 16.04+：支持
- Debian 8+：支持
- SUSE Linux Enterprise：支持

## 常见问题

### 1. auditd 服务无法启动
检查 auditd 配置文件语法：
```bash
# 检查配置文件语法
augenrules --check

# 验证审计规则
auditctl -l
```

### 2. 审计规则不生效
确认内核审计支持：
```bash
# 检查内核审计支持
cat /proc/sys/kernel/audit_enabled

# 检查审计规则是否加载
auditctl -l
```

### 3. 审计日志增长过快
调整审计策略和日志轮转：
```bash
# 减少审计规则的粒度
# 配置更激进的日志轮转
auditctl -D  # 删除所有规则，重新配置
```

### 4. 远程日志转发失败
检查网络和防火墙配置：
```bash
# 测试远程服务器连通性
nc -zv audit-server 60

# 检查防火墙规则
iptables -L -n | grep 60
```

## 最佳实践

### 生产环境审计配置
```yaml
- name: 生产环境审计配置
  block:
    - name: 安装审计软件包
      ansible.builtin.package:
        name: audit
        state: present
      become: yes
    
    - name: 配置 auditd 基础设置
      ansible.builtin.template:
        src: auditd.conf.j2
        dest: /etc/audit/auditd.conf
        backup: yes
      become: yes
      notify: 重启 auditd 服务
    
    - name: 部署审计规则
      ansible.builtin.template:
        src: audit.rules.j2
        dest: /etc/audit/rules.d/audit.rules
        backup: yes
      become: yes
      notify: 重新加载审计规则
```

### 合规性审计规则
```yaml
- name: 合规性审计规则配置
  block:
    - name: 监控敏感文件访问
      ansible.builtin.lineinfile:
        path: /etc/audit/rules.d/audit.rules
        line: "-w /etc/passwd -p wa -k identity"
        create: yes
      become: yes
    
    - name: 监控用户登录事件
      ansible.builtin.lineinfile:
        path: /etc/audit/rules.d/audit.rules
        line: "-w /var/log/secure -p wa -k logins"
        create: yes
      become: yes
```

### 审计日志分析
```yaml
- name: 审计日志分析示例
  block:
    - name: 检查最近的审计事件
      ansible.builtin.shell: |
        ausearch -ts recent -k identity | head -20
      register: audit_events
      changed_when: false
    
    - name: 显示审计事件摘要
      ansible.builtin.debug:
        msg: "{{ audit_events.stdout_lines }}"
```

## 相关示例
- [selinux 模块](../selinux/README.md) - SELinux 安全策略管理
- [firewalld 模块](../firewalld/README.md) - 防火墙规则管理
- [user 模块](../user/README.md) - 用户账号管理
- [service 模块](../service/README.md) - 系统服务管理