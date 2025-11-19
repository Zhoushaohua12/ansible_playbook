# iptables 模块使用指南

## 模块用途
`community.general.iptables` 模块用于管理内核级防火墙规则，支持 IPv4 和 IPv6，广泛应用于传统 Linux 系统、容器宿主机、NAT 网关等场景。相比 firewalld 的高层抽象，iptables 提供更低层且灵活的规则控制。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `chain` | str | 规则链（INPUT/OUTPUT/FORWARD/自定义） | INPUT、OUTPUT、FORWARD、DOCKER 等 |
| `protocol` | str | 协议（tcp、udp、icmp、all） | tcp、udp、icmp、all |
| `source` | str | 源 IP 或网络（CIDR 格式） | 192.168.1.0/24、10.0.0.5、0.0.0.0/0 |
| `destination` | str | 目标 IP 或网络（CIDR 格式） | 192.168.1.100、224.0.0.0/8 等 |
| `match` | str | 匹配条件（state、limit、multiport 等） | state、limit、multiport 等 |
| `ctstate` | str | 连接状态（NEW、ESTABLISHED、RELATED） | NEW、ESTABLISHED、RELATED、INVALID |
| `destination_port` | str/int | 目标端口或端口范围 | 80、443、1024:65535 等 |
| `source_port` | str/int | 源端口或端口范围 | 1024:65535、53 等 |
| `jump` | str | 规则动作（ACCEPT、DROP、REJECT、REDIRECT 等） | ACCEPT、DROP、REJECT、REDIRECT、DNAT 等 |
| `in_interface` | str | 输入网络接口 | eth0、wlan0、docker0 等 |
| `out_interface` | str | 输出网络接口 | eth0、tun0、docker0 等 |
| `table` | str | 规则表（filter、nat、mangle、raw） | filter、nat、mangle、raw |
| `action` | str | 规则操作（append 追加，insert 插入，replace 替换，remove 删除） | append、insert、replace、remove |
| `state` | str | 规则状态（present 存在，absent 删除） | present、absent |
| `comment` | str | 规则注释（用于识别规则） | "Allow SSH"、"Drop spam" 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 规则是否被修改 | true/false |

## 使用情境

### 基本防火墙过滤
**场景**：设置 INPUT、OUTPUT、FORWARD 链的默认策略
- 设置默认 DROP，仅允许特定端口入站
- 限制特定源 IP 访问管理端口
- 防止 IP 扫描和 DDoS 攻击

### NAT 与端口转发
**场景**：实现端口转发、内外网隔离
- 将外网 80 端口转发到内网 8080
- 源 NAT (SNAT)：内网主机通过网关访问外网
- 目标 NAT (DNAT)：将特定流量转发到特定主机

### 容器与虚拟网络
**场景**：Docker 宿主机、Kubernetes 节点的网络隔离
- 配置 Docker 0 网桥的防火墙规则
- 管理容器间通信
- 实现容器到主机的网络隔离

### 高级流量控制
**场景**：QoS、限流、连接追踪
- 使用 limit 限制连接速率
- 使用 state 追踪连接状态
- 防止 SYN flood 攻击

## 安全注意事项

1. **谨慎使用 DROP**：确保不会锁定 SSH 等管理端口
2. **规则顺序很重要**：iptables 按顺序匹配规则，第一个匹配的规则生效
3. **state 追踪**：使用 `ctstate: NEW,ESTABLISHED,RELATED` 追踪连接状态
4. **备份与恢复**：修改前备份当前规则，支持快速回滚
5. **持久化**：iptables 规则在重启后丢失，需配置持久化
6. **性能影响**：复杂规则会影响网络性能

## 环境依赖

### 必需
- 目标系统必须安装 iptables/iptables-services
- community.general collection
- 执行操作需要 root 或 sudo 权限

### 推荐
- iptables-persistent 或 ufw 用于规则持久化
- 了解 OSI 模型与 TCP/IP 协议栈
- 准备回滚脚本

## 常见问题

### 1. 如何查看当前规则？
```bash
# 查看 filter 表
iptables -L -n -v

# 查看所有表
iptables -L -n -v -t filter
iptables -L -n -v -t nat
iptables -L -n -v -t mangle
```

### 2. 规则不生效或重启后丢失？
iptables 规则需要持久化：
```bash
# 保存规则
iptables-save > /etc/iptables/rules.v4

# 恢复规则
iptables-restore < /etc/iptables/rules.v4
```

### 3. 如何安全地测试规则而不锁定自己？
```yaml
- name: 在特定时间后自动清除规则（防止锁定）
  block:
    - name: 添加测试规则
      community.general.iptables:
        chain: INPUT
        jump: DROP
        # ...
    
    - name: 等待确认（30秒超时）
      ansible.builtin.wait_for:
        timeout: 30
        msg: "规则测试完成"
```

### 4. 如何删除已添加的规则？
使用 `action: remove` 或 `state: absent`：
```yaml
- name: 删除规则
  community.general.iptables:
    chain: INPUT
    protocol: tcp
    destination_port: 22
    jump: ACCEPT
    action: remove  # 或 state: absent
```

## 最佳实践

### 基础防火墙配置
```yaml
- name: 设置基础防火墙规则
  block:
    # 允许已建立的连接
    - name: 允许已建立连接
      community.general.iptables:
        chain: INPUT
        protocol: all
        match: state
        ctstate: ESTABLISHED,RELATED
        jump: ACCEPT
    
    # 允许本机访问
    - name: 允许 loopback 接口
      community.general.iptables:
        chain: INPUT
        in_interface: lo
        jump: ACCEPT
    
    # 允许 SSH
    - name: 允许 SSH 访问
      community.general.iptables:
        chain: INPUT
        protocol: tcp
        destination_port: 22
        jump: ACCEPT
    
    # 允许 Web 服务
    - name: 允许 HTTP/HTTPS
      community.general.iptables:
        chain: INPUT
        protocol: tcp
        destination_port: "{{ item }}"
        jump: ACCEPT
      loop:
        - 80
        - 443
```

### NAT 与端口转发
```yaml
- name: 配置 NAT 规则
  block:
    # 启用 IP 转发
    - name: 启用 IP 转发
      ansible.builtin.sysctl:
        name: net.ipv4.ip_forward
        value: '1'
        sysctl_set: yes
    
    # 配置 DNAT（端口转发）
    - name: 将 80 端口转发到内网主机
      community.general.iptables:
        table: nat
        chain: PREROUTING
        protocol: tcp
        destination_port: 80
        jump: DNAT
        to_destination: "192.168.1.100:8080"
    
    # 配置 SNAT（源 NAT）
    - name: 内网主机通过网关访问外网
      community.general.iptables:
        table: nat
        chain: POSTROUTING
        out_interface: eth0
        source: 192.168.1.0/24
        jump: SNAT
        to_source: 203.0.113.10
```

### 防止 DDoS 攻击
```yaml
- name: 配置 DDoS 防护规则
  community.general.iptables:
    chain: INPUT
    protocol: tcp
    destination_port: 80
    match: limit
    limit: "100/minute"
    jump: ACCEPT
    comment: "限制 HTTP 连接速率"
```

## 与其他模块的协同

- **firewalld 模块**：高层防火墙管理（互斥）
- **service 模块**：启动 iptables 服务
- **sysctl 模块**：启用 IP 转发等内核参数

## 相关文档
- [network/iptables 详细指南](../../network/iptables/README.md)
- [firewalld 防火墙管理](../firewalld/README.md)
- [service 模块](../service/README.md)
