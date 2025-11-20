# interface 模块使用指南

## 模块用途
`community.general.nmcli` 模块用于管理 Linux 系统的网络接口配置，通过 NetworkManager 的命令行工具实现接口的创建、修改、删除和状态管理。此模块适用于服务器网络配置、虚拟化管理、容器网络、VPN 连接等场景，能够统一管理不同类型的网络接口（以太网、VLAN、Bridge、Bond 等）。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `conn_name` | str | 连接名称 | eth0、br0、vlan100 等 |
| `ifname` | str | 接口名称 | eth0、ens33、enp0s3 等 |
| `type` | str | 连接类型 | ethernet、bridge、bond、vlan 等 |
| `autoconnect` | bool | 是否自动连接 | true、false |
| `ip4` | str | IPv4 地址配置 | 192.168.1.100/24、dhcp 等 |
| `gw4` | str | IPv4 网关地址 | 192.168.1.1 等 |
| `dns4` | list | IPv4 DNS 服务器 | ["8.8.8.8", "8.8.4.4"] 等 |
| `method4` | str | IPv4 配置方法 | auto（DHCP）、manual（静态）等 |
| `state` | str | 连接状态 | present、absent、up、down |
| `master` | str | 主接口名称（用于 slave） | br0、bond0 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 配置是否发生变更 | true、false |
| `rc` | 命令返回码 | 0（成功）、非 0（失败） |
| `stderr` | 错误输出信息 | 错误详情 |
| `stdout` | 标准输出信息 | nmcli 命令执行结果 |

## 常见字段说明

### 连接类型 (type)
- **ethernet**：标准以太网接口
- **bridge**：网桥接口（用于虚拟化）
- **bond**：绑定接口（链路聚合）
- **vlan**：VLAN 接口
- **team**：Team 接口（另一种绑定方式）
- **wifi**：无线网络接口

### IP 配置方法 (method4)
- **auto**：自动获取 IP 地址（DHCP）
- **manual**：手动配置静态 IP 地址
- **disabled**：禁用 IPv4
- **link-local**：链路本地地址

### 连接状态 (state)
- **present**：创建或更新连接配置
- **absent**：删除连接配置
- **up**：激活连接
- **down**：停用连接

### 自动连接 (autoconnect)
- **true**：系统启动时自动激活连接
- **false**：需要手动激活连接

## 适用场景

### 服务器网络配置
**场景**：数据中心服务器的网络接口标准化配置
- 配置管理网络接口
- 设置业务网络接口
- 配置存储网络接口
- 实现网络配置的一致性

### 虚拟化管理
**场景**：KVM、Docker 等虚拟化环境的网络管理
- 创建和管理网桥接口
- 配置 VLAN 网络
- 管理 Docker 网络接口
- 支持虚拟机网络隔离

### 高可用网络
**场景**：使用绑定接口提高网络可靠性
- 配置主备网络绑定
- 实现负载均衡绑定
- 网络故障自动切换
- 提高网络吞吐量

### 移动和远程网络
**场景**：笔记本或远程设备的网络管理
- WiFi 网络配置
- VPN 连接管理
- 多网络环境切换
- 网络配置模板化

## 安全注意事项

1. **网络中断风险**：修改生产网络接口前确保有备用连接
2. **配置备份**：修改前备份现有网络配置
3. **测试验证**：在测试环境验证配置的正确性
4. **权限控制**：限制网络配置权限，避免未授权修改
5. **监控告警**：配置网络接口状态监控
6. **回滚机制**：准备网络配置回滚方案
7. **依赖管理**：确保 NetworkManager 服务正常运行
8. **配置一致性**：保持集群中网络配置的一致性

## 最佳实践

### 1. 基础接口配置
```yaml
# 配置静态 IP 接口
- name: 配置管理网络接口
  community.general.nmcli:
    conn_name: "mgmt-eth0"
    ifname: "eth0"
    type: "ethernet"
    autoconnect: true
    ip4: "192.168.1.100/24"
    gw4: "192.168.1.1"
    dns4: ["8.8.8.8", "8.8.4.4"]
    method4: "manual"
    state: "present"
```

### 2. DHCP 接口配置
```yaml
# 配置 DHCP 接口
- name: 配置业务网络接口
  community.general.nmcli:
    conn_name: "business-eth1"
    ifname: "eth1"
    type: "ethernet"
    autoconnect: true
    method4: "auto"
    state: "present"
```

### 3. 网桥接口配置
```yaml
# 创建网桥接口
- name: 创建虚拟化网桥
  community.general.nmcli:
    conn_name: "br0"
    ifname: "br0"
    type: "bridge"
    autoconnect: true
    ip4: "192.168.100.1/24"
    method4: "manual"
    state: "present"
  notify: 重新加载 NetworkManager

# 将物理接口加入网桥
- name: 将物理接口加入网桥
  community.general.nmcli:
    conn_name: "eth0-br0"
    ifname: "eth0"
    type: "ethernet"
    master: "br0"
    slave_type: "bridge"
    state: "present"
```

### 4. 绑定接口配置
```yaml
# 创建绑定接口
- name: 创建网络绑定接口
  community.general.nmcli:
    conn_name: "bond0"
    ifname: "bond0"
    type: "bond"
    autoconnect: true
    ip4: "192.168.1.200/24"
    gw4: "192.168.1.1"
    method4: "manual"
    mode: "active-backup"
    state: "present"
  notify: 重新加载 NetworkManager

# 添加物理接口到绑定
- name: 将物理接口加入绑定
  community.general.nmcli:
    conn_name: "eth0-bond0"
    ifname: "eth0"
    type: "ethernet"
    master: "bond0"
    slave_type: "bond"
    state: "present"
```

## 测试步骤

### 1. 接口状态检查
```bash
# 查看网络连接状态
nmcli connection show

# 查看接口详细信息
nmcli device show

# 查看接口 IP 配置
ip addr show
```

### 2. 连通性测试
```bash
# 测试接口连通性
ping -c 3 -I eth0 8.8.8.8

# 测试网关连通性
ping -c 3 192.168.1.1

# 测试 DNS 解析
nslookup google.com
```

### 3. Ansible 测试
```bash
# 语法检查
ansible-playbook network/interface/playbook.yml --syntax-check

# Dry-Run 预览
ansible-playbook network/interface/playbook.yml --check

# 执行配置
ansible-playbook network/interface/playbook.yml
```

## 常见问题

### 接口配置后无法连接网络怎么办？
1. 检查 IP 地址和网关配置是否正确
2. 验证网络接口物理连接状态
3. 检查防火墙规则是否阻止连接
4. 确认 NetworkManager 服务状态

### 网桥或绑定接口不工作？
1. 确保相关的内核模块已加载
2. 检查物理接口是否正确加入网桥/绑定
3. 验证网桥/绑定的配置参数
4. 检查系统日志中的错误信息

### 如何安全地修改生产网络配置？
1. 通过控制台或带外管理访问
2. 在维护窗口期间操作
3. 先配置新接口，再停用旧接口
4. 准备配置回滚脚本

## 依赖说明

### 必需依赖
- **community.general collection**：提供 `community.general.nmcli` 模块
- **NetworkManager**：Linux 网络管理服务
- **nmcli 工具**：NetworkManager 命令行工具
- **系统权限**：需要 root 权限修改网络配置

### 系统要求
- **Linux 系统**：支持 NetworkManager 的现代 Linux 发行版
- **内核支持**：支持相应网络接口类型的内核模块
- **服务状态**：NetworkManager 服务运行正常

### 可选依赖
- **网络工具**：iproute2、net-tools 等网络诊断工具
- **监控工具**：用于监控网络接口状态的工具
- **配置管理**：网络配置文件的备份和版本控制

### 安装依赖
```bash
# 安装 community.general collection
ansible-galaxy collection install community.general

# 安装 NetworkManager（RHEL/CentOS）
yum install -y NetworkManager

# 安装 NetworkManager（Ubuntu/Debian）
apt install -y network-manager

# 启动并启用 NetworkManager
systemctl enable --now NetworkManager
```

## 相关示例

### 基础以太网接口配置
```yaml
- name: 配置静态 IP 以太网接口
  community.general.nmcli:
    conn_name: "static-eth0"
    ifname: "eth0"
    type: "ethernet"
    autoconnect: true
    ip4: "192.168.1.100/24"
    gw4: "192.168.1.1"
    dns4: ["8.8.8.8", "1.1.1.1"]
    method4: "manual"
    state: "present"
```

### DHCP 接口配置示例
```yaml
- name: 配置 DHCP 以太网接口
  community.general.nmcli:
    conn_name: "dhcp-eth1"
    ifname: "eth1"
    type: "ethernet"
    autoconnect: true
    method4: "auto"
    state: "present"
```

### VLAN 接口配置示例
```yaml
- name: 创建 VLAN 接口
  community.general.nmcli:
    conn_name: "vlan100"
    ifname: "eth0.100"
    type: "vlan"
    autoconnect: true
    ip4: "192.168.100.10/24"
    method4: "manual"
    vlanid: 100
    vlandev: "eth0"
    state: "present"
```

### 接口删除示例
```yaml
- name: 删除网络连接配置
  community.general.nmcli:
    conn_name: "old-connection"
    state: "absent"
```

### 条件性接口配置示例
```yaml
- name: 生产环境网络接口配置
  community.general.nmcli:
    conn_name: "prod-eth0"
    ifname: "eth0"
    type: "ethernet"
    autoconnect: true
    ip4: "{{ item.ip }}"
    gw4: "{{ item.gateway }}"
    dns4: "{{ item.dns }}"
    method4: "manual"
    state: "present"
  loop: "{{ production_interfaces }}"
  when: 
    - ansible_environment == "production"
    - production_interfaces is defined
  notify: 重新加载 NetworkManager
```