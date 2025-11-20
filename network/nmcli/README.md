# nmcli 模块使用指南

## 模块用途
`community.general.nmcli` 模块用于通过 NetworkManager 命令行工具管理网络连接，支持创建、修改、删除网络连接，配置 IP 地址、DNS、网关等网络参数。适用于服务器网络配置、网络接口管理、网络故障恢复等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `conn_name` | str | 连接名称（必需） | `eth0`、`wlan0`、`br0` 等 |
| `ifname` | str | 接口名称（可选） | `eth0`、`enp0s3`、`wlp2s0` 等 |
| `type` | str | 连接类型（必需） | `ethernet`、`wifi`、`bridge`、`bond`、`vlan` 等 |
| `state` | str | 连接状态（present 创建/修改，absent 删除） | present、absent |
| `autoconnect` | bool | 是否自动连接（默认 true） | true、false |
| `method4` | str | IPv4 配置方法（auto 自动，manual 手动） | auto、manual、disabled |
| `ip4` | str | IPv4 地址（manual 模式时必需） | `192.168.1.100/24` |
| `gw4` | str | IPv4 网关地址（可选） | `192.168.1.1` |
| `dns4` | list | IPv4 DNS 服务器列表（可选） | `['8.8.8.8', '8.8.4.4']` |
| `method6` | str | IPv6 配置方法（auto 自动，manual 手动） | auto、manual、disabled |
| `ip6` | str | IPv6 地址（manual 模式时必需） | `2001:db8::1/64` |
| `gw6` | str | IPv6 网关地址（可选） | `2001:db8::ffff` |
| `dns6` | list | IPv6 DNS 服务器列表（可选） | `['2001:4860:4860::8888']` |

## 高级参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `master` | str | 主接口名称（用于桥接、绑定等） | `br0`、`bond0` 等 |
| `slave_type` | str | 从接口类型（bridge、bond） | bridge、bond |
| `vlan_id` | int | VLAN ID（用于 VLAN 连接） | 100、200 等 |
| `mtu` | int | 最大传输单元（可选） | 1500、9000 等 |
| `mac` | str | MAC 地址（可选） | `00:11:22:33:44:55` |
| `zone` | str | 防火墙区域（可选） | `public`、`trusted`、`internal` 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了修改 | true/false |
| `conn_name` | 连接名称 | eth0 |
| `state` | 连接状态 | present/absent |
| `msg` | 操作结果消息 | "Connection 'eth0' successfully added" |

## 使用情境

### 服务器网络配置
- **静态 IP 配置**：为服务器配置固定 IP 地址
- **DHCP 配置**：配置自动获取 IP 地址
- **多网卡配置**：管理多个网络接口
- **网络故障恢复**：重新配置网络接口恢复连接

### 网络设备管理
- **以太网接口**：配置有线网络连接
- **无线网络**：配置 Wi-Fi 连接
- **网桥配置**：创建和管理网络桥接
- **VLAN 配置**：配置虚拟局域网

### 高级网络功能
- **网络绑定**：配置多网卡绑定提高可靠性
- **网络路由**：配置静态路由
- **DNS 配置**：设置 DNS 服务器
- **防火墙集成**：配置防火墙区域

## 安全注意事项

### 网络安全
1. **MAC 地址过滤**：配置 MAC 地址绑定提高安全性
2. **防火墙集成**：正确配置防火墙区域
3. **网络隔离**：使用 VLAN 进行网络隔离
4. **加密传输**：无线网络使用加密协议

### 配置安全
1. **备份配置**：修改网络配置前备份当前设置
2. **测试验证**：配置后测试网络连通性
3. **权限控制**：限制网络配置权限
4. **监控告警**：配置网络状态监控

### 操作安全
1. **远程操作**：修改网络配置时注意远程连接可能中断
2. **分步操作**：复杂网络配置分步骤进行
3. **回滚方案**：准备配置回滚方案
4. **维护窗口**：在维护窗口期进行网络变更

## 环境依赖

### 必需
- NetworkManager 服务
- nmcli 命令行工具
- 足够的系统权限配置网络

### 推荐
- NetworkManager-glib 包
- 网络接口驱动程序
- 系统网络服务

## 常见问题

### 1. NetworkManager 服务未运行
**解决方案**：
```bash
# 启动 NetworkManager 服务
sudo systemctl start NetworkManager
sudo systemctl enable NetworkManager

# 检查服务状态
sudo systemctl status NetworkManager
```

### 2. 网络接口不存在
**解决方案**：
```bash
# 查看可用网络接口
nmcli device status
ip link show

# 检查驱动程序
lspci | grep -i network
lsmod | grep -i network
```

### 3. IP 地址配置失败
**可能原因**：
- IP 地址冲突
- 网关不可达
- DNS 服务器不可用
- 网络接口被占用

**排查方法**：
```bash
# 检查 IP 地址冲突
arping -c 3 192.168.1.100

# 检查网关连通性
ping -c 3 192.168.1.1

# 检查 DNS 解析
nslookup example.com 8.8.8.8
```

### 4. 无线网络连接问题
**解决方案**：
```bash
# 扫描可用网络
nmcli device wifi list

# 检查无线网卡状态
nmcli radio wifi

# 启用无线网卡
nmcli radio wifi on
```

## 最佳实践

### 基础以太网配置示例
```yaml
- name: 配置以太网接口静态 IP
  community.general.nmcli:
    conn_name: eth0
    ifname: eth0
    type: ethernet
    state: present
    method4: manual
    ip4: 192.168.1.100/24
    gw4: 192.168.1.1
    dns4:
      - 8.8.8.8
      - 8.8.4.4
    autoconnect: yes
```

### DHCP 配置示例
```yaml
- name: 配置以太网接口 DHCP
  community.general.nmcli:
    conn_name: eth0
    ifname: eth0
    type: ethernet
    state: present
    method4: auto
    autoconnect: yes
```

### 多 IP 地址配置示例
```yaml
- name: 配置多个 IP 地址
  community.general.nmcli:
    conn_name: eth0-multi
    ifname: eth0
    type: ethernet
    state: present
    method4: manual
    ip4:
      - 192.168.1.100/24
      - 192.168.1.101/24
    gw4: 192.168.1.1
    dns4:
      - 8.8.8.8
```

### VLAN 配置示例
```yaml
- name: 创建 VLAN 接口
  community.general.nmcli:
    conn_name: eth0.100
    ifname: eth0.100
    type: vlan
    vlan_id: 100
    state: present
    method4: manual
    ip4: 192.168.100.10/24
    autoconnect: yes

- name: 配置 VLAN 主接口
  community.general.nmcli:
    conn_name: eth0
    ifname: eth0
    type: ethernet
    state: present
    method4: disabled
    autoconnect: yes
```

### 网桥配置示例
```yaml
- name: 创建网桥接口
  community.general.nmcli:
    conn_name: br0
    ifname: br0
    type: bridge
    state: present
    method4: manual
    ip4: 192.168.1.10/24
    autoconnect: yes

- name: 将以太网接口加入网桥
  community.general.nmcli:
    conn_name: eth0-br0
    ifname: eth0
    type: ethernet
    master: br0
    slave_type: bridge
    state: present
    autoconnect: yes
```

### 绑定配置示例
```yaml
- name: 创建绑定接口
  community.general.nmcli:
    conn_name: bond0
    ifname: bond0
    type: bond
    state: present
    method4: manual
    ip4: 192.168.1.10/24
    autoconnect: yes
    mode: balance-rr

- name: 将物理接口加入绑定
  community.general.nmcli:
    conn_name: "{{ item.conn_name }}"
    ifname: "{{ item.ifname }}"
    type: ethernet
    master: bond0
    slave_type: bond
    state: present
    autoconnect: yes
  loop:
    - { conn_name: 'eth0-bond0', ifname: 'eth0' }
    - { conn_name: 'eth1-bond0', ifname: 'eth1' }
```

### IPv6 配置示例
```yaml
- name: 配置 IPv6 静态地址
  community.general.nmcli:
    conn_name: eth0
    ifname: eth0
    type: ethernet
    state: present
    method6: manual
    ip6: 2001:db8::100/64
    gw6: 2001:db8::1
    dns6:
      - 2001:4860:4860::8888
      - 2001:4860:4860::8844
    autoconnect: yes
```

### 无线网络配置示例
```yaml
- name: 配置无线网络连接
  community.general.nmcli:
    conn_name:_wifi: MyWiFi
    ifname: wlan0
    type: wifi
    state: present
    method4: auto
    wifi:
      ssid: MyWiFiNetwork
      mode: infrastructure
      password: "{{ wifi_password }}"
    autoconnect: yes
  no_log: true
```

### 网络接口删除示例
```yaml
- name: 删除网络连接
  community.general.nmcli:
    conn_name: old-connection
    state: absent
```

### 网络配置验证示例
```yaml
- name: 配置网络接口
  community.general.nmcli:
    conn_name: eth0
    ifname: eth0
    type: ethernet
    state: present
    method4: manual
    ip4: 192.168.1.100/24
    gw4: 192.168.1.1
    dns4:
      - 8.8.8.8
    autoconnect: yes
  register: network_config

- name: 激活网络连接
  ansible.builtin.shell: nmcli connection up eth0
  when: network_config.changed

- name: 验证网络连通性
  ansible.builtin.shell: ping -c 3 8.8.8.8
  register: connectivity_test

- name: 显示连通性测试结果
  ansible.builtin.debug:
    msg: "网络连通性 {{ '正常' if connectivity_test.rc == 0 else '异常' }}"
```

### 批量网络配置示例
```yaml
- name: 批量配置服务器网络接口
  community.general.nmcli:
    conn_name: "{{ item.conn_name }}"
    ifname: "{{ item.ifname }}"
    type: "{{ item.type }}"
    state: present
    method4: "{{ item.method4 }}"
    ip4: "{{ item.ip4 | default(omit) }}"
    gw4: "{{ item.gw4 | default(omit) }}"
    dns4: "{{ item.dns4 | default(omit) }}"
    autoconnect: yes
  loop: "{{ network_interfaces }}"
  loop_control:
    label: "{{ item.conn_name }}"
```

### 网络配置备份和恢复示例
```yaml
- name: 备份当前网络配置
  ansible.builtin.shell: |
    nmcli connection show > /tmp/network_backup_$(date +%Y%m%d_%H%M%S).txt
    nmcli device status >> /tmp/network_backup_$(date +%Y%m%d_%H%M%S).txt
  register: backup_result

- name: 显示备份结果
  ansible.builtin.debug:
    msg: "网络配置已备份到: {{ backup_result.stdout_lines[0] }}"

- name: 应用网络配置（带回滚）
  community.general.nmcli:
    conn_name: "{{ network_config.conn_name }}"
    ifname: "{{ network_config.ifname }}"
    type: "{{ network_config.type }}"
    state: present
    method4: "{{ network_config.method4 }}"
    ip4: "{{ network_config.ip4 }}"
    gw4: "{{ network_config.gw4 }}"
    dns4: "{{ network_config.dns4 }}"
    autoconnect: yes
  register: config_result

- name: 如果配置失败则回滚
  ansible.builtin.fail:
    msg: "网络配置失败，请检查配置并手动回滚"
  when: config_result.failed | default(false)
```

## 相关示例
- [interface 模块](../interface/README.md) - 网络接口管理
- [route 模块](../route/README.md) - 静态路由管理
- [firewalld 模块](../firewalld/README.md) - 防火墙管理
- [systemd 模块](../../system/systemd/README.md) - 网络服务管理