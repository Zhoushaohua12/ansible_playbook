# wait_for 模块使用指南

## 模块用途
`ansible.builtin.wait_for` 模块用于等待特定条件满足后再继续执行后续任务。最常见的场景是等待服务端口开放，适用于集群部署、滚动更新、依赖链路中确保服务可用性等场景。相比直接检查，wait_for 提供了重试、超时、延迟等灵活控制。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `port` | int | 等待的端口号 | 80、443、3306、5432 等 |
| `host` | str | 等待的主机地址（默认 localhost） | localhost、127.0.0.1、远程 IP 等 |
| `delay` | int | 开始检查前的延迟秒数（默认 0） | 5、10、30 等 |
| `timeout` | int | 最大等待秒数（默认 300） | 60、120、300 等 |
| `connect_timeout` | int | 单次连接超时秒数 | 5、10 等 |
| `state` | str | 等待的状态 | started、stopped、present、absent 等 |
| `path` | str | 等待的文件路径 | /var/log/app.log、/tmp/ready.flag 等 |
| `search_regex` | str | 在文件/端口中搜索的正则表达式 | "ready"、"listening" 等 |
| `msg` | str | 超时时显示的错误消息 | 自定义提示文本 |
| `active_connection_states` | list | 认定为可用的连接状态 | ["ESTABLISHED"、"FIN_WAIT1"] 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `elapsed` | 等待花费的秒数 | 2.5 |
| `state` | 最终状态 | started、stopped 等 |

## 使用情境

### 等待服务启动
**场景**：安装并启动服务后，验证端口开放再执行后续配置
- 安装服务 → 启动服务 → wait_for 验证端口 → 配置应用

### 滚动更新协调
**场景**：分批次更新应用，每批次完成后验证可用性
- 更新应用 A 的第 1 批主机 → wait_for 验证启动 → 更新第 2 批

### 多服务依赖协调
**场景**：多个服务之间有依赖关系，需确保前置服务先启动
- 启动数据库 → wait_for 数据库端口 → 启动应用 → wait_for 应用端口

### 分布式系统初始化
**场景**：集群节点启动需要等待某些全局状态就绪
- 启动所有节点 → 等待主节点 → 其他节点加入集群

## 安全注意事项

1. **合理超时设置**：避免过短超时导致假失败，过长影响效率
2. **连接状态验证**：使用 `search_regex` 验证不仅端口开放，还要应用就绪
3. **错误处理**：结合 `ignore_errors` 或 `failed_when` 灵活处理失败
4. **环境差异**：不同环境启动时间可能不同，设置差异化超时
5. **日志记录**：重要等待点应记录日志便于调试

## 环境依赖

### 必需
- Ansible builtin 模块（无需额外安装）

### 推荐
- Python socket 库（通常已内置）
- 目标主机网络可达

## 部署步骤

### 1. 基础端口等待
```yaml
- name: 等待 Web 服务启动
  ansible.builtin.wait_for:
    host: "{{ inventory_hostname }}"
    port: 80
    state: started
    timeout: 30
```

### 2. 等待文件创建
```yaml
- name: 等待初始化完成（检查标记文件）
  ansible.builtin.wait_for:
    path: /tmp/app_initialized.flag
    state: present
    timeout: 60
```

### 3. 等待日志消息
```yaml
- name: 等待应用就绪消息
  ansible.builtin.wait_for:
    path: /var/log/app.log
    search_regex: "Application started successfully"
    timeout: 120
```

## 典型规则示例

### 1. 等待数据库启动
```yaml
- name: 安装 MySQL
  ansible.builtin.apt:
    name: mysql-server
    state: present
- name: 启动 MySQL
  ansible.builtin.systemd:
    name: mysql
    state: started

- name: 等待 MySQL 端口开放
  ansible.builtin.wait_for:
    host: localhost
    port: 3306
    state: started
    delay: 2
    timeout: 60
```

### 2. 滚动更新中的协调
```yaml
- name: 更新应用
  ansible.builtin.apt:
    name: myapp
    state: latest

- name: 启动应用
  ansible.builtin.systemd:
    name: myapp
    state: restarted

- name: 等待应用就绪
  ansible.builtin.wait_for:
    host: localhost
    port: 8080
    delay: 3
    timeout: 30
```

### 3. 检查远程主机服务
```yaml
- name: 等待远程主机数据库就绪
  ansible.builtin.wait_for:
    host: "{{ db_server_ip }}"
    port: 5432
    state: started
    timeout: 120
  delegate_to: localhost  # 从本地检查
```

## 故障排查

### 1. wait_for 超时
```bash
# 检查目标端口是否开放
sudo netstat -tlnp | grep :80

# 检查服务状态
sudo systemctl status nginx

# 查看服务日志
sudo journalctl -u nginx -n 50
```

### 2. 无法连接到远程主机
```bash
# 测试网络连通性
ping <remote_host>

# 检查端口是否开放
nc -zv <remote_host> <port>

# 检查防火墙规则
sudo firewall-cmd --list-all
```

### 3. 应用已启动但 wait_for 失败
使用 `search_regex` 验证应用真正就绪：
```yaml
- name: 等待应用完全就绪
  ansible.builtin.wait_for:
    path: /var/log/app.log
    search_regex: "Ready to accept requests"
    timeout: 60
```

## 相关链接
- [Ansible wait_for 官方文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html)
- [Ansible wait_for_connection 模块](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_connection_module.html)
