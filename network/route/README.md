# route 模块使用指南

## 模块用途
`ansible.posix.route` 模块用于管理系统的静态路由表，支持添加、删除和修改路由规则。此模块适用于多网卡环境、复杂网络拓扑、VPN 配置、容器网络等场景，能够精确控制网络流量的路径选择。通过 Ansible 的幂等性特性，可以确保路由配置的一致性和可重复性。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `dest` | str | 目标网络地址（CIDR 格式） | 192.168.1.0/24、10.0.0.0/8 等 |
| `gw` | str | 网关 IP 地址 | 192.168.1.1、10.0.0.1 等 |
| `dev` | str | 网络接口名称 | eth0、ens33、br0 等 |
| `metric` | int | 路由优先级（跃点数） | 100、200、300 等 |
| `netmask` | str | 子网掩码（兼容性参数） | 255.255.255.0、255.0.0.0 等 |
| `state` | str | 路由状态 | present（存在）、absent（删除） |
| `src` | str | 源 IP 地址（可选） | 192.168.1.100 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 路由是否发生变更 | true、false |
| `cmd` | 执行的系统命令 | "ip route add 192.168.1.0/24 via 192.168.1.1" |
| `rc` | 命令返回码 | 0（成功）、非 0（失败） |
| `stderr` | 错误输出信息 | 错误详情 |
| `stdout` | 标准输出信息 | 命令执行结果 |

## 常见字段说明

### 路由目标 (dest)
- **网络路由**：指定目标网络段，如 `192.168.1.0/24`
- **主机路由**：指定单个主机，如 `192.168.1.100/32`
- **默认路由**：使用 `0.0.0.0/0` 表示所有目标

### 网关配置 (gw)
- **下一跳地址**：数据包转发的下一跳路由器 IP
- **多网关**：可通过 metric 参数设置优先级
- **本地网关**：通常是本网段的路由器地址

### 接口指定 (dev)
- **物理接口**：eth0、ens33、enp0s3 等
- **虚拟接口**：br0、docker0、virbr0 等
- **VPN 接口**：tun0、wg0 等

### 路由优先级 (metric)
- **数值越小优先级越高**：metric 100 优于 metric 200
- **默认值**：通常为 0 或系统默认值
- **用途**：多路径路由中的路径选择

## 适用场景

### 多网卡环境路由
**场景**：服务器配置多个网卡，需要指定不同网络段的流量走向
- 管理网络路由 → 管理接口
- 业务网络路由 → 业务接口
- 存储网络路由 → 存储接口

### VPN 和专线接入
**场景**：通过 VPN 或专线连接到远程网络
- VPN 网络路由 → VPN 隧道接口
- 专线网络路由 → 专线接口
- 备份路由 → 低优先级备份链路

### 容器和虚拟化网络
**场景**：容器或虚拟机需要特殊的网络路由
- 容器网络路由 → 网桥接口
- 虚拟机网络路由 → 虚拟网络接口
- Overlay 网络路由 → 隧道接口

### 复杂网络拓扑
**场景**：企业网络中的多层级路由配置
- 分支机构路由 → 专线网关
- 数据中心路由 → 核心路由器
- 互联网路由 → 边界路由器

## 安全注意事项

1. **网络连通性验证**：路由变更前验证网络连通性，避免网络中断
2. **备份现有路由**：修改前备份当前路由表，便于故障恢复
3. **分阶段部署**：在测试环境验证后再部署到生产环境
4. **回滚机制**：准备路由回滚方案，应对配置错误
5. **权限控制**：限制路由配置权限，避免未授权修改
6. **监控告警**：配置路由变更监控，及时发现异常
7. **系统兼容性**：注意不同操作系统（RHEL/Ubuntu）的路由命令差异
8. **网络拓扑理解**：充分理解网络拓扑结构，避免路由环路

## 最佳实践

### 1. 系统兼容性处理
```yaml
# 根据操作系统类型使用不同的路由配置
- name: 添加静态路由 (RHEL/CentOS)
  ansible.posix.route:
    dest: "{{ item.dest }}"
    gw: "{{ item.gw }}"
    state: present
  loop: "{{ static_routes }}"
  when: ansible_os_family == "RedHat"

- name: 添加静态路由 (Ubuntu/Debian)
  ansible.posix.route:
    dest: "{{ item.dest }}"
    gw: "{{ item.gw }}"
    state: present
  loop: "{{ static_routes }}"
  when: ansible_os_family == "Debian"
```

### 2. 路由优先级管理
```yaml
# 主路由（高优先级）
- name: 配置主业务路由
  ansible.posix.route:
    dest: 10.0.0.0/8
    gw: 192.168.1.1
    metric: 100
    state: present

# 备份路由（低优先级）
- name: 配置备份业务路由
  ansible.posix.route:
    dest: 10.0.0.0/8
    gw: 192.168.2.1
    metric: 200
    state: present
```

### 3. 接口特定路由
```yaml
# 管理网络路由
- name: 配置管理网络路由
  ansible.posix.route:
    dest: 172.16.0.0/16
    gw: 172.16.1.1
    dev: eth0
    state: present

# 存储网络路由
- name: 配置存储网络路由
  ansible.posix.route:
    dest: 10.10.0.0/16
    gw: 10.10.1.1
    dev: eth1
    state: present
```

## 测试步骤

### 1. 路由配置验证
```bash
# 检查当前路由表
ip route show
# 或
route -n

# 验证特定路由
ip route get 8.8.8.8
```

### 2. 连通性测试
```bash
# 测试目标网络连通性
ping -c 3 192.168.1.1

# 跟踪路由路径
traceroute 8.8.8.8
```

### 3. Ansible 测试
```bash
# 语法检查
ansible-playbook network/route/playbook.yml --syntax-check

# Dry-Run 预览
ansible-playbook network/route/playbook.yml --check

# 执行配置
ansible-playbook network/route/playbook.yml
```

## 常见问题

### 路由配置后网络不通怎么办？
1. 检查网关 IP 地址是否正确
2. 验证网络接口是否正常工作
3. 确认防火墙规则是否允许流量
4. 检查目标网络是否存在路由环路

### 如何处理多网关场景？
1. 使用 metric 参数设置优先级
2. 配置路由策略 (ip rule)
3. 使用源路由 (source routing)
4. 考虑使用动态路由协议

### 路由配置如何避免网络中断？
1. 在维护窗口期间操作
2. 先添加新路由，再删除旧路由
3. 准备回滚脚本
4. 使用 check_mode 预览变更

## 依赖说明

### 必需依赖
- **ansible.posix collection**：提供 `ansible.posix.route` 模块
- **系统权限**：需要 root 权限修改路由表
- **系统工具**：`iproute2` 包（提供 ip 命令）或 `net-tools` 包（提供 route 命令）

### 系统要求
- **Linux 系统**：支持 iproute2 的现代 Linux 发行版
- **内核支持**：内核支持多路由表和策略路由
- **网络配置**：网络接口已正确配置并启用

### 可选依赖
- **网络工具**：net-tools、iproute2、traceroute
- **监控工具**：用于监控路由变更的工具
- **配置管理**：网络配置文件的备份和版本控制

### 安装依赖
```bash
# 安装 ansible.posix collection
ansible-galaxy collection install ansible.posix

# 安装系统工具（RHEL/CentOS）
yum install -y iproute

# 安装系统工具（Ubuntu/Debian）
apt install -y iproute2
```

## 相关示例

### 基础路由配置示例
```yaml
- name: 添加默认路由
  ansible.posix.route:
    dest: 0.0.0.0/0
    gw: 192.168.1.1
    state: present

- name: 添加网络路由
  ansible.posix.route:
    dest: 192.168.100.0/24
    gw: 192.168.1.254
    state: present
```

### 多接口路由示例
```yaml
- name: 配置管理网络路由
  ansible.posix.route:
    dest: 172.16.0.0/16
    gw: 172.16.1.1
    dev: eth0
    metric: 100
    state: present

- name: 配置业务网络路由
  ansible.posix.route:
    dest: 10.0.0.0/8
    gw: 10.0.1.1
    dev: eth1
    metric: 100
    state: present
```

### 路由删除示例
```yaml
- name: 删除旧的路由配置
  ansible.posix.route:
    dest: 192.168.200.0/24
    gw: 192.168.1.254
    state: absent
```

### 条件性路由配置示例
```yaml
- name: 生产环境特殊路由
  ansible.posix.route:
    dest: "{{ item.dest }}"
    gw: "{{ item.gw }}"
    metric: "{{ item.metric | default(100) }}"
    state: present
  loop: "{{ production_routes }}"
  when: 
    - ansible_environment == "production"
    - production_routes is defined
```