# ufw 模块使用指南

## 模块用途
`community.general.ufw` 模块用于管理 Ubuntu/Debian 系统的 Uncomplicated Firewall（ufw）。相比复杂的 iptables，ufw 提供了更简洁的界面和默认安全策略，非常适合快速配置基础防火墙规则。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `rule` | str | 规则操作类型 | allow、deny、reject、delete、limit |
| `direction` | str | 流量方向（可选） | in、out、incoming、outgoing |
| `from_ip` | str | 源 IP 地址（可选） | 0.0.0.0/0、192.168.1.0/24 等 |
| `from_port` | int/str | 源端口（可选） | 任意整数或服务名 |
| `to_port` | int/str | 目标端口 | 80、443、3306 等 |
| `protocol` | str | 协议类型（可选，默认 any） | tcp、udp、esp、ah、gre、igmp 等 |
| `interface` | str | 网络接口（可选） | eth0、wlan0 等 |
| `port` | int/str | 简化参数，指定端口 | 80、443、ssh 等 |
| `name` | str | 服务名称 | ssh、http、https、ftp、mysql 等 |
| `state` | str | 规则状态 | enabled、disabled、reloaded、reset |
| `logging` | str | 日志级别（可选） | low、medium、high、full |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 规则是否被修改 | true/false |
| `state` | 当前规则状态 | enabled/disabled |

## 使用情境

### 快速防火墙配置
**场景**：新系统或容器镜像需要快速启用基础防火墙
- 启用 ufw
- 配置默认 deny inbound 政策
- 开放必要的服务端口

### UFW 策略模板
**场景**：为不同角色的主机应用统一安全策略
- **Web 服务器**：允许 80、443，拒绝其他
- **应用服务器**：允许特定 IP 的应用端口
- **数据库服务器**：仅允许应用层访问

### 微服务架构支持
**场景**：容器或微服务需要受控的网络访问
- 在容器宿主机配置 ufw
- 使用源 IP 限制微服务间的通信
- 通过日志级别监控异常流量

## 安全注意事项

1. **保持 SSH 畅通**：修改规则前确保 SSH 访问不被阻止
2. **默认政策配置**：设置恰当的 `default` 政策（deny inbound）
3. **规则顺序重要**：先配置默认政策，再添加具体规则
4. **日志监控**：启用日志追踪异常连接尝试
5. **幂等性操作**：重复运行不应造成规则重复添加

## 环境依赖

### 必需
- Ubuntu/Debian 系统
- ufw 工具已安装
- Ansible collection：`community.general`

### 可选
- 启用 ufw 自启动：`systemctl enable ufw`

## 部署步骤

### 1. 安装 ufw
```bash
# 在目标主机上执行
sudo apt-get update
sudo apt-get install -y ufw
```

### 2. 初始化 ufw
```bash
# 重置规则（仅首次）
sudo ufw reset

# 启用 ufw
sudo ufw enable

# 验证状态
sudo ufw status verbose
```

### 3. 运行 Playbook
```bash
# 检查语法
ansible-playbook network/ufw/playbook.yml --syntax-check

# Dry-Run 预览
ansible-playbook network/ufw/playbook.yml -i hosts.ini --check

# 执行部署
ansible-playbook network/ufw/playbook.yml -i hosts.ini
```

## 典型规则示例

### 1. Web 服务器配置
```yaml
- name: 配置 Web 服务器防火墙
  community.general.ufw:
    rule: allow
    port: "{{ item }}"
    proto: tcp
  loop:
    - '80'
    - '443'
    - '22'  # SSH 保持畅通
```

### 2. 应用服务器配置
```yaml
- name: 允许应用端口仅从特定 IP 访问
  community.general.ufw:
    rule: allow
    from_ip: "{{ app_server_ip }}"
    to_port: '8080'
    proto: tcp
```

### 3. 拒绝规则
```yaml
- name: 拒绝特定 IP 访问
  community.general.ufw:
    rule: deny
    from_ip: "{{ blocked_ip }}"
    direction: in
```

## 故障排查

### 1. ufw 未启用
```bash
# 检查状态
sudo ufw status

# 启用 ufw
sudo ufw enable
```

### 2. SSH 连接断开
```bash
# 快速允许 SSH
sudo ufw allow ssh

# 或指定端口
sudo ufw allow 22/tcp

# 重新加载
sudo ufw reload
```

### 3. 查看所有规则
```bash
# 列出所有规则（带编号）
sudo ufw show added

# 详细状态
sudo ufw status verbose

# 删除规则
sudo ufw delete allow 80
```

### 4. 启用日志
```bash
# 设置日志级别
sudo ufw logging medium

# 查看日志
sudo tail -f /var/log/ufw.log
```

## 相关链接
- [UFW 官方文档](https://help.ubuntu.com/community/UFW)
- [Ansible community.general.ufw](https://docs.ansible.com/ansible/latest/collections/community/general/ufw_module.html)
- [ufw 命令参考](https://linux.die.net/man/8/ufw)
