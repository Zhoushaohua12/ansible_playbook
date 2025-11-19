# firewalld 模块使用指南

## 模块用途
`community.general.firewalld` 模块用于在 RHEL/CentOS/Fedora 系统上管理动态防火墙规则。支持 zone（区域）概念、service（服务）、port（端口）、rich rule（复杂规则）等多种管理方式，可在线更新规则无需重启防火墙服务。

本指南重点从系统管理角度阐述 firewalld 的部署与配置，详见 [network/firewalld](../../network/firewalld/README.md) 了解更多网络层面的设计。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `service` | str | 服务名称（预定义的服务集合） | http、https、ftp、mysql、postgresql 等 |
| `port` | str | 端口号与协议，格式 `PORT/PROTOCOL` | 80/tcp、443/tcp、3306/tcp 等 |
| `zone` | str | 应用规则的区域（信任级别） | public、internal、dmz、trusted、drop 等 |
| `state` | str | 规则操作（enabled 添加，disabled 移除） | enabled、disabled |
| `permanent` | bool | 规则是否永久生效（重启后保留） | true、false |
| `immediate` | bool | 立即应用规则（不等待重启） | true、false |
| `source` | str | 限制规则适用的源 IP 或网络 | 192.168.1.0/24、10.0.0.5 等 |
| `rich_rule` | str | 复杂防火墙规则字符串 | family="ipv4" rule="..." |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 规则是否被修改 | true/false |
| `state` | 规则当前状态 | enabled/disabled |

## 使用情境

### 系统基线防火墙配置
**场景**：部署新服务器时的标准化防火墙配置
- 配置 public zone 开放必要的服务端口
- 配置 internal zone 用于内部通信
- 配置 dmz zone 用于边界隔离

### 应用隔离与微分段
**场景**：为不同应用创建独立的防火墙规则
- 数据库服务仅对特定应用主机开放
- 缓存服务仅对内网开放
- 管理接口限制源 IP 访问

### 容器化与 Kubernetes 支持
**场景**：容器宿主机的防火墙配置
- 开放 Ingress 控制器端口
- 配置容器间通信
- NAT 和端口转发规则

## 安全注意事项

1. **规则校验**：
   - 确保不会锁定 SSH 等管理端口
   - 在测试环境验证规则后再上线
2. **Zone 隔离**：根据网络信任级别正确配置 zone
3. **permanent 与 immediate**：
   - permanent: true 重启后生效
   - immediate: true 立即生效
   - 通常两个都设置为 true
4. **备份与恢复**：
   - 修改前备份当前规则：`firewall-cmd --runtime-to-permanent`
   - 配置文件位于 `/etc/firewalld/zones/`
5. **审计日志**：启用 firewalld 日志记录关键操作

## 环境依赖

### 必需
- RHEL/CentOS/Fedora 系统
- firewalld 服务：`systemctl start firewalld`
- community.general collection

### 推荐
- firewalld 开启自启动：`systemctl enable firewalld`
- 配置 SELinux 规则支持 firewalld

## 常见问题

### 1. 如何查看当前防火墙规则？
```bash
# 查看所有 zone 的规则
firewall-cmd --list-all-zones

# 查看特定 zone 的规则
firewall-cmd --zone=public --list-all
```

### 2. permanent 与 immediate 的区别？
- `permanent: true` 修改持久配置，重启后生效
- `immediate: true` 立即应用到运行时
- 通常两个都设置为 true 以确保规则立即生效且持久保存

### 3. 如何限制 SSH 访问？
```yaml
- name: 限制 SSH 访问
  community.general.firewalld:
    port: 22/tcp
    zone: internal
    state: enabled
    permanent: true
    immediate: true
    source: 192.168.1.0/24
```

### 4. rich rule 如何使用？
complex rules 支持更细粒度的控制：
```yaml
- name: 复杂规则示例
  community.general.firewalld:
    rich_rule: 'family="ipv4" source address="192.168.1.0/24" service name="http" accept'
    zone: internal
    state: enabled
    permanent: true
    immediate: true
```

## 最佳实践

### 标准化部署流程
```yaml
- name: 配置防火墙基线
  block:
    - name: 启动 firewalld
      ansible.builtin.systemd:
        name: firewalld
        state: started
        enabled: true
    
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
    
    - name: 在 internal zone 开放应用端口
      community.general.firewalld:
        port: "{{ app_port }}/tcp"
        zone: internal
        state: enabled
        permanent: true
        immediate: true
```

### 应用特定的规则示例
```yaml
- name: 为数据库配置防火墙
  community.general.firewalld:
    port: 3306/tcp
    zone: internal
    source: "{{ app_server_ip }}"
    state: enabled
    permanent: true
    immediate: true
```

### 批量管理多个服务
```yaml
- name: 配置 Web 服务防火墙
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

## 与其他系统模块的协同

- **service/systemd 模块**：启动 firewalld 服务
- **user/group 模块**：配置 firewalld 管理员权限
- **iptables 模块**：高级防火墙规则管理

## 相关文档
- [Network firewalld 详细指南](../../network/firewalld/README.md)
- [iptables 防火墙与 NAT 规则](../iptables/README.md)
- [service 模块](../service/README.md)
