# reboot 模块使用指南

## 模块用途
`ansible.builtin.reboot` 模块用于重启远程主机，支持等待系统重启完成、验证重启状态等功能。适用于系统更新后重启、内核更新、配置变更生效等需要重启系统的场景。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `reboot_timeout` | int | 重启超时时间（秒） | 600、900、1800 等 |
| `connect_timeout` | int | 连接超时时间（秒） | 60、120、300 等 |
| `pre_reboot_delay` | int | 重启前延迟时间（秒） | 0、10、30 等 |
| `post_reboot_delay` | int | 重启后延迟时间（秒） | 10、30、60 等 |
| `test_command` | str | 验证重启成功的测试命令 | "whoami"、"uptime" 等 |
| `msg` | str | 重启前发送给用户的消息 | "系统将重启进行更新" 等 |
| `search_paths` | list | 搜索 reboot 命令的路径 | ["/sbin", "/usr/sbin", "/usr/local/sbin"] |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了重启 | true/false |
| `rebooted` | 系统是否已重启 | true/false |
| `elapsed` | 重启耗时（秒） | 120 |
| `msg` | 操作结果消息 | "Reboot successful" |

## 使用情境

### 系统更新场景
- **内核更新后**：安装新内核后需要重启生效
- **系统补丁**：安装关键安全补丁后重启
- **glibc 更新**：系统库更新后需要重启服务
- **系统升级**：大版本系统升级后重启

### 配置变更场景
- **网络配置**：重大网络配置变更后重启
- **存储配置**：磁盘分区或文件系统变更后重启
- **系统参数**：内核参数或系统配置变更后重启
- **服务配置**：系统级服务配置变更后重启

### 维护操作场景
- **定期维护**：计划性系统维护重启
- **性能优化**：内存清理或性能调优后重启
- **故障恢复**：系统异常后的重启恢复
- **环境切换**：测试环境到生产环境的切换

## 安全注意事项

### 重启前准备
1. **数据保存**：确保所有重要数据已保存
2. **服务通知**：提前通知相关用户和服务
3. **备份检查**：确认重要数据已备份
4. **依赖检查**：检查重启依赖的服务和系统

### 重启过程控制
1. **超时设置**：设置合理的重启超时时间
2. **状态监控**：监控重启过程和状态
3. **失败处理**：准备重启失败的应对方案
4. **回滚计划**：准备系统回滚方案

### 重启后验证
1. **服务检查**：验证关键服务是否正常启动
2. **连接测试**：测试网络连接和远程访问
3. **功能验证**：验证系统功能是否正常
4. **日志检查**：检查系统日志是否有错误

## 环境依赖

### 必需
- 目标主机必须支持 reboot 命令
- Ansible 控制节点与目标主机网络连接
- 足够的权限执行重启操作

### 推荐
- 系统支持 shutdown/reboot 命令
- 配置合理的 SSH 连接参数
- 启用系统日志记录

## 常见问题

### 1. 重启超时
**可能原因**：
- 系统启动时间过长
- 网络连接延迟
- 服务启动失败
- 硬件问题

**解决方案**：
```yaml
- name: 增加重启超时时间
  ansible.builtin.reboot:
    reboot_timeout: 1800  # 30分钟
    connect_timeout: 300  # 5分钟
```

### 2. SSH 连接失败
**可能原因**：
- SSH 服务未启动
- 防火墙阻止连接
- 网络配置问题
- 主机名解析失败

**排查方法**：
```bash
# 检查 SSH 服务状态
sudo systemctl status sshd

# 检查网络连接
ping hostname

# 检查防火墙状态
sudo ufw status
```

### 3. 重启后系统异常
**可能原因**：
- 服务配置错误
- 磁盘空间不足
- 权限问题
- 硬件故障

**排查方法**：
```bash
# 检查系统日志
sudo journalctl -xe

# 检查磁盘空间
df -h

# 检查服务状态
sudo systemctl status
```

## 最佳实践

### 基础重启示例
```yaml
- name: 重启系统
  ansible.builtin.reboot:
    msg: "系统将重启进行系统更新"
```

### 带超时控制的重启示例
```yaml
- name: 重启系统并等待完成
  ansible.builtin.reboot:
    reboot_timeout: 600  # 10分钟重启超时
    connect_timeout: 120  # 2分钟连接超时
    pre_reboot_delay: 10  # 重启前延迟10秒
    post_reboot_delay: 30  # 重启后延迟30秒
```

### 带验证命令的重启示例
```yaml
- name: 重启系统并验证
  ansible.builtin.reboot:
    reboot_timeout: 900
    test_command: "whoami"  # 验证命令
```

### 分阶段重启示例
```yaml
- name: 通知用户即将重启
  ansible.builtin.shell: |
    echo "系统将在 5 分钟后重启进行维护" | wall
    sleep 300  # 等待5分钟

- name: 执行系统重启
  ansible.builtin.reboot:
    msg: "系统维护重启"
    reboot_timeout: 600
```

### 条件重启示例
```yaml
- name: 检查是否需要重启
  ansible.builtin.shell: |
    if [ -f /var/run/reboot-required ]; then
      echo "reboot_needed"
    else
      echo "no_reboot"
    fi
  register: reboot_check

- name: 重启系统（如果需要）
  ansible.builtin.reboot:
    msg: "检测到重启需求，执行系统重启"
  when: reboot_check.stdout == "reboot_needed"
```

### 批量重启示例
```yaml
- name: 重启 Web 服务器组
  ansible.builtin.reboot:
    msg: "Web 服务器维护重启"
    reboot_timeout: 600
  delegate_to: "{{ item }}"
  loop: "{{ groups['webservers'] }}"
  serial: 1  # 逐个重启，避免服务中断
```

### 重启后验证示例
```yaml
- name: 重启数据库服务器
  ansible.builtin.reboot:
    msg: "数据库服务器重启"
    reboot_timeout: 900
    test_command: "systemctl is-active mysql"

- name: 验证数据库服务状态
  ansible.builtin.systemd:
    name: mysql
    state: started
    enabled: yes

- name: 测试数据库连接
  ansible.builtin.shell: |
    mysql -u root -e "SELECT 1"
  register: db_test

- name: 显示数据库连接测试结果
  ansible.builtin.debug:
    msg: "数据库连接测试结果: {{ '成功' if db_test.rc == 0 else '失败' }}"
```

### 安全重启示例
```yaml
- name: 安全重启生产系统
  ansible.builtin.reboot:
    msg: "生产系统计划维护重启"
    reboot_timeout: 1800  # 30分钟超时
    pre_reboot_delay: 60   # 重启前1分钟延迟
    post_reboot_delay: 120 # 重启后2分钟延迟
    test_command: "systemctl is-active nginx && systemctl is-active mysql"
  register: reboot_result

- name: 记录重启结果
  ansible.builtin.lineinfile:
    path: /var/log/system_reboots.log
    line: "{{ ansible_date_time.iso8601 }} - {{ inventory_hostname }} - 重启结果: {{ '成功' if reboot_result.rebooted else '失败' }}"
    create: yes
```

## 相关示例
- [service 模块](../service/README.md) - 服务管理
- [systemd 模块](../systemd/README.md) - systemd 单元管理
- [user 模块](../user/README.md) - 用户管理
- [cron 模块](../cron/README.md) - 定时任务管理