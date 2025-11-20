# kernel_tuning 内核调优模块使用指南

## 模块用途
`kernel_tuning` 模块用于配置 Linux 内核参数，通过调整 sysctl 参数来优化系统性能、增强网络安全性、提升系统稳定性。支持内存管理、网络栈优化、安全加固、文件系统调优等场景。适用于性能优化、安全加固、高负载环境配置等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `kernel_params` | dict | 内核参数配置字典 | 网络参数、内存参数、安全参数 |
| `network_settings` | dict | 网络栈优化配置 | TCP/IP 调优、防火墙参数 |
| `memory_settings` | dict | 内存管理配置 | 交换分区、缓存策略 |
| `security_settings` | dict | 安全加固配置 | IP转发、源路由、SYN保护 |
| `filesystem_settings` | dict | 文件系统优化配置 | 文件描述符、inode限制 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `kernel_params_updated` | 是否更新了内核参数 | true/false |
| `network_optimizations` | 网络优化参数应用状态 | applied/failed |
| `memory_tuning` | 内存调优参数状态 | tuned/not_tuned |
| `security_hardening` | 安全加固参数状态 | hardened/not_hardened |
| `filesystem_optimization` | 文件系统优化状态 | optimized/not_optimized |
| `changed` | 是否修改了内核配置 | true/false |

## 使用情境

### 高性能服务器优化
**场景**：在高负载 Web 服务器上优化内核参数提升性能
- 调整 TCP/IP 栈参数提升网络吞吐量
- 优化内存管理和页面缓存策略
- 配置文件描述符限制支持更多并发连接
- 调整进程调度参数提升响应性能

### 数据库服务器调优
**场景**：在数据库服务器上配置内核参数优化 I/O 性能
- 调整虚拟内存和交换分区使用策略
- 优化 I/O 调度器和文件系统参数
- 配置共享内存和信号量限制
- 调整网络参数支持高并发数据库连接

### 安全加固配置
**场景**：在安全敏感环境中配置内核安全参数
- 禁用不必要的网络功能（IP转发、源路由）
- 启用 SYN flood 保护和其他网络防护
- 配置内核级的安全限制和审计
- 调整进程和资源限制防止 DoS 攻击

### 容器化环境优化
**场景**：在容器宿主机上优化内核参数支持容器运行
- 调整 cgroup 相关内核参数
- 优化网络命名空间和虚拟网络设备
- 配置文件系统支持容器镜像存储
- 调整内存管理支持容器内存限制

## 安全注意事项

1. **内核参数变更风险**：
   - 错误的内核参数可能导致系统不稳定或无法启动
   - 在生产环境部署前必须充分测试参数效果
   - 保留原始配置以便快速回滚

2. **性能影响评估**：
   - 某些参数可能对特定工作负载产生负面影响
   - 需要根据实际应用场景调整参数值
   - 监控系统性能指标评估调优效果

3. **安全配置平衡**：
   - 过于严格的安全参数可能影响系统功能
   - 平衡安全性和可用性，避免影响业务运行
   - 定期评估和更新安全参数配置

4. **版本兼容性**：
   - 不同内核版本的参数支持可能不同
   - 某些参数在特定内核版本中已废弃或变更
   - 需要考虑系统升级时的参数兼容性

## 环境依赖

### 必需
- 目标主机为 Linux 系统
- sysctl 工具已安装
- 需要管理员权限修改内核参数
- 内核支持相应的参数配置

### 推荐
- sysstat（性能监控工具）
- iotop（I/O 监控）
- netstat/ss（网络连接监控）
- lsof（文件描述符监控）

### 系统支持
- RHEL/CentOS 6/7/8/9：全面支持
- Ubuntu 16.04+：支持
- Debian 8+：支持
- SUSE Linux Enterprise：支持
- 其他 Linux 发行版：基本支持

## 常见问题

### 1. 内核参数设置不生效
检查参数配置和加载：
```bash
# 检查当前参数值
sysctl -a | grep parameter_name

# 手动设置测试
sysctl -w parameter.name=value

# 检查配置文件语法
sysctl -p /etc/sysctl.conf
```

### 2. 系统重启后参数丢失
确认配置文件持久化：
```bash
# 检查 sysctl 配置文件
cat /etc/sysctl.conf
cat /etc/sysctl.d/*.conf

# 验证配置文件语法
sysctl -p /etc/sysctl.conf
```

### 3. 参数设置导致系统问题
回滚配置：
```bash
# 恢复默认值
sysctl -w parameter.name=default_value

# 备份当前配置
sysctl -a > /tmp/sysctl_backup.conf

# 从备份恢复
sysctl -p /tmp/sysctl_backup.conf
```

### 4. 性能调优效果不明显
监控和评估：
```bash
# 监控系统性能
vmstat 1
iostat 1
sar -n DEV 1

# 检查参数是否生效
sysctl parameter.name
```

## 最佳实践

### 分阶段调优策略
```yaml
- name: 分阶段内核调优
  block:
    - name: 第一阶段：基础网络优化
      ansible.posix.sysctl:
        name: net.core.rmem_max
        value: "{{ network_settings.rmem_max }}"
        state: present
        sysctl_file: /etc/sysctl.d/99-network.conf
      become: yes
    
    - name: 第二阶段：内存管理优化
      ansible.posix.sysctl:
        name: vm.swappiness
        value: "{{ memory_settings.swappiness }}"
        state: present
        sysctl_file: /etc/sysctl.d/99-memory.conf
      become: yes
```

### 安全加固配置
```yaml
- name: 安全加固内核参数
  ansible.posix.sysctl:
    name: "{{ item.name }}"
    value: "{{ item.value }}"
    state: present
    sysctl_file: /etc/sysctl.d/99-security.conf
  become: yes
  loop:
    - { name: "net.ipv4.ip_forward", value: "0" }
    - { name: "net.ipv4.conf.all.send_redirects", value: "0" }
    - { name: "net.ipv4.conf.all.accept_source_route", value: "0" }
```

### 性能监控集成
```yaml
- name: 调优后性能验证
  block:
    - name: 收集系统性能指标
      ansible.builtin.shell: |
        vmstat 1 3 | tail -1
        iostat -x 1 2 | tail -n +4
      register: performance_metrics
    
    - name: 显示性能指标
      ansible.builtin.debug:
        msg: "{{ performance_metrics.stdout_lines }}"
```

## 相关示例
- [selinux 模块](../selinux/README.md) - SELinux 安全策略
- [firewalld 模块](../firewalld/README.md) - 防火墙管理
- [service 模块](../service/README.md) - 系统服务管理
- [systemd 模块](../systemd/README.md) - systemd 单元管理