# timezone 模块使用指南

## 模块用途
`ansible.builtin.timezone` 模块用于设置系统时区，支持多种操作系统和时区数据库。在服务器集群管理、日志时间戳统一、国际化部署等场景中必不可少。可确保分布式系统的时间一致性，防止由时区差异导致的日志错乱、计划任务失效等问题。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | 时区名称（必需），格式为 `大陆/城市` | Asia/Shanghai、UTC、America/New_York、Europe/London |
| `hwclock` | str | 硬件时钟是否使用 UTC（可选） | UTC、local |
| `utc` | bool | 是否使用 UTC（已过期，建议用 hwclock） | true、false |
| `ntp_service` | str | NTP 时间同步服务（可选） | ntpd、chronyd、systemd-timesyncd 等 |
| `timedatectl_bin` | str | timedatectl 命令的完整路径（可选） | /usr/bin/timedatectl 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `timezone` | 当前时区名称 | Asia/Shanghai |
| `hwclock_mode` | 硬件时钟模式 | local、UTC |
| `changed` | 是否修改了系统时区 | true/false |
| `ansible_facts` | Ansible 采集的事实信息 | ansible_date_time、ansible_system 等 |

## 使用情境

### 数据中心时区标准化
**场景**：将多地数据中心的服务器时区统一设置为 UTC 或统一的标准时区
- 避免日志中的时间戳混乱
- 确保分布式追踪、监控系统中的事件时间顺序准确
- 便于跨地域故障排查与时间关联分析

### 地理位置相关部署
**场景**：为不同地区的服务器设置本地时区
- 亚太地区数据中心：Asia/Shanghai、Asia/Tokyo 等
- 欧洲地区数据中心：Europe/London、Europe/Paris 等
- 美洲地区数据中心：America/New_York、America/Los_Angeles 等

### 容器与 Kubernetes 集群
**场景**：在容器镜像构建或集群初始化时统一设置时区
- 确保容器内应用日志时间戳准确
- 容器编排平台中 Pod 的时间同步

### 虚拟机与云实例初始化
**场景**：在云主机配置管理中自动设置时区
- VMware、KVM、OpenStack 虚拟机初始化
- AWS、Azure、阿里云等公有云实例的时区配置

## 安全注意事项

1. **硬件时钟同步**：
   - 确保 BIOS/UEFI 硬件时钟与系统时间同步
   - 物理服务器应定期验证硬件时钟准确性
2. **NTP 时间同步**：
   - 建议结合 NTP 或 chronyd 确保时间准确
   - 在修改时区前，确保 NTP 服务运行正常
3. **应用兼容性**：
   - 某些应用（如数据库、日志系统）对时区变更敏感
   - 修改时区前备份配置，应用变更后验证时间戳格式
4. **分布式系统**：
   - 在分布式系统中避免频繁修改时区，选择一次性统一
   - 跨时区部署时要明确时区设置策略

## 环境依赖

### 必需
- 目标主机的 `/usr/share/zoneinfo/` 目录包含时区数据库（通常 Linux 发行版已包含）
- 需要 root 或 sudo 权限修改系统时区

### 推荐
- NTP 服务（ntpd、chronyd 或 systemd-timesyncd）用于时间同步
- timedatectl 工具（systemd 系统上推荐使用，较 tzdata 更可靠）

### 系统支持
- CentOS/RHEL：使用 timedatectl 或修改 /etc/localtime
- Ubuntu/Debian：使用 timedatectl 或修改 /etc/timezone + /etc/localtime
- Alpine Linux：需要 tzdata 包

## 常见问题

### 1. 修改时区后，应用时间仍然不变
某些应用（如 Java 进程）缓存了时区信息，需要重启应用才能生效：
```yaml
- name: 修改时区后重启应用
  ansible.builtin.systemd:
    name: myapp
    state: restarted
  become: yes
```

### 2. NTP 时间同步不稳定
确保 NTP 服务运行正常，并使用 `timedatectl status` 验证：
```yaml
- name: 检查时间同步状态
  ansible.builtin.shell: |
    timedatectl status | grep synchronized
  register: ntp_status
```

### 3. 时区设置失败："Unknown timezone"
验证时区名称是否正确，并检查 `/usr/share/zoneinfo/` 中是否存在该时区文件：
```yaml
- name: 列出可用时区（示例）
  ansible.builtin.shell: |
    timedatectl list-timezones | grep -i shanghai
  register: available_tzones
```

### 4. 虚拟机中时区设置不生效
某些虚拟化平台（如 Hyper-V）需要在虚拟机配置中同步硬件时钟，检查 BIOS 时间：
```yaml
- name: 验证 BIOS 时间
  ansible.builtin.shell: |
    hwclock --show
  register: bios_time
```

## 最佳实践

### 生产环境时区管理
```yaml
- name: 统一设置生产数据中心时区
  ansible.builtin.timezone:
    name: UTC
    hwclock: UTC
  become: yes
  check_mode: true  # 先使用 --check 预览
```

### 地理位置相关配置
```yaml
- name: 根据地理位置设置时区
  ansible.builtin.timezone:
    name: "{{ timezone_by_region[region] }}"
    hwclock: UTC
  become: yes
  vars:
    timezone_by_region:
      asia: Asia/Shanghai
      eu: Europe/London
      us: America/New_York
```

### 与 NTP 服务协同
```yaml
- name: 设置时区并启动 NTP 时间同步
  block:
    - name: 设置时区
      ansible.builtin.timezone:
        name: Asia/Shanghai
        hwclock: UTC
      become: yes
    
    - name: 启动时间同步服务
      ansible.builtin.systemd:
        name: chronyd
        enabled: yes
        state: started
      become: yes
  rescue:
    - name: 失败时输出错误信息
      ansible.builtin.debug:
        msg: "时区设置失败，请检查 NTP 或时区数据库"
```

## 相关示例
- [hostname 模块](../hostname/README.md) - 主机名配置
- [service 模块](../service/README.md) - 服务管理（用于管理 NTP 服务）
- [systemd 模块](../systemd/README.md) - systemd 单元管理（用于 NTP 服务配置）
