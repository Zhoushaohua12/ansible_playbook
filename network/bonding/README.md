# 网络接口绑定（Bonding）模块使用指南

## 模块用途
`community.general.nmcli` 模块用于配置网络接口绑定（Network Interface Bonding），也称为链路聚合或网卡绑定。通过将多个物理网络接口聚合为一个逻辑接口，实现网络冗余、负载均衡和带宽聚合。广泛应用于服务器高可用架构、数据中心网络和关键业务系统。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `conn_name` | str | 绑定连接名称（必需） | `bond0`、`bond1` 等 |
| `ifname` | str | 绑定接口名称（可选） | `bond0`、`bond1` 等 |
| `type` | str | 连接类型（必需） | `bond` |
| `mode` | str | 绑定模式（必需） | `balance-rr`、`active-backup`、`802.3ad` 等 |
| `state` | str | 连接状态（present 创建/修改，absent 删除） | present、absent |
| `autoconnect` | bool | 是否自动连接（默认 true） | true、false |
| `method4` | str | IPv4 配置方法（auto 自动，manual 手动） | auto、manual、disabled |
| `ip4` | str | IPv4 地址（manual 模式时必需） | `192.168.1.100/24` |
| `gw4` | str | IPv4 网关地址（可选） | `192.168.1.1` |
| `dns4` | list | IPv4 DNS 服务器列表（可选） | `['8.8.8.8', '8.8.4.4']` |

## 从属接口参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `master` | str | 主接口名称（从属接口使用） | `bond0`、`bond1` 等 |
| `slave_type` | str | 从属接口类型（必需） | `bond` |
| `type` | str | 从属接口连接类型 | `ethernet` |

## 绑定模式说明

| 模式 | 说明 | 特性 | 适用场景 |
|------|------|------|----------|
| `balance-rr` (mode 0) | 轮询模式 | 负载均衡，容错 | 需要负载均衡的场景 |
| `active-backup` (mode 1) | 主备模式 | 容错，单活动接口 | 高可用场景，最常用 |
| `balance-xor` (mode 2) | XOR 模式 | 负载均衡，容错 | 基于 MAC 地址的负载均衡 |
| `broadcast` (mode 3) | 广播模式 | 容错，所有接口发送 | 特殊场景，较少使用 |
| `802.3ad` (mode 4) | LACP 模式 | 动态链路聚合，负载均衡 | 需要交换机支持 LACP |
| `balance-tlb` (mode 5) | 自适应负载均衡 | 出站负载均衡 | 不需要交换机支持 |
| `balance-alb` (mode 6) | 自适应负载均衡 | 入站和出站负载均衡 | 不需要交换机支持 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了修改 | true/false |
| `conn_name` | 绑定连接名称 | bond0 |
| `state` | 连接状态 | present/absent |
| `mode` | 绑定模式 | active-backup |
| `msg` | 操作结果消息 | "Connection 'bond0' successfully added" |

## 使用情境

### 高可用性
- **服务器冗余**：服务器网络接口冗余，单点故障自动切换
- **关键业务**：关键业务系统网络高可用保障
- **数据库服务器**：数据库服务器网络冗余
- **Web 服务器**：Web 服务器网络高可用

### 负载均衡
- **带宽聚合**：多网卡聚合带宽，提升网络吞吐量
- **流量分担**：多网卡分担网络流量
- **高性能计算**：HPC 环境网络性能优化
- **存储网络**：存储网络带宽聚合

### 数据中心
- **服务器网络**：数据中心服务器标准配置
- **虚拟化平台**：虚拟化主机网络冗余
- **容器平台**：Kubernetes/Docker 主机网络
- **云平台**：云计算平台网络架构

## 安全注意事项

### 配置安全
1. **模式选择**：根据交换机支持和需求选择合适的绑定模式
2. **交换机配置**：LACP 模式需要交换机端配置支持
3. **测试验证**：配置后测试故障切换和负载均衡功能
4. **文档记录**：记录绑定配置和网卡对应关系

### 操作安全
1. **远程操作风险**：修改绑定配置可能导致网络中断
2. **分步操作**：先创建绑定接口，再添加从属接口
3. **维护窗口**：在维护窗口期进行绑定配置变更
4. **回滚方案**：准备配置回滚方案

### 监控管理
1. **状态监控**：监控绑定接口状态和活动接口
2. **性能监控**：监控网络流量和带宽使用
3. **告警机制**：配置接口故障告警
4. **定期检查**：定期检查绑定配置和状态

## 环境依赖

### 必需
- NetworkManager 服务
- nmcli 命令行工具
- bonding 内核模块
- 多个物理网络接口

### 推荐
- NetworkManager-glib 包
- ifenslave 工具（传统绑定管理）
- 网络监控工具
- 交换机支持（LACP 模式）

### 外部依赖
- **Ansible Collection**: `community.general` (版本 >= 7.0.0)
- **系统服务**: NetworkManager 服务必须运行
- **内核模块**: bonding 内核模块必须加载
- **网络设备**: 至少两个物理网络接口

## 常见问题

### 1. bonding 模块未加载
**解决方案**：
```bash
# 检查 bonding 模块是否加载
lsmod | grep bonding

# 加载 bonding 模块
sudo modprobe bonding

# 永久加载
echo "bonding" | sudo tee -a /etc/modules

# 检查模块参数
cat /sys/class/net/bond0/bonding/mode
```

### 2. LACP 模式无法工作
**可能原因**：
- 交换机未启用 LACP
- 交换机端口配置不正确
- 网卡驱动不支持 LACP
- 接口速率不匹配

**排查方法**：
```bash
# 检查 LACP 状态
cat /proc/net/bonding/bond0

# 检查交换机配置
# (需要登录交换机)

# 检查网卡驱动
ethtool -i eth0

# 检查接口速率
ethtool eth0 | grep Speed
```

### 3. 绑定接口无法启动
**解决方案**：
```bash
# 检查从属接口状态
nmcli device status

# 检查绑定配置
nmcli connection show bond0

# 查看详细日志
journalctl -u NetworkManager -f

# 手动激活绑定
nmcli connection up bond0
```

### 4. 故障切换不工作
**解决方案**：
```bash
# 检查 miimon 参数（链路监控间隔）
cat /sys/class/net/bond0/bonding/miimon

# 检查主备状态
cat /sys/class/net/bond0/bonding/active_slave

# 模拟故障测试
sudo ip link set eth0 down
cat /sys/class/net/bond0/bonding/active_slave
sudo ip link set eth0 up
```

## 最佳实践

### 主备模式（active-backup）配置示例
```yaml
- name: 创建绑定接口 - 主备模式
  community.general.nmcli:
    conn_name: bond0
    ifname: bond0
    type: bond
    mode: active-backup
    state: present
    method4: manual
    ip4: 192.168.1.100/24
    gw4: 192.168.1.1
    dns4:
      - 8.8.8.8
      - 8.8.4.4
    autoconnect: yes

- name: 添加从属接口到绑定 - eth0
  community.general.nmcli:
    conn_name: bond0-slave-eth0
    ifname: eth0
    type: ethernet
    master: bond0
    slave_type: bond
    state: present
    autoconnect: yes

- name: 添加从属接口到绑定 - eth1
  community.general.nmcli:
    conn_name: bond0-slave-eth1
    ifname: eth1
    type: ethernet
    master: bond0
    slave_type: bond
    state: present
    autoconnect: yes
```

### LACP 模式（802.3ad）配置示例
```yaml
- name: 创建绑定接口 - LACP 模式
  community.general.nmcli:
    conn_name: bond1
    ifname: bond1
    type: bond
    mode: 802.3ad
    state: present
    method4: manual
    ip4: 10.0.0.100/24
    autoconnect: yes

- name: 批量添加从属接口
  community.general.nmcli:
    conn_name: "{{ item.conn_name }}"
    ifname: "{{ item.ifname }}"
    type: ethernet
    master: bond1
    slave_type: bond
    state: present
    autoconnect: yes
  loop:
    - { conn_name: 'bond1-slave-eth2', ifname: 'eth2' }
    - { conn_name: 'bond1-slave-eth3', ifname: 'eth3' }
```

### 负载均衡模式（balance-tlb）配置示例
```yaml
- name: 创建绑定接口 - TLB 负载均衡
  community.general.nmcli:
    conn_name: bond-tlb
    ifname: bond2
    type: bond
    mode: balance-tlb
    state: present
    method4: manual
    ip4: 172.16.0.100/24
    autoconnect: yes

- name: 添加多个从属接口
  community.general.nmcli:
    conn_name: "bond2-slave-{{ item }}"
    ifname: "{{ item }}"
    type: ethernet
    master: bond2
    slave_type: bond
    state: present
    autoconnect: yes
  loop:
    - eth4
    - eth5
    - eth6
    - eth7
```

### DHCP 模式绑定配置示例
```yaml
- name: 创建绑定接口使用 DHCP
  community.general.nmcli:
    conn_name: bond-dhcp
    ifname: bond3
    type: bond
    mode: active-backup
    state: present
    method4: auto
    autoconnect: yes

- name: 添加从属接口
  community.general.nmcli:
    conn_name: "bond3-slave-{{ item }}"
    ifname: "{{ item }}"
    type: ethernet
    master: bond3
    slave_type: bond
    state: present
    autoconnect: yes
  loop:
    - eth8
    - eth9
```

### 绑定配置验证示例
```yaml
- name: 创建并配置绑定接口
  community.general.nmcli:
    conn_name: bond0
    ifname: bond0
    type: bond
    mode: active-backup
    state: present
    method4: manual
    ip4: 192.168.1.100/24
    autoconnect: yes
  register: bond_config

- name: 激活绑定连接
  ansible.builtin.shell: nmcli connection up bond0
  when: bond_config.changed

- name: 检查绑定状态
  ansible.builtin.shell: cat /proc/net/bonding/bond0
  register: bond_status
  changed_when: false

- name: 显示绑定状态
  ansible.builtin.debug:
    msg: "{{ bond_status.stdout_lines }}"
```

### 故障切换测试示例
```yaml
- name: 测试绑定故障切换
  block:
    - name: 检查当前活动接口
      ansible.builtin.shell: cat /sys/class/net/bond0/bonding/active_slave
      register: active_before

    - name: 模拟接口故障
      ansible.builtin.shell: ip link set {{ active_before.stdout }} down
      when: test_failover | default(false) | bool

    - name: 等待故障切换
      ansible.builtin.pause:
        seconds: 5

    - name: 检查切换后活动接口
      ansible.builtin.shell: cat /sys/class/net/bond0/bonding/active_slave
      register: active_after
      when: test_failover | default(false) | bool

    - name: 显示切换结果
      ansible.builtin.debug:
        msg: "故障切换成功: {{ active_before.stdout }} -> {{ active_after.stdout }}"
      when: test_failover | default(false) | bool

    - name: 恢复接口
      ansible.builtin.shell: ip link set {{ active_before.stdout }} up
      when: test_failover | default(false) | bool
```

### 删除绑定配置示例
```yaml
- name: 删除从属接口连接
  community.general.nmcli:
    conn_name: "{{ item }}"
    state: absent
  loop:
    - bond0-slave-eth0
    - bond0-slave-eth1

- name: 删除绑定接口
  community.general.nmcli:
    conn_name: bond0
    state: absent
```

### 批量绑定部署示例
```yaml
- name: 批量创建服务器绑定接口
  community.general.nmcli:
    conn_name: "{{ item.name }}"
    ifname: "{{ item.interface }}"
    type: bond
    mode: "{{ item.mode }}"
    state: present
    method4: "{{ item.method }}"
    ip4: "{{ item.ip4 | default(omit) }}"
    gw4: "{{ item.gw4 | default(omit) }}"
    autoconnect: yes
  loop: "{{ bond_interfaces }}"
  loop_control:
    label: "{{ item.name }}"
```

## 相关示例
- [nmcli 模块](../nmcli/README.md) - NetworkManager 网络连接管理
- [interface 模块](../interface/README.md) - 网络接口管理
- [vlan 模块](../vlan/README.md) - VLAN 网络配置
- [route 模块](../route/README.md) - 静态路由管理
- [firewalld 模块](../firewalld/README.md) - 防火墙管理
