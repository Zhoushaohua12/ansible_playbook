# iptables 模块使用指南

## 模块用途
`community.general.iptables` 模块用于直接管理 Linux 内核的 iptables 防火墙规则。相比高层抽象的 firewalld/ufw，iptables 提供了对防火墙的细粒度控制，包括 NAT、DNAT、SNAT、自定义链等高级功能，适合需要复杂网络配置的场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `table` | str | 操作的 iptables 表 | filter、nat、mangle、raw、security |
| `chain` | str | 链名称 | INPUT、OUTPUT、FORWARD、PREROUTING、POSTROUTING 等 |
| `action` | str | 链级操作 | append、insert、replace、delete 等 |
| `protocol` | str | 协议 | tcp、udp、icmp、all 等 |
| `source` | str | 源 IP 地址 | 0.0.0.0/0、192.168.1.0/24 等 |
| `destination` | str | 目标 IP 地址 | 0.0.0.0/0、10.0.0.5 等 |
| `destination_port` | int/str | 目标端口 | 80、443、3306 等 |
| `match` | list | 匹配条件 | state、multiport、limit 等 |
| `ctstate` | list | 连接状态过滤 | NEW、ESTABLISHED、RELATED、INVALID |
| `jump` | str | 规则动作 | ACCEPT、DROP、REJECT、DNAT、SNAT、MASQUERADE 等 |
| `to_destination` | str | DNAT 转发目标 | 192.168.1.10:8080 等 |
| `to_source` | str | SNAT 源转换 | 192.168.1.1 等 |
| `in_interface` | str | 入站网卡 | eth0、wlan0 等 |
| `out_interface` | str | 出站网卡 | eth0、wlan0 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 规则是否被修改 | true/false |

## 使用情境

### iptables NAT 规则配置
**场景**：网络流量转发和地址转换
- **DNAT**：将外部请求转发到内部服务（如反向代理）
- **SNAT**：隐藏内部主机的真实 IP（如代理出站）
- **MASQUERADE**：IP 伪装，适合 DHCP 网络

### 自定义安全链
**场景**：复杂的安全策略需要自定义规则链
- 创建专有链处理特定协议
- 使用 stateful 防火墙追踪连接状态
- 配置限流规则防止 DDoS

### 容器网络和 overlay 支持
**场景**：Kubernetes/Docker 需要精确的网络配置
- 管理宿主机 NAT 规则支持容器通信
- 配置端口转发
- 实现网络分隔和隔离

## 安全注意事项

1. **备份和恢复**：修改前备份当前规则 `iptables-save > rules.bak`
2. **持久化规则**：使用 iptables-persistent 保存规则
3. **保持连接**：避免修改阻断 SSH 连接的规则
4. **原子性操作**：一次修改多个规则可能导致中间状态不一致
5. **性能考虑**：过多规则会影响转发性能

## 环境依赖

### 必需
- Linux 系统（任何发行版）
- iptables 工具已安装
- Ansible collection：`community.general`

### 推荐
- iptables-persistent 包（持久化规则）
- netfilter-persistent 服务（Debian/Ubuntu）

## 部署步骤

### 1. 安装 iptables
```bash
# 大多数系统已预装，如需安装：
# RHEL/CentOS
sudo yum install -y iptables

# Debian/Ubuntu
sudo apt-get install -y iptables
```

### 2. 持久化配置（可选但推荐）
```bash
# Debian/Ubuntu
sudo apt-get install -y iptables-persistent
sudo netfilter-persistent save

# RHEL/CentOS
sudo yum install -y iptables-services
sudo systemctl enable iptables
```

### 3. 运行 Playbook
```bash
# 检查语法
ansible-playbook network/iptables/playbook.yml --syntax-check

# Dry-Run 预览
ansible-playbook network/iptables/playbook.yml -i hosts.ini --check

# 执行部署（需要 root 权限）
ansible-playbook network/iptables/playbook.yml -i hosts.ini --become
```

## 典型规则示例

### 1. 基础入站规则
```yaml
- name: 允许 SSH 入站
  community.general.iptables:
    chain: INPUT
    protocol: tcp
    destination_port: 22
    ctstate:
      - NEW
      - ESTABLISHED
    jump: ACCEPT
    comment: "Allow SSH"
```

### 2. 端口转发（DNAT）
```yaml
- name: 将外部流量转发到内部服务
  community.general.iptables:
    table: nat
    chain: PREROUTING
    protocol: tcp
    destination_port: 80
    to_destination: "192.168.1.10:8080"
    jump: DNAT
    comment: "Forward HTTP to internal app"
```

### 3. 伪装（MASQUERADE）
```yaml
- name: 配置出站 IP 伪装
  community.general.iptables:
    table: nat
    chain: POSTROUTING
    out_interface: eth0
    jump: MASQUERADE
    comment: "Masquerade outgoing traffic"
```

## 故障排查

### 1. 查看当前规则
```bash
# 列出 filter 表的所有规则
sudo iptables -L -n -v

# 列出 nat 表的所有规则
sudo iptables -t nat -L -n -v

# 显示规则详细信息
sudo iptables -L -n -v --line-numbers
```

### 2. 清空所有规则
```bash
# 仅用于紧急情况
sudo iptables -F  # 清空链
sudo iptables -X  # 删除自定义链
sudo iptables -Z  # 清零计数器

# nat 表清空
sudo iptables -t nat -F
```

### 3. 恢复备份规则
```bash
# 恢复备份的规则
sudo iptables-restore < rules.bak

# 或使用 iptables-persistent（Debian/Ubuntu）
sudo cp rules.bak /etc/iptables/rules.v4
sudo netfilter-persistent reload
```

### 4. SSH 连接断开的紧急恢复
```bash
# 在主机本地（非 SSH）执行
sudo iptables -I INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

## 相关链接
- [iptables 官方文档](https://linux.die.net/man/8/iptables)
- [Ansible community.general.iptables](https://docs.ansible.com/ansible/latest/collections/community/general/iptables_module.html)
- [iptables 命令参考](https://www.digitalocean.com/community/tutorials/iptables-essentials-common-firewall-rules-and-commands)
