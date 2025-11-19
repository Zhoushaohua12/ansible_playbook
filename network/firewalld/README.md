# firewalld 模块使用指南

## 模块用途
`community.general.firewalld` 模块用于管理 RHEL/CentOS/Fedora 系统的动态防火墙。与静态 iptables 不同，firewalld 支持在线更新规则而无需重启服务，并引入了 zone（区域）的概念，可根据网络信任级别应用不同的策略。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `service` | str | 要管理的服务名称（如 http、mysql） | http、https、ftp、mysql、postgresql 等 |
| `port` | str | 要管理的端口号/协议，格式 `PORT/PROTOCOL` | 80/tcp、3306/tcp、5432/tcp 等 |
| `permanent` | bool | 规则是否永久生效（重启后保留） | true、false |
| `state` | str | 规则操作，enabled 添加，disabled 移除 | enabled、disabled |
| `zone` | str | 应用规则的区域 | public、internal、dmz、trusted、drop 等 |
| `immediate` | bool | 立即应用规则（不等待重启） | true、false |
| `source` | str | 限制规则适用的源 IP（可选） | 192.168.1.0/24、10.0.0.5 等 |
| `rich_rule` | str | 复杂的防火墙规则（支持条件判断） | family="ipv4" 开头的规则字符串 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 规则是否被修改 | true/false |
| `state` | 当前规则状态 | enabled/disabled |

## 使用情境

### 分层环境部署
**场景**：微服务应用需要不同安全等级的网络隔离
- **DMZ 区域**（对外）：开放 80/443 端口
- **Internal 区域**（对内）：开放应用服务端口（如 8080）
- **Trusted 区域**（内部管理）：允许管理工具访问

### 远程主机安全基线
**场景**：批量部署统一的安全防火墙策略
- 关闭所有不必要的端口
- 仅允许特定源 IP 访问管理端口
- 使用 zone 区分生产/开发/测试环境

### 容器化应用支持
**场景**：Kubernetes 节点或 Docker 宿主机需要管理容器网络
- 在 public zone 开放 Ingress 端口
- 在 internal zone 开放容器通信端口
- 配置 NAT 规则支持容器访问外部网络

## 安全注意事项

1. **先测试后上线**：在测试环境验证规则后再部署到生产
2. **保持管理端口畅通**：避免锁定 SSH 等管理端口（通常 22）
3. **备份当前规则**：修改前使用 `firewall-cmd --runtime-to-permanent` 保存状态
4. **使用 zone 隔离**：根据网络信任级别应用不同区域政策
5. **幂等性操作**：重复运行不应造成服务中断

## 环境依赖

### 必需
- RHEL/CentOS/Fedora 系统
- firewalld 服务运行中：`systemctl start firewalld`
- Ansible collection：`community.general`

### 可选
- firewalld 开启自启动：`systemctl enable firewalld`

## 部署步骤

### 1. 安装 firewalld
```bash
# 在目标主机上执行
sudo yum install -y firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld
```

### 2. 验证 firewalld 状态
```bash
# 在目标主机上执行
sudo firewall-cmd --state  # 应输出 running
sudo firewall-cmd --get-zones
```

### 3. 运行 Playbook
```bash
# 检查语法
ansible-playbook network/firewalld/playbook.yml --syntax-check

# Dry-Run 预览
ansible-playbook network/firewalld/playbook.yml -i hosts.ini --check

# 执行部署
ansible-playbook network/firewalld/playbook.yml -i hosts.ini
```

## 典型规则示例

### 1. 批量开放 Web 服务端口
```yaml
- name: 在 public zone 开放 HTTP/HTTPS
  community.general.firewalld:
    service: "{{ item }}"
    zone: public
    state: enabled
    permanent: true
    immediate: true
  loop:
    - http
    - https
```

### 2. 限制源 IP 访问管理端口
```yaml
- name: 仅允许管理员 IP 访问 SSH
  community.general.firewalld:
    port: 22/tcp
    zone: internal
    state: enabled
    permanent: true
    immediate: true
    source: "192.168.1.0/24"
```

### 3. 开放数据库访问
```yaml
- name: 在 internal zone 开放 MySQL
  community.general.firewalld:
    service: mysql
    zone: internal
    state: enabled
    permanent: true
    immediate: true
```

## 故障排查

### 1. firewalld 服务未运行
```bash
# 检查服务状态
sudo systemctl status firewalld

# 启动服务
sudo systemctl start firewalld
```

### 2. 规则应用后 SSH 连接断开
```bash
# 恢复规则（在主机本地执行）
sudo firewall-cmd --runtime-to-permanent
sudo systemctl reload firewalld
```

### 3. 查看当前规则
```bash
# 列出所有活跃规则
sudo firewall-cmd --list-all

# 列出特定 zone 的规则
sudo firewall-cmd --zone=public --list-all
```

## 相关链接
- [firewalld 官方文档](https://firewalld.org/)
- [Ansible community.general.firewalld](https://docs.ansible.com/ansible/latest/collections/community/general/firewalld_module.html)
- [firewall-cmd 命令参考](https://linux.die.net/man/1/firewall-cmd)
