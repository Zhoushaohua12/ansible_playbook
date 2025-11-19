# Nginx Web 服务器管理

## 服务简介

Nginx 是一款高性能的 HTTP 和反向代理服务器，以其高并发处理能力、低内存占用和灵活的配置著称。常用于静态内容服务、反向代理、负载均衡、API 网关等场景。本示例展示如何使用 Ansible 自动化安装、配置和管理 Nginx 服务。

核心特性：
- **事件驱动架构**：采用异步非阻塞模型，单进程可处理数万并发连接
- **模块化设计**：支持丰富的第三方模块扩展（如 Lua、RTMP）
- **反向代理**：支持 HTTP、HTTPS、WebSocket、FastCGI、uWSGI 等协议
- **负载均衡**：内置轮询、IP Hash、最少连接等多种策略
- **缓存机制**：支持静态内容缓存和反向代理缓存

## 常用 Ansible 模块

### ansible.builtin.apt / ansible.builtin.yum
**用途**：安装 Nginx 包及相关依赖

**常用参数**：
- `name`：包名称（如 `nginx`、`nginx-full`）
- `state`：期望状态（`present` 安装、`latest` 最新版、`absent` 卸载）
- `update_cache`：是否更新包缓存（apt 专用，建议设为 `yes`）

**示例**：
```yaml
- name: 安装 Nginx
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: yes
```

### ansible.builtin.template
**用途**：基于 Jinja2 模板生成 Nginx 配置文件

**常用参数**：
- `src`：模板文件路径（如 `templates/nginx.conf.j2`）
- `dest`：目标路径（如 `/etc/nginx/nginx.conf`）
- `owner`：文件所有者（建议 `root`）
- `group`：文件所属组（建议 `root`）
- `mode`：文件权限（建议 `0644`）
- `backup`：是否备份原文件（生产环境建议 `yes`）
- `validate`：配置生效前的语法检查命令（如 `nginx -t -c %s`）

**示例**：
```yaml
- name: 部署 Nginx 主配置文件
  ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: 'nginx -t -c %s'
  notify: 重载 Nginx 服务
```

### ansible.builtin.service
**用途**：管理 Nginx 服务状态（启动、停止、重启、重载）

**常用参数**：
- `name`：服务名称（通常为 `nginx`）
- `state`：期望状态（`started` 启动、`stopped` 停止、`restarted` 重启、`reloaded` 重载）
- `enabled`：是否开机自启（`yes` 或 `no`）

**示例**：
```yaml
- name: 启动 Nginx 并设置开机自启
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: yes
```

### community.general.ufw
**用途**：配置 Ubuntu/Debian 防火墙规则，开放 HTTP/HTTPS 端口

**常用参数**：
- `rule`：规则类型（`allow` 允许、`deny` 拒绝）
- `port`：端口号（如 `80`、`443`）
- `proto`：协议（`tcp` 或 `udp`）
- `from_ip`：源 IP 地址（可选，限制访问来源）

**示例**：
```yaml
- name: 开放 HTTP 和 HTTPS 端口
  community.general.ufw:
    rule: allow
    port: "{{ item }}"
    proto: tcp
  loop:
    - '80'
    - '443'
```

## 主要参数说明

### 全局配置参数
- `worker_processes`：工作进程数（建议设为 CPU 核心数或 `auto`）
- `worker_connections`：单个工作进程最大连接数（默认 1024）
- `error_log`：错误日志路径与级别（如 `/var/log/nginx/error.log warn`）
- `access_log`：访问日志路径与格式（如 `/var/log/nginx/access.log combined`）

### HTTP 配置参数
- `sendfile`：高效文件传输（建议 `on`）
- `tcp_nopush`：减少网络拥塞（建议 `on`）
- `tcp_nodelay`：禁用 Nagle 算法（建议 `on`）
- `keepalive_timeout`：长连接超时时间（秒，默认 65）
- `gzip`：是否启用 Gzip 压缩（建议 `on`）
- `gzip_types`：压缩文件类型（如 `text/css application/json`）

### 虚拟主机参数
- `listen`：监听端口与地址（如 `80`、`443 ssl http2`）
- `server_name`：服务器域名（支持通配符和正则）
- `root`：网站根目录（静态站点）
- `location`：URL 路径匹配规则
- `proxy_pass`：反向代理后端地址（如 `http://127.0.0.1:8000`）
- `proxy_set_header`：传递请求头（如 `Host $host`、`X-Real-IP $remote_addr`）

### SSL/TLS 参数
- `ssl_certificate`：SSL 证书路径
- `ssl_certificate_key`：SSL 私钥路径
- `ssl_protocols`：支持的协议版本（推荐 `TLSv1.2 TLSv1.3`）
- `ssl_ciphers`：加密套件（推荐使用 Mozilla 配置）
- `ssl_prefer_server_ciphers`：优先使用服务器加密套件（建议 `on`）

## 日志路径

### 默认日志位置
- **访问日志**：`/var/log/nginx/access.log`
  - 记录所有 HTTP 请求（客户端 IP、请求方法、URL、状态码、响应大小等）
  - 格式可通过 `log_format` 指令自定义

- **错误日志**：`/var/log/nginx/error.log`
  - 记录配置错误、连接失败、上游服务器故障等信息
  - 级别可设置为 `debug`、`info`、`notice`、`warn`、`error`、`crit`

### 虚拟主机独立日志
```nginx
server {
    listen 80;
    server_name example.com;
    
    access_log /var/log/nginx/example.com_access.log;
    error_log /var/log/nginx/example.com_error.log warn;
}
```

### 日志轮转
- 默认配置：`/etc/logrotate.d/nginx`
- 轮转频率：每日
- 保留天数：14 天（可根据磁盘空间调整）

## 常见部署场景

### 场景 1：静态网站发布
**需求**：托管 HTML/CSS/JS 静态资源

**步骤**：
1. 安装 Nginx
2. 创建网站根目录（如 `/var/www/html`）
3. 配置虚拟主机指向根目录
4. 开放防火墙 80 端口
5. 启动 Nginx 服务

**关键配置**：
```nginx
server {
    listen 80;
    server_name www.example.com;
    root /var/www/html;
    index index.html index.htm;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### 场景 2：反向代理后端应用
**需求**：将外部请求代理到内网应用服务器

**步骤**：
1. 确保后端应用已启动（如 Gunicorn 监听 127.0.0.1:8000）
2. 配置 Nginx 反向代理规则
3. 设置必要的请求头（Host、X-Real-IP、X-Forwarded-For）
4. 配置超时参数避免长连接断开

**关键配置**：
```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 场景 3：负载均衡
**需求**：分发流量到多个后端服务器

**步骤**：
1. 定义 upstream 块，列出所有后端服务器
2. 选择负载均衡策略（轮询、IP Hash、最少连接）
3. 配置健康检查（开源版需第三方模块）
4. 设置故障转移参数

**关键配置**：
```nginx
upstream backend_cluster {
    least_conn;  # 最少连接策略
    server 192.168.1.10:8000 weight=3;
    server 192.168.1.11:8000 weight=2;
    server 192.168.1.12:8000 backup;  # 备用服务器
}

server {
    listen 80;
    server_name lb.example.com;
    
    location / {
        proxy_pass http://backend_cluster;
        proxy_next_upstream error timeout http_500 http_502 http_503;
    }
}
```

### 场景 4：HTTPS 站点配置
**需求**：启用 SSL/TLS 加密传输

**步骤**：
1. 准备 SSL 证书和私钥（Let's Encrypt 或自签名）
2. 配置 443 端口监听
3. 指定证书路径
4. 设置 HTTP 到 HTTPS 自动跳转
5. 开放防火墙 443 端口

**关键配置**：
```nginx
server {
    listen 80;
    server_name secure.example.com;
    return 301 https://$host$request_uri;  # 跳转到 HTTPS
}

server {
    listen 443 ssl http2;
    server_name secure.example.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        root /var/www/secure;
        index index.html;
    }
}
```

## 如何在本地测试

### 1. 语法检查
在运行 Playbook 前，先验证语法是否正确：
```bash
ansible-playbook playbook.yml --syntax-check
```

### 2. Check 模式（Dry-Run）
预览变更内容，不实际修改系统：
```bash
ansible-playbook playbook.yml -i localhost, --connection=local --check
```

### 3. 配置文件语法验证
生成配置后，使用 Nginx 自带工具检查语法：
```bash
sudo nginx -t
```

### 4. 本地测试环境准备
```bash
# 使用 Docker 快速搭建测试环境
docker run -d --name nginx-test -p 8080:80 nginx:latest

# 或使用虚拟机
vagrant init ubuntu/focal64
vagrant up
```

### 5. 端到端验证
```bash
# 运行 Playbook
ansible-playbook playbook.yml -i hosts.ini

# 检查服务状态
systemctl status nginx

# 测试 HTTP 访问
curl -I http://localhost

# 查看日志
tail -f /var/log/nginx/access.log
```

### 6. 调试技巧
```bash
# 增加详细输出
ansible-playbook playbook.yml -vvv

# 仅运行特定标签的任务
ansible-playbook playbook.yml --tags nginx_config

# 从特定任务开始运行
ansible-playbook playbook.yml --start-at-task="部署 Nginx 主配置文件"
```

## 安全注意事项

1. **版本管理**：定期更新 Nginx 到最新稳定版，修复安全漏洞
2. **隐藏版本信息**：设置 `server_tokens off;` 避免暴露版本号
3. **限制请求大小**：设置 `client_max_body_size` 防止大文件上传攻击
4. **限流保护**：使用 `limit_req_zone` 和 `limit_conn_zone` 防止 DDoS
5. **禁用不安全方法**：限制允许的 HTTP 方法（GET、POST、HEAD）
6. **目录遍历防护**：禁用 `autoindex` 或限制访问范围
7. **SSL 配置加固**：禁用 SSLv3、TLSv1.0，启用 HSTS
8. **日志脱敏**：避免记录敏感信息（密码、Token）

## 故障排查

### 常见问题 1：Nginx 启动失败
**症状**：`systemctl start nginx` 报错

**排查步骤**：
```bash
# 查看详细错误信息
sudo nginx -t
sudo journalctl -u nginx -n 50

# 常见原因：
# - 配置文件语法错误
# - 端口已被占用（使用 netstat -tlnp | grep :80 检查）
# - 证书路径错误或权限不足
```

### 常见问题 2：502 Bad Gateway
**症状**：访问站点返回 502 错误

**排查步骤**：
```bash
# 检查后端服务是否运行
ps aux | grep gunicorn

# 检查后端端口是否监听
netstat -tlnp | grep 8000

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log

# 常见原因：
# - 后端服务未启动
# - proxy_pass 地址配置错误
# - 后端服务响应超时
```

### 常见问题 3：配置修改不生效
**症状**：修改配置文件后访问无变化

**排查步骤**：
```bash
# 重载配置（平滑重启）
sudo systemctl reload nginx

# 或强制重启
sudo systemctl restart nginx

# 检查是否有语法错误
sudo nginx -t

# 清除浏览器缓存或使用 curl 测试
curl -I http://localhost
```

## 性能优化建议

1. **工作进程调优**：`worker_processes auto;` 自动匹配 CPU 核心数
2. **连接数优化**：根据系统资源调整 `worker_connections`
3. **启用 Gzip 压缩**：减少传输数据量（注意 CPU 开销）
4. **静态资源缓存**：设置合理的 `expires` 和 `Cache-Control` 头
5. **启用 HTTP/2**：在 `listen` 指令添加 `http2` 参数
6. **反向代理缓存**：使用 `proxy_cache` 缓存后端响应
7. **禁用访问日志**：高并发场景可设置 `access_log off;`（注意影响审计）

## 相关资源

- [Nginx 官方文档](https://nginx.org/en/docs/)
- [Nginx 中文文档](https://www.nginx.cn/doc/)
- [Ansible Template 模块](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html)
- [Mozilla SSL 配置生成器](https://ssl-config.mozilla.org/)
- [Let's Encrypt 证书申请](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
