# selinux 模块使用指南

## 模块用途
`ansible.posix.selinux` 模块用于管理 SELinux（Security Enhanced Linux）安全策略，支持设置 SELinux 工作模式、切换 SELinux 策略、管理文件安全上下文等。在 RHEL/CentOS 等企业 Linux 系统中提供强制访问控制（MAC），是提升系统安全性的重要手段。适用于安全加固、合规性要求、沙箱隔离等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `state` | str | SELinux 状态（enforcing 强制，permissive 宽容，disabled 禁用） | enforcing、permissive、disabled |
| `configfile` | str | SELinux 配置文件路径 | /etc/selinux/config |
| `policy` | str | SELinux 策略类型 | targeted、mls、strict 等 |
| `reload` | bool | 立即生效（不需要重启） | true、false |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `current_state` | 当前 SELinux 状态 | enforcing、permissive、disabled |
| `current_policy` | 当前 SELinux 策略 | targeted、mls |
| `changed` | 是否修改了 SELinux 配置 | true/false |
| `reboot_required` | 是否需要重启生效 | true/false |

## 使用情境

### 生产环境安全加固
**场景**：在生产服务器上启用 SELinux 强制模式，防止权限提升攻击
- 从 disabled 升级到 permissive，再到 enforcing
- 分阶段验证应用兼容性
- 防止未授权进程访问系统资源

### 开发和测试环境
**场景**：使用 SELinux 宽容模式进行开发与调试
- 记录所有违反 SELinux 策略的操作
- 生成审计日志用于分析应用权限需求
- 确保应用与 SELinux 策略兼容

### 合规性验证
**场景**：满足 PCI DSS、HIPAA 等安全合规要求
- 启用 SELinux 强制访问控制
- 定期审计 SELinux 策略违规
- 维护审计日志

### Docker 与容器隔离
**场景**：利用 SELinux 增强容器安全隔离
- 配置 SELinux 容器上下文
- 防止容器逃逸攻击
- 隔离容器与宿主机资源

## 安全注意事项

1. **分阶段启用 SELinux**：
   - 不建议直接从 disabled 切换到 enforcing
   - 先切换到 permissive 模式，观察审计日志
   - 逐步调整策略规则后再启用 enforcing
2. **应用兼容性验证**：
   - 某些应用可能与 SELinux 策略冲突
   - 启用 SELinux 前需要充分测试
   - 生成自定义 SELinux 策略规则
3. **审计日志管理**：
   - 启用 auditd 记录 SELinux 违规事件
   - 定期分析审计日志，发现权限需求
   - 防止审计日志过大占满磁盘
4. **策略选择**：
   - targeted 策略：覆盖常见网络服务，推荐用于标准部署
   - mls（Multi-Level Security）：针对军工等特殊场景
   - strict 策略：最严格的访问控制，可能影响性能

## 环境依赖

### 必需
- 目标主机支持 SELinux（仅限 RHEL、CentOS、Fedora 等 Red Hat 系列）
- selinux-policy 包（包含策略规则）
- selinux-utils 工具包（提供 semanage、getsebool 等命令）
- 需要 root 或 sudo 权限修改 SELinux 配置

### 推荐
- policycoreutils 包（policy 管理工具）
- policycoreutils-python-utils 包（生成自定义规则）
- setroubleshoot（SELinux 故障排查工具）
- audit 和 auditd（SELinux 审计系统）

### 系统支持
- CentOS/RHEL 7/8/9：全面支持
- Fedora：全面支持
- 其他 Linux 发行版：不支持 SELinux

## 常见问题

### 1. 启用 SELinux 后应用无法启动
应用可能需要特定的 SELinux 上下文。查看审计日志找出具体违规：
```yaml
- name: 检查 SELinux 违规日志
  ansible.builtin.shell: |
    ausearch -m avc -ts recent | grep denied | tail -20
  become: yes
  register: selinux_violations
```

### 2. 从 disabled 切换到 enforcing 需要多长时间生效？
需要重启系统才能从 disabled 切换到 enforcing，permissive 和 enforcing 之间可以立即切换：
```yaml
- name: SELinux 模式切换（需要分阶段）
  block:
    - name: 先切换到 permissive 模式
      ansible.posix.selinux:
        state: permissive
        reload: yes
      become: yes
    
    - name: 提示需要重启
      ansible.builtin.debug:
        msg: "需要重启系统以完全应用 SELinux 配置"
```

### 3. 如何生成自定义 SELinux 规则？
使用审计日志生成自定义规则：
```yaml
- name: 生成自定义 SELinux 策略（演示）
  ansible.builtin.shell: |
    # 查看违规日志
    ausearch -m avc -ts recent | grep denied > /tmp/violations.log
    # 生成自定义规则（需要 policycoreutils-python-utils）
    grep myapp /tmp/violations.log | audit2allow -M myapp_custom
  become: yes
  ignore_errors: yes
```

### 4. SELinux 是否会影响性能？
SELinux 对性能的影响很小（通常 <3%），但不当配置可能导致严重性能下降。建议：
- 使用 targeted 策略（较 strict 性能更好）
- 定期检查 SELinux 规则大小
- 监控 SELinux 违规事件频率

## 最佳实践

### 生产环境分阶段启用
```yaml
- name: 生产环境分阶段启用 SELinux
  block:
    - name: 第一阶段：启用 permissive 模式
      ansible.posix.selinux:
        state: permissive
        policy: targeted
        reload: yes
      become: yes
    
    - name: 第二阶段：监控审计日志（1-2 周）
      ansible.builtin.debug:
        msg: "请监控 /var/log/audit/audit.log，检查 SELinux 违规情况"
    
    - name: 第三阶段：调整策略规则（可选）
      ansible.builtin.debug:
        msg: "根据审计日志生成自定义规则，使用 audit2allow -M myapp"
    
    - name: 第四阶段：切换到 enforcing 模式
      ansible.posix.selinux:
        state: enforcing
        policy: targeted
      become: yes
      when: selinux_audit_passed | default(false)
```

### 容器化应用 SELinux 配置
```yaml
- name: 配置容器 SELinux 上下文
  block:
    - name: 启用 SELinux 宽容模式以支持容器
      ansible.posix.selinux:
        state: permissive
        policy: targeted
      become: yes
    
    - name: 配置容器运行用户的 SELinux 上下文（演示）
      ansible.builtin.shell: |
        semanage fcontext -a -t container_runtime_t "/opt/mycontainer(/.*)?";
        restorecon -R /opt/mycontainer
      become: yes
      when: manage_container_context | default(false)
```

### 与审计系统协同
```yaml
- name: 启用 SELinux 并配置审计
  block:
    - name: 启用 SELinux enforcing 模式
      ansible.posix.selinux:
        state: enforcing
        policy: targeted
        reload: yes
      become: yes
    
    - name: 启动审计守护进程（如果可用）
      ansible.builtin.systemd:
        name: auditd
        enabled: yes
        state: started
      become: yes
      ignore_errors: yes
```

## 相关示例
- [service 模块](../service/README.md) - 系统服务管理
- [systemd 模块](../systemd/README.md) - systemd 单元管理
- [firewalld 模块](../firewalld/README.md) - 防火墙管理（可与 SELinux 协同）
