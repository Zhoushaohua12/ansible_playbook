# VLAN 网络配置模块使用指南

## 模块用途
`community.general.nmcli` 模块用于配置 VLAN（虚拟局域网）网络接口，实现网络隔离、流量分割和多租户环境管理。VLAN 技术允许在同一物理网络设备上创建多个逻辑隔离的网络，广泛应用于企业网络、数据中心、云平台和多环境部署场景。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `conn_name` | str | VLAN 连接名称（必需） | `eth0.100`、`vlan100` 等 |
| `ifname` | str | VLAN 接口名称（可选） | `eth0.100`、`vlan100` 等 |
| `type` | str | 连接类型（必需） | `vlan` |
| `vlan_id` | int | VLAN ID 标识符（必需，1-4094） | 100、200、1000 等 |
| `dev` | str | 父物理接口名称（必需） | `eth0`、`enp0s3` 等 |
| `state` | str | 连接状态（present 创建/修改，absent 删除） | present、absent |
| `autoconnect` | bool | 是否自动连接（默认 true） | true、false |
| `method4` | str | IPv4 配置方法（auto 自动，manual 手动） | auto、manual、disabled |
| `ip4` | str | IPv4 地址（manual 模式时必需） | `192.168.100.10/24` |
| `gw4` | str | IPv4 网关地址（可选） | `192.168.100.1` |
| `dns4` | list | IPv4 DNS 服务器列表（可选） | `['8.8.8.8', '8.8.4.4']` |

## 高级参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `mtu` | int | 最大传输单元（可选） | 1500、9000 等 |
| `zone` | str | 防火墙区域（可选） | `public`、`trusted`、`internal` 等 |
| `method6` | str | IPv6 配置方法（auto 自动，manual 手动） | auto、manual、disabled |
| `ip6` | str | IPv6 地址（manual 模式时必需） | `2001:db8:100::1/64` |
| `gw6` | str | IPv6 网关地址（可选） | `2001:db8:100::ffff` |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了修改 | true/false |
| `conn_name` | VLAN 连接名称 | eth0.100 |
| `state` | 连接状态 | present/absent |
| `vlan_id` | VLAN ID | 100 |
| `msg` | 操作结果消息 | "Connection 'eth0.100' successfully added" |

## 使用情境

### 网络隔离
- **多环境隔离**：开发、测试、生产环境网络隔离
- **多租户环境**：云平台多租户网络隔离
- **部门网络**：企业内不同部门网络分割
- **安全隔离**：DMZ、内网、管理网络隔离

### 数据中心管理
- **存储网络**：iSCSI、NFS 等存储流量隔离
- **管理网络**：带外管理、IPMI 网络隔离
- **虚拟化网络**：虚拟机网络流量隔离
- **集群通信**：集群心跳、数据同步网络

### 服务分类
- **Web 服务层**：前端 Web 服务器 VLAN
- **应用服务层**：中间件、应用服务器 VLAN
- **数据库层**：数据库服务器 VLAN
- **缓存层**：Redis、Memcached 等缓存服务 VLAN

## 安全注意事项

### VLAN 安全
1. **VLAN 跳跃攻击防护**：禁用 DTP 协议，配置端口为 access 模式
2. **VLAN ID 规划**：合理规划 VLAN ID 范围，避免冲突
3. **跨 VLAN 访问控制**：通过 ACL 或防火墙控制跨 VLAN 通信
4. **私有 VLAN**：敏感环境使用私有 VLAN 技术

### 配置安全
1. **配置备份**：修改 VLAN 配置前备份当前设置
2. **测试验证**：配置后测试 VLAN 连通性和隔离性
3. **变更管理**：VLAN 配置变更应经过审批流程
4. **文档记录**：维护 VLAN 分配和用途文档

### 操作安全
1. **远程操作风险**：修改网络配置时注意远程连接可能中断
2. **标签一致性**：确保交换机端口和主机 VLAN 标签一致
3. **trunk 端口配置**：正确配置 trunk 端口允许的 VLAN 列表
4. **维护窗口**：在维护窗口期进行 VLAN 变更

## 环境依赖

### 必需
- NetworkManager 服务
- nmcli 命令行工具
- 支持 802.1Q VLAN 的网卡驱动
- 交换机支持 VLAN 标签

### 推荐
- NetworkManager-glib 包
- 8021q 内核模块
- VLAN 配置管理工具
- 网络监控工具

### 外部依赖
- **Ansible Collection**: `community.general` (版本 >= 7.0.0)
- **系统服务**: NetworkManager 服务必须运行
- **网络设备**: 交换机需要配置对应的 VLAN 标签

## 常见问题

### 1. VLAN 接口无法创建
**解决方案**：
```bash
# 检查 8021q 模块是否加载
lsmod | grep 8021q

# 加载 8021q 模块
sudo modprobe 8021q

# 永久加载
echo "8021q" | sudo tee -a /etc/modules

# 检查父接口是否存在
ip link show eth0
```

### 2. VLAN 流量无法通信
**可能原因**：
- 交换机端口未配置 VLAN 标签
- VLAN ID 不匹配
- 父接口未启用
- 防火墙规则阻止流量

**排查方法**：
```bash
# 检查 VLAN 接口状态
ip link show eth0.100

# 检查 VLAN 配置
cat /proc/net/vlan/eth0.100

# 检查父接口状态
nmcli device status

# 抓包验证 VLAN 标签
tcpdump -i eth0 -nn -e vlan
```

### 3. NetworkManager 不支持 VLAN
**解决方案**：
```bash
# 检查 NetworkManager 版本
nmcli --version

# 更新 NetworkManager
sudo yum update NetworkManager
# 或
sudo apt update && sudo apt upgrade network-manager

# 检查 VLAN 插件
nmcli connection show | grep vlan
```

### 4. VLAN 接口自动断开
**解决方案**：
```bash
# 设置自动连接
nmcli connection modify eth0.100 connection.autoconnect yes

# 设置父接口不自动配置 IP
nmcli connection modify eth0 ipv4.method disabled

# 检查 NetworkManager 配置
cat /etc/NetworkManager/NetworkManager.conf
```

## 最佳实践

### 基础 VLAN 配置示例
```yaml
- name: 创建 VLAN 100 接口
  community.general.nmcli:
    conn_name: eth0.100
    ifname: eth0.100
    type: vlan
    vlan_id: 100
    dev: eth0
    state: present
    method4: manual
    ip4: 192.168.100.10/24
    gw4: 192.168.100.1
    autoconnect: yes
```

### 多 VLAN 配置示例
```yaml
- name: 创建多个 VLAN 接口
  community.general.nmcli:
    conn_name: "{{ item.conn_name }}"
    ifname: "{{ item.ifname }}"
    type: vlan
    vlan_id: "{{ item.vlan_id }}"
    dev: "{{ item.dev }}"
    state: present
    method4: manual
    ip4: "{{ item.ip4 }}"
    gw4: "{{ item.gw4 }}"
    autoconnect: yes
  loop:
    - { conn_name: 'eth0.100', ifname: 'eth0.100', vlan_id: 100, dev: 'eth0', ip4: '192.168.100.10/24', gw4: '192.168.100.1' }
    - { conn_name: 'eth0.200', ifname: 'eth0.200', vlan_id: 200, dev: 'eth0', ip4: '192.168.200.10/24', gw4: '192.168.200.1' }
    - { conn_name: 'eth0.300', ifname: 'eth0.300', vlan_id: 300, dev: 'eth0', ip4: '192.168.300.10/24', gw4: '192.168.300.1' }
```

### 禁用父接口 IP 配置示例
```yaml
- name: 配置父接口（不分配 IP）
  community.general.nmcli:
    conn_name: eth0
    ifname: eth0
    type: ethernet
    state: present
    method4: disabled
    autoconnect: yes

- name: 创建 VLAN 子接口
  community.general.nmcli:
    conn_name: eth0.100
    ifname: eth0.100
    type: vlan
    vlan_id: 100
    dev: eth0
    state: present
    method4: manual
    ip4: 192.168.100.10/24
    autoconnect: yes
```

### DHCP 模式 VLAN 配置示例
```yaml
- name: 创建 VLAN 接口使用 DHCP
  community.general.nmcli:
    conn_name: vlan200
    ifname: eth0.200
    type: vlan
    vlan_id: 200
    dev: eth0
    state: present
    method4: auto
    autoconnect: yes
```

### VLAN 配置验证示例
```yaml
- name: 创建 VLAN 接口
  community.general.nmcli:
    conn_name: eth0.100
    ifname: eth0.100
    type: vlan
    vlan_id: 100
    dev: eth0
    state: present
    method4: manual
    ip4: 192.168.100.10/24
    autoconnect: yes
  register: vlan_config

- name: 激活 VLAN 连接
  ansible.builtin.shell: nmcli connection up eth0.100
  when: vlan_config.changed

- name: 验证 VLAN 接口状态
  ansible.builtin.shell: ip link show eth0.100
  register: vlan_status

- name: 显示 VLAN 接口信息
  ansible.builtin.debug:
    msg: "VLAN 接口 {{ 'UP' if 'state UP' in vlan_status.stdout else 'DOWN' }}"
```

### 存储网络 VLAN 配置示例
```yaml
- name: 创建存储网络 VLAN
  community.general.nmcli:
    conn_name: storage-vlan
    ifname: eth1.500
    type: vlan
    vlan_id: 500
    dev: eth1
    state: present
    method4: manual
    ip4: 10.0.500.10/24
    mtu: 9000
    autoconnect: yes
  notify: Restart storage services
```

### 管理网络 VLAN 配置示例
```yaml
- name: 创建管理网络 VLAN
  community.general.nmcli:
    conn_name: mgmt-vlan
    ifname: eth0.10
    type: vlan
    vlan_id: 10
    dev: eth0
    state: present
    method4: manual
    ip4: 172.16.10.10/24
    zone: trusted
    autoconnect: yes
```

### 删除 VLAN 配置示例
```yaml
- name: 删除 VLAN 接口
  community.general.nmcli:
    conn_name: eth0.100
    state: absent
```

### 批量 VLAN 部署示例
```yaml
- name: 批量创建服务器 VLAN 接口
  community.general.nmcli:
    conn_name: "{{ item.name }}"
    ifname: "{{ item.interface }}"
    type: vlan
    vlan_id: "{{ item.vlan_id }}"
    dev: "{{ item.parent }}"
    state: present
    method4: "{{ item.method }}"
    ip4: "{{ item.ip4 | default(omit) }}"
    gw4: "{{ item.gw4 | default(omit) }}"
    autoconnect: yes
  loop: "{{ vlan_interfaces }}"
  loop_control:
    label: "{{ item.name }}"
```

## 相关示例
- [nmcli 模块](../nmcli/README.md) - NetworkManager 网络连接管理
- [interface 模块](../interface/README.md) - 网络接口管理
- [bonding 模块](../bonding/README.md) - 网络接口绑定
- [route 模块](../route/README.md) - 静态路由管理
- [firewalld 模块](../firewalld/README.md) - 防火墙区域管理
