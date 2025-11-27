# seboolean 模块使用指南

## 模块用途
`ansible.posix.seboolean` 模块用于管理 SELinux 布尔值，这些布尔值控制 SELinux 策略的特定行为。通过修改布尔值，可以在不重新编译 SELinux 策略的情况下调整安全策略的行为，如允许 HTTP 服务访问网络、允许用户登录等。在 RHEL/CentOS 等支持 SELinux 的系统中，这是灵活调整安全策略的重要工具。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | SELinux 布尔值名称 | httpd_can_network_connect、ftp_home_dir 等 |
| `state` | str | 布尔值状态（on/off、yes/no、true/false） | on、off、yes、no、true、false |
| `persistent` | bool | 是否永久保存设置 | true、false |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否修改了布尔值状态 | true/false |
| `name` | 修改的布尔值名称 | httpd_can_network_connect |
| `state` | 设置后的状态 | on/off |

## 使用情境

### Web 服务安全配置
**场景**：允许 Web 服务器访问网络资源，但限制其他服务
- 启用 httpd_can_network_connect 允许 Apache/Nginx 访问网络
- 禁用不必要的网络访问权限
- 与 firewalld 协同配置网络安全策略

### FTP 服务配置
**场景**：配置 FTP 服务的文件访问权限
- 启用 ftp_home_dir 允许用户访问家目录
- 配置 ftpd_full_access 允许完整文件系统访问
- 根据安全需求调整访问权限

### 用户权限管理
**场景**：调整用户登录和权限相关设置
- 配置 ssh_keysign 允许 SSH 密钥签名
- 管理用户空间相关的 SELinux 权限
- 实现最小权限原则

## 安全注意事项

1. **权限最小化原则**：
   - 只启用应用必需的 SELinux 布尔值
   - 定期审查已启用的布尔值，禁用不再需要的
   - 避免过度放宽安全策略

2. **变更影响评估**：
   - 修改布尔值前评估安全风险
   - 在测试环境验证变更影响
   - 记录变更原因和预期效果

3. **审计和监控**：
   - 监控 SELinux 违规日志
   - 定期检查布尔值状态
   - 与安全团队协作制定策略

4. **生产环境谨慎操作**：
   - 分阶段启用关键布尔值
   - 准备回滚方案
   - 监控应用行为变化

## 环境依赖

### 必需
- 目标主机支持 SELinux（RHEL、CentOS、Fedora 等）
- selinux-policy-targeted 或相关策略包
- setroubleshoot 工具包（用于故障排查）
- 需要 root 或 sudo 权限

### 推荐
- policycoreutils-python-utils 包
- setools-console 包（用于策略分析）
- auditd 审计系统

## 常见问题

### 1. 如何查看所有可用的 SELinux 布尔值？
使用 getsebool 命令查看所有布尔值：
```bash
getsebool -a
```

### 2. 修改布尔值后立即生效吗？
是的，布尔值修改立即生效，但重启后可能恢复。使用 persistent: true 确保永久保存。

### 3. 如何查看布尔值的作用？
使用 semanage boolean -l 命令查看详细说明：
```bash
semanage boolean -l | grep httpd
```

### 4. 布尔值修改失败怎么办？
检查 SELinux 模式是否为 enforcing 或 permissive，确认布尔值名称正确。

## 最佳实践

### 生产环境分阶段配置
```yaml
- name: 分阶段启用 SELinux 布尔值
  block:
    - name: 第一阶段：启用基础网络访问
      ansible.posix.seboolean:
        name: httpd_can_network_connect
        state: on
        persistent: true
      become: yes
      
    - name: 第二阶段：监控应用行为
      ansible.builtin.debug:
        msg: "监控应用行为，确认网络访问正常"
      
    - name: 第三阶段：启用其他必需权限
      ansible.posix.seboolean:
        name: httpd_can_sendmail
        state: on
        persistent: true
      become: yes
      when: app_needs_email | default(false)
```

### 安全审计配置
```yaml
- name: 配置 SELinux 布尔值并记录变更
  ansible.posix.seboolean:
    name: "{{ item.name }}"
    state: "{{ item.state }}"
    persistent: true
  become: yes
  loop: "{{ selinux_booleans }}"
  register: boolean_changes
  
- name: 记录布尔值变更
  ansible.builtin.debug:
    msg: "SELinux 布尔值 {{ item.item.name }} 已设置为 {{ item.item.state }}"
  loop: "{{ boolean_changes.results }}"
  when: item.changed
```

## 相关示例
- [selinux 模块](../selinux/README.md) - SELinux 整体配置管理
- [firewalld 模块](../firewalld/README.md) - 防火墙规则管理
- [service 模块](../service/README.md) - 系统服务管理