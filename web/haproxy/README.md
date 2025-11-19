# HAProxy 负载均衡配置

## 服务简介

HAProxy 是一款高性能、开源的 TCP/HTTP 负载均衡和代理解决方案。与 Nginx 相比，HAProxy 在传输层（Layer 4）和应用层（Layer 7）均提供强大的负载均衡能力，支持 SSL/TLS、WebSocket、FastCGI、TCP Socket 等多种协议。HAProxy 特别适合于构建高可用集群、进行 A/B 测试、灰度发布等复杂场景。

核心特性：
- **高性能与低延迟**：事件驱动架构，单进程可处理数万并发连接
- **多层负载均衡**：支持 TCP（L4）和 HTTP（L7）两层负载均衡
- **健康检查**：内置主动和被动健康检查机制，自动故障转移
- **会话保持**：支持 Cookie、IP Hash 等多种会话粘性方式
- **透明代理**：支持透明代理和 TPROXY 模式
- **统计与管理**：内置 Web 界面查看实时统计和管理数据
- **SSL/TLS 加密**：支持 SNI、ALPN、OCSP Stapling 等现代特性
- **灵活的路由**：ACL 匹配和 use_backend/use_server 等高级路由策略

## 常用 Ansible 模块

### ansible.builtin.apt / ansible.builtin.yum
**用途**：安装 HAProxy 包及相关依赖工具

**常用参数**：
- `name`：包名称（如 `haproxy`、`rsyslog`）
- `state`：期望状态（`present` 安装、`absent` 卸载、`latest` 最新版）
- `update_cache`：是否更新包缓存（apt 专用，建议 `yes`）

**示例**：
```yaml
- name: 安装 HAProxy（Debian/Ubuntu）
  ansible.builtin.apt:
    name: haproxy
    state: present
    update_cache: yes

- name: 安装 HAProxy（RHEL/CentOS）
  ansible.builtin.yum:
    name: haproxy
    state: present
```

### ansible.builtin.package
**用途**：跨平台包管理（自动检测包管理器）

**常用参数**：
- `name`：包名称（如 `haproxy`）
- `state`：期望状态（`present` 安装、`absent` 卸载、`latest` 最新版）

**示例**：
```yaml
- name: 安装 HAProxy（自动检测系统）
  ansible.builtin.package:
    name: haproxy
    state: present
```

### ansible.builtin.template
**用途**：基于 Jinja2 模板生成 HAProxy 配置文件

**常用参数**：
- `src`：模板文件路径（如 `templates/haproxy.cfg.j2`）
- `dest`：目标路径（通常为 `/etc/haproxy/haproxy.cfg`）
- `owner`：文件所有者（建议 `root`）
- `group`：文件所属组（建议 `root`）
- `mode`：文件权限（建议 `0644`）
- `backup`：是否备份原文件（生产环境建议 `yes`）
- `validate`：配置生效前的语法检查命令（如 `haproxy -c -f %s`）

**示例**：
```yaml
- name: 部署 HAProxy 配置文件
  ansible.builtin.template:
    src: templates/haproxy.cfg.j2
    dest: /etc/haproxy/haproxy.cfg
    owner: root
    group: root
    mode: '0644'
    backup: yes
    validate: 'haproxy -c -f %s'
  notify: 重载 HAProxy 服务
```

### ansible.builtin.service
**用途**：管理 HAProxy 服务状态（启动、停止、重启、重载）

**常用参数**：
- `name`：服务名称（通常为 `haproxy`）
- `state`：期望状态（`started` 启动、`stopped` 停止、`restarted` 重启、`reloaded` 重载）
- `enabled`：是否开机自启（`yes` 或 `no`）

**示例**：
```yaml
- name: 启动 HAProxy 并设置开机自启
  ansible.builtin.service:
    name: haproxy
    state: started
    enabled: yes
```

### ansible.builtin.uri
**用途**：检查 HAProxy 管理界面和后端服务健康状况

**常用参数**：
- `url`：检查的 URL（如管理界面 `http://localhost:8404/stats`）
- `status_code`：期望的 HTTP 状态码
- `return_content`：是否返回响应内容

**示例**：
```yaml
- name: 检查 HAProxy 管理界面
  ansible.builtin.uri:
    url: "http://localhost:8404/stats"
    status_code: 200
    return_content: yes
  register: stats_check
```

### community.general.ufw
**用途**：配置 Ubuntu/Debian 防火墙规则，开放 HAProxy 监听端口

**常用参数**：
- `rule`：规则类型（`allow` 允许、`deny` 拒绝）
- `port`：端口号（如 `80`、`443`、`8404`）
- `proto`：协议（`tcp` 或 `udp`）
- `from_ip`：源 IP 地址（可选，限制访问来源）

**示例**：
```yaml
- name: 开放 HAProxy 监听端口
  community.general.ufw:
    rule: allow
    port: "{{ item }}"
    proto: tcp
  loop:
    - '80'
    - '443'
    - '8404'  # 管理界面
```

## 主要参数说明

### 全局配置参数（global 块）
- `maxconn`：最大连接数（根据系统限制设置，通常为 4096 或更大）
- `log`：日志输出配置（如 `local0`）
- `chroot`：chroot 监狱目录（增强安全性）
- `user`：运行用户（建议 `haproxy`）
- `group`：运行用户组（建议 `haproxy`）
- `ssl-default-bind-ciphers`：SSL 加密套件
- `ssl-default-bind-options`：SSL 选项（如禁用不安全协议）

### 默认配置参数（defaults 块）
- `mode`：协议模式（`http`、`tcp`、`health`）
- `log`：是否记录日志（`global` 继承全局配置）
- `timeout connect`：连接超时时间（通常 5s）
- `timeout client`：客户端连接超时（通常 50s）
- `timeout server`：服务器连接超时（通常 50s）
- `retries`：连接失败重试次数
- `option httplog`：启用 HTTP 日志格式
- `option dontlognull`：不记录空日志

### 前端配置参数（frontend 块）
- `bind`：监听地址和端口（如 `0.0.0.0:80`、`0.0.0.0:443 ssl`）
- `mode`：前端协议模式（`http` 或 `tcp`）
- `maxconn`：前端最大连接数
- `default_backend`：默认后端服务池
- `acl`：访问控制列表，定义流量匹配规则
- `use_backend`：根据 ACL 条件选择后端服务池

### 后端配置参数（backend 块）
- `mode`：后端协议模式（通常与前端保持一致）
- `balance`：负载均衡策略（如 `roundrobin`、`leastconn`、`source` 等）
- `server`：后端服务器定义（如 `server web1 127.0.0.1:8001 check`）
- `cookie`：会话保持策略（基于 Cookie）
- `option httpchk`：HTTP 健康检查
- `http-check`：详细的 HTTP 健康检查配置

## 日志路径

### 默认日志位置
- **系统日志**：`/var/log/syslog` (Ubuntu/Debian) 或 `/var/log/messages` (RHEL/CentOS)
  - HAProxy 日志通常由 rsyslog 记录
  - 可通过配置 `/etc/rsyslog.d/` 中的规则将 HAProxy 日志重定向到独立文件

- **HAProxy 专用日志**：`/var/log/haproxy/haproxy.log` (如配置 rsyslog 重定向)
  - 记录客户端连接、后端转发、错误等信息
  - 格式遵循 `option httplog` 或 `option tcplog` 的定义

### 日志轮转
- 配置文件：`/etc/logrotate.d/haproxy`
- 轮转频率：通常每日或每周（根据流量调整）
- 保留备份：根据磁盘容量设定（建议至少 7 天）

### 管理界面日志
- HAProxy Stats 页面：`http://localhost:8404/stats`（如配置启用）
- 实时查看连接、后端状态、错误等统计信息

## 常见部署场景

### 场景 1：简单负载均衡（两个后端服务）
**需求**：将客户端请求分散到两个后端应用服务器

**步骤**：
1. 安装 HAProxy
2. 配置前端监听 80 端口
3. 定义后端服务池，包含两个服务器
4. 选择轮询（round-robin）作为负载均衡策略
5. 启动 HAProxy 服务

**关键配置**：
```yaml
frontend http_front
    bind *:80
    default_backend http_back

backend http_back
    balance roundrobin
    server app1 192.168.1.10:8000 check
    server app2 192.168.1.11:8000 check
```

### 场景 2：基于路径的请求路由
**需求**：不同 URL 路径转发到不同的后端服务

**步骤**：
1. 定义 ACL 规则，匹配不同 URL 路径
2. 使用 `use_backend` 根据 ACL 选择后端服务池
3. 为每个服务池配置对应的后端应用

**关键配置**：
```yaml
frontend http_front
    bind *:80
    acl is_api path_beg /api
    acl is_web path_beg /web
    use_backend api_back if is_api
    use_backend web_back if is_web
    default_backend web_back

backend api_back
    balance roundrobin
    server api1 192.168.1.20:3000 check
    server api2 192.168.1.21:3000 check

backend web_back
    balance roundrobin
    server web1 192.168.1.30:8000 check
    server web2 192.168.1.31:8000 check
```

### 场景 3：会话保持（粘性会话）
**需求**：同一客户端的请求始终转发到同一后端服务器

**步骤**：
1. 配置 Cookie 基会话保持
2. 在后端服务器定义中指定 Cookie 值
3. 启用 HTTP Cookie 的处理

**关键配置**：
```yaml
backend app_back
    balance roundrobin
    cookie SERVERID insert indirect nocache
    server app1 192.168.1.10:8000 cookie app1 check
    server app2 192.168.1.11:8000 cookie app2 check
```

### 场景 4：HTTPS 负载均衡与证书自动续期
**需求**：启用 HTTPS 前端，并自动管理 SSL 证书

**步骤**：
1. 准备 SSL 证书（可使用 Let's Encrypt）
2. 配置前端监听 443 端口（SSL/TLS）
3. 指定证书路径
4. 配置证书自动续期提醒（监控 cert 过期时间）

**关键配置**：
```yaml
frontend https_front
    bind *:443 ssl crt /etc/haproxy/certs/server.pem
    default_backend https_back

backend https_back
    balance roundrobin
    server app1 192.168.1.10:8000 check
    server app2 192.168.1.11:8000 check
```

## 如何在本地测试

### 1. 语法检查
在运行 Playbook 前，先验证配置文件语法是否正确：
```bash
ansible-playbook playbook.yml --syntax-check
```

### 2. Check 模式（Dry-Run）
预览变更内容，不实际修改系统：
```bash
ansible-playbook playbook.yml -i localhost, --connection=local --check
```

### 3. 配置文件语法验证
生成配置后，使用 HAProxy 自带工具检查语法：
```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg
```

### 4. 本地测试环境准备
```bash
# 使用 Docker 快速搭建测试环境
docker run -d --name haproxy-test -p 80:80 -p 8404:8404 haproxy:latest

# 或使用虚拟机
vagrant init ubuntu/focal64
vagrant up
```

### 5. 端到端验证
```bash
# 运行 Playbook
ansible-playbook playbook.yml -i hosts.ini

# 检查服务状态
systemctl status haproxy

# 测试 HTTP 访问
curl -I http://localhost

# 访问管理界面（如配置启用）
curl http://localhost:8404/stats

# 查看日志
tail -f /var/log/haproxy/haproxy.log
```

### 6. 调试技巧
```bash
# 增加详细输出
ansible-playbook playbook.yml -vvv

# 仅运行特定标签的任务
ansible-playbook playbook.yml --tags haproxy_config

# 从特定任务开始运行
ansible-playbook playbook.yml --start-at-task="部署 HAProxy 配置文件"

# 查看 HAProxy 运行状态
haproxy -f /etc/haproxy/haproxy.cfg -c
```

## SSL 证书自动化与续期提醒

### 证书获取
HAProxy 支持使用 Let's Encrypt 免费证书，可通过 Ansible 的 `community.crypto.acme_certificate` 模块自动化获取。

### 证书续期提醒
- **监控过期时间**：使用 Ansible 定时任务检查证书过期时间
- **自动续期**：部署定时任务（cron）自动调用 certbot 续期证书
- **验证更新**：证书更新后自动执行 `systemctl reload haproxy`

### 配置示例
```yaml
# 部署 Let's Encrypt 证书
- name: 请求 Let's Encrypt 证书
  community.crypto.acme_certificate:
    account_key_src: /etc/haproxy/certs/account.key
    account_email: admin@example.com
    terms_agreed: yes
    challenge: dns-01
    csr_src: /etc/haproxy/certs/server.csr
    dest: /etc/haproxy/certs/server.crt
    fullchain_dest: /etc/haproxy/certs/fullchain.pem
    state: present
  register: cert_result

# 定时续期任务
- name: 配置证书续期定时任务
  ansible.builtin.cron:
    name: "Let's Encrypt 证书续期"
    minute: "0"
    hour: "2"
    job: "certbot renew --quiet && systemctl reload haproxy"
    state: present
```

## 安全注意事项

1. **版本管理**：定期更新 HAProxy 到最新稳定版，修复安全漏洞
2. **隐藏版本信息**：在配置中避免暴露版本号（不回复 Server 头）
3. **限制连接**：使用 `maxconn` 限制最大连接数，防止资源耗尽
4. **ACL 规则安全**：仔细设计 ACL 规则，避免绕过安全策略
5. **监听地址绑定**：根据需要绑定特定 IP 地址，不要默认监听所有接口
6. **SSL/TLS 加固**：
   - 禁用 SSLv3、TLSv1.0
   - 使用强加密套件（如 ECDHE-based）
   - 启用 HSTS、OCSP Stapling
7. **日志审计**：启用详细日志，定期审查异常请求
8. **后端服务验证**：配置健康检查，及时发现故障服务器
9. **凭证管理**：使用 Ansible Vault 保护敏感信息（SSL 私钥、API 密钥）

## 故障排查

### 常见问题 1：HAProxy 启动失败
**症状**：`systemctl start haproxy` 报错

**排查步骤**：
```bash
# 检查配置文件语法
sudo haproxy -c -f /etc/haproxy/haproxy.cfg

# 查看详细错误信息
sudo journalctl -u haproxy -n 50

# 常见原因：
# - 配置文件语法错误
# - 监听端口已被占用
# - 证书路径错误或权限不足
```

### 常见问题 2：后端服务连接失败
**症状**：访问 HAProxy 时返回 503 或连接超时

**排查步骤**：
```bash
# 检查后端服务是否运行
ps aux | grep app_server

# 检查后端端口是否监听
netstat -tlnp | grep 8000

# 查看 HAProxy 日志
tail -f /var/log/haproxy/haproxy.log

# 常见原因：
# - 后端服务未启动
# - 后端地址配置错误
# - 防火墙阻止连接
# - 后端服务响应超时
```

### 常见问题 3：SSL 证书错误
**症状**：浏览器显示证书警告或连接失败

**排查步骤**：
```bash
# 检查证书文件存在性
ls -la /etc/haproxy/certs/

# 验证证书有效期
openssl x509 -in /etc/haproxy/certs/server.pem -noout -dates

# 检查证书和私钥匹配
openssl x509 -noout -modulus -in /etc/haproxy/certs/server.crt | openssl md5
openssl rsa -noout -modulus -in /etc/haproxy/certs/server.key | openssl md5

# 重载配置
sudo systemctl reload haproxy
```

## 性能优化建议

1. **连接参数调优**：
   - 根据系统 ulimit 和硬件资源调整 `maxconn`
   - 调整 `timeout client`、`timeout server` 以适应网络状况

2. **负载均衡策略优化**：
   - 对于 CPU 密集型应用使用 `leastconn`（最少连接）
   - 对于 I/O 密集型应用使用 `roundrobin`（轮询）
   - 对于需要会话保持的应用使用 `source`（基于客户端 IP）

3. **缓冲与 Keep-Alive**：
   - 启用 HTTP Keep-Alive 减少连接建立开销
   - 合理配置缓冲区大小避免内存溢出

4. **日志优化**：
   - 在高并发场景可禁用访问日志（`option dontlog`）
   - 使用 UDP 日志转发减少磁盘 I/O

5. **健康检查优化**：
   - 调整检查间隔和超时时间
   - 使用被动检查（观察连接失败）而非主动检查

## 相关资源

- [HAProxy 官方文档](http://www.haproxy.org/#docs)
- [HAProxy 配置手册](http://www.haproxy.org/#docs)
- [Let's Encrypt 证书管理](https://letsencrypt.org/getting-started/)
- [Ansible Template 模块文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html)
- [Mozilla SSL 配置生成器](https://ssl-config.mozilla.org/)
