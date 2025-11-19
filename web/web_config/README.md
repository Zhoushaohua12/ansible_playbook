# Web 通用配置管理

## 服务简介

本目录提供跨 Web 服务器（Nginx/Apache）的通用配置场景示例，涵盖反向代理、静态站点发布、SSL 证书管理等常见任务。这些示例可作为模板，根据实际使用的 Web 服务器进行调整和扩展。

核心场景：
- **反向代理**：将外部请求代理到内网应用服务器（Django、Flask、Node.js 等）
- **静态站点发布**：部署 HTML/CSS/JS 静态资源到 Web 服务器
- **SSL 证书管理**：自动化申请、部署和更新 Let's Encrypt 证书
- **负载均衡配置**：配置多后端服务器的流量分发策略
- **安全加固**：统一配置安全头、防火墙规则、访问控制

## 常用 Ansible 模块

### ansible.builtin.template
**用途**：根据 Web 服务器类型生成对应配置文件

**常用参数**：
- `src`：模板文件路径
- `dest`：目标路径（根据 Web 服务器类型动态决定）
- `validate`：配置语法检查命令

**示例**：
```yaml
- name: 部署反向代理配置
  ansible.builtin.template:
    src: "templates/proxy_{{ web_server_type }}.conf.j2"
    dest: "{{ config_dest_path }}"
    owner: root
    group: root
    mode: '0644'
    validate: "{{ validate_command }}"
  notify: 重载 Web 服务
```

### ansible.builtin.copy
**用途**：复制静态文件到 Web 根目录

**示例**：
```yaml
- name: 部署静态资源
  ansible.builtin.copy:
    src: "{{ item }}"
    dest: "{{ web_root }}/{{ item | basename }}"
    owner: www-data
    group: www-data
    mode: '0644'
  with_fileglob:
    - files/static/*
```

### ansible.builtin.service
**用途**：管理 Web 服务状态（支持 Nginx/Apache）

**示例**：
```yaml
- name: 重载 Web 服务
  ansible.builtin.service:
    name: "{{ web_service_name }}"
    state: reloaded
```

### community.general.ufw
**用途**：配置防火墙规则

**示例**：
```yaml
- name: 开放 Web 服务端口
  community.general.ufw:
    rule: allow
    port: "{{ item }}"
    proto: tcp
  loop:
    - '80'
    - '443'
```

## 主要参数说明

### 通用配置参数
- `web_server_type`：Web 服务器类型（`nginx` 或 `apache2`）
- `web_service_name`：服务名称（Nginx 为 `nginx`，Apache 为 `apache2`）
- `web_root`：Web 根目录（默认 `/var/www/html`）
- `web_user`：Web 服务运行用户（Nginx 为 `www-data`，Apache 为 `www-data` 或 `apache`）

### 反向代理参数
- `proxy_domain`：对外访问域名（如 `api.example.com`）
- `proxy_backend_host`：后端服务器地址（如 `127.0.0.1`）
- `proxy_backend_port`：后端服务器端口（如 `8000`）
- `proxy_protocol`：后端协议（`http` 或 `https`）
- `proxy_timeout`：代理超时时间（秒）
- `proxy_websocket_enabled`：是否启用 WebSocket 支持

### 静态站点参数
- `static_domain`：静态站点域名
- `static_root`：静态文件存放路径
- `static_index_files`：默认首页文件列表（如 `['index.html', 'index.htm']`）
- `static_cache_enabled`：是否启用静态资源缓存
- `static_cache_duration`：缓存有效期（如 `30d`）

### SSL/TLS 参数
- `ssl_enabled`：是否启用 HTTPS
- `ssl_certificate_path`：证书文件路径
- `ssl_certificate_key_path`：私钥文件路径
- `ssl_provider`：证书提供商（`letsencrypt`、`self-signed`、`commercial`）
- `ssl_protocols`：支持的协议版本（如 `['TLSv1.2', 'TLSv1.3']`）

## 日志路径

日志路径根据 Web 服务器类型动态确定：

### Nginx 日志
- 访问日志：`/var/log/nginx/{{ domain }}_access.log`
- 错误日志：`/var/log/nginx/{{ domain }}_error.log`

### Apache 日志
- 访问日志：`/var/log/apache2/{{ domain }}_access.log`
- 错误日志：`/var/log/apache2/{{ domain }}_error.log`

## 常见部署场景

### 场景 1：反向代理后端应用

**需求**：将外部 HTTP/HTTPS 请求代理到内网应用服务器

**步骤**：
1. 确认后端应用已启动并监听指定端口
2. 根据 Web 服务器类型选择配置模板
3. 设置必要的请求头（Host、X-Real-IP、X-Forwarded-For）
4. 配置超时参数避免长连接中断
5. 开放防火墙端口

**使用场景**：
- Django/Flask 应用通过 Gunicorn/uWSGI 提供服务
- Node.js 应用监听高端口（如 3000）需要代理到 80/443
- 微服务架构中的 API 网关
- WebSocket 实时通信应用

**关键配置（Nginx）**：
```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**关键配置（Apache）**：
```apache
ProxyPass / http://127.0.0.1:8000/
ProxyPassReverse / http://127.0.0.1:8000/
RequestHeader set X-Forwarded-Proto "http"
```

### 场景 2：静态站点发布

**需求**：托管纯静态 HTML/CSS/JS 网站

**步骤**：
1. 准备静态资源文件（HTML、CSS、JS、图片）
2. 创建 Web 根目录并设置权限
3. 复制静态文件到根目录
4. 配置虚拟主机指向根目录
5. 设置缓存策略优化性能

**使用场景**：
- 企业官网、产品介绍页
- 单页应用（SPA）如 React/Vue/Angular 构建产物
- 技术文档站点（如 MkDocs、Sphinx 生成）
- 静态博客（如 Jekyll、Hugo）

**目录结构示例**：
```
/var/www/mysite/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── app.js
└── images/
    └── logo.png
```

### 场景 3：SSL 证书自动化管理

**需求**：为站点配置 HTTPS 并自动更新证书

**步骤**：
1. 安装 Certbot（Let's Encrypt 客户端）
2. 使用 Certbot 申请证书（HTTP-01 或 DNS-01 验证）
3. 配置 Web 服务器使用证书
4. 设置 Cron 任务自动更新证书
5. 配置 HTTP 到 HTTPS 自动跳转

**Certbot 安装与使用**：
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx  # Nginx
sudo apt install certbot python3-certbot-apache  # Apache

# 申请证书（自动配置）
sudo certbot --nginx -d example.com -d www.example.com
sudo certbot --apache -d example.com -d www.example.com

# 手动申请证书
sudo certbot certonly --webroot -w /var/www/html -d example.com

# 测试自动更新
sudo certbot renew --dry-run
```

### 场景 4：负载均衡配置

**需求**：分发流量到多个后端服务器

**步骤**：
1. 定义后端服务器列表（IP + 端口）
2. 选择负载均衡策略（轮询、最少连接、IP Hash）
3. 配置健康检查机制
4. 设置故障转移备用服务器

**负载均衡策略**：
- **轮询（Round Robin）**：默认策略，依次分发请求到各后端
- **最少连接（Least Connections）**：优先分发到连接数最少的后端
- **IP Hash**：根据客户端 IP 计算哈希，保证同一客户端请求到同一后端

**Nginx 配置示例**：
```nginx
upstream backend_cluster {
    least_conn;  # 最少连接策略
    server 192.168.1.10:8000 weight=3;
    server 192.168.1.11:8000 weight=2;
    server 192.168.1.12:8000 backup;  # 备用服务器
}

server {
    listen 80;
    location / {
        proxy_pass http://backend_cluster;
    }
}
```

### 场景 5：安全加固与防护

**需求**：统一配置安全策略保护 Web 应用

**安全措施**：
1. **隐藏版本信息**：避免暴露 Web 服务器版本号
2. **配置安全响应头**：X-Frame-Options、CSP、HSTS 等
3. **限制请求大小**：防止大文件上传攻击
4. **限流保护**：防止 DDoS 和暴力破解
5. **禁止目录浏览**：避免信息泄露
6. **过滤恶意请求**：阻止 SQL 注入、XSS 等攻击

**安全响应头示例**：
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: no-referrer-when-downgrade
```

## 如何在本地测试

### 1. 语法检查
```bash
ansible-playbook playbook.yml --syntax-check
```

### 2. Check 模式（Dry-Run）
```bash
ansible-playbook playbook.yml -i localhost, --connection=local --check
```

### 3. 配置文件语法验证
根据 Web 服务器类型执行对应命令：
```bash
# Nginx
sudo nginx -t

# Apache
sudo apache2ctl configtest
```

### 4. 本地测试环境搭建
```bash
# 使用 Docker Compose 搭建完整测试环境
cat > docker-compose.yml <<EOF
version: '3'
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./www:/var/www/html:ro
  
  backend:
    image: python:3.9
    command: python -m http.server 8000
    ports:
      - "8000:8000"
EOF

docker-compose up -d
```

### 5. 端到端验证流程
```bash
# 1. 运行 Playbook
ansible-playbook playbook.yml -i hosts.ini

# 2. 检查服务状态
systemctl status nginx  # 或 apache2

# 3. 测试 HTTP 访问
curl -I http://localhost

# 4. 测试反向代理
curl http://localhost/api/endpoint

# 5. 验证 SSL 配置
openssl s_client -connect localhost:443 -servername example.com

# 6. 检查响应头
curl -I https://example.com | grep -E "X-Frame-Options|Strict-Transport"

# 7. 查看日志
tail -f /var/log/nginx/access.log
```

### 6. 性能测试
```bash
# 使用 ApacheBench 进行压力测试
ab -n 1000 -c 10 http://localhost/

# 使用 wrk 进行更详细的性能测试
wrk -t12 -c400 -d30s http://localhost/
```

## 安全注意事项

1. **凭证保护**：使用 Ansible Vault 加密 SSL 私钥和敏感配置
2. **最小权限**：Web 服务进程以非特权用户运行
3. **定期更新**：及时更新 Web 服务器软件和依赖包
4. **监控告警**：配置日志监控，及时发现异常访问
5. **备份恢复**：定期备份配置文件和 SSL 证书
6. **访问控制**：限制管理后台和敏感路径的访问来源
7. **输入验证**：在应用层验证所有用户输入
8. **HTTPS 强制**：生产环境强制使用 HTTPS 传输

## 故障排查

### 常见问题 1：反向代理 502 错误

**症状**：访问站点返回 502 Bad Gateway

**排查步骤**：
```bash
# 1. 检查后端服务是否运行
ps aux | grep gunicorn
netstat -tlnp | grep 8000

# 2. 检查防火墙是否阻止内网连接
sudo iptables -L -n

# 3. 查看 Web 服务器错误日志
tail -f /var/log/nginx/error.log

# 4. 测试后端服务可访问性
curl http://127.0.0.1:8000

# 5. 检查 SELinux 状态（RedHat 系）
getenforce
sudo setsebool -P httpd_can_network_connect 1
```

### 常见问题 2：SSL 证书错误

**症状**：浏览器提示证书无效或过期

**排查步骤**：
```bash
# 1. 检查证书文件是否存在
ls -la /etc/letsencrypt/live/example.com/

# 2. 验证证书有效期
openssl x509 -in /etc/letsencrypt/live/example.com/fullchain.pem -noout -dates

# 3. 测试证书链完整性
openssl s_client -connect example.com:443 -servername example.com

# 4. 手动更新证书
sudo certbot renew

# 5. 检查自动更新任务
sudo systemctl status certbot.timer
```

### 常见问题 3：静态资源 404

**症状**：静态文件无法访问

**排查步骤**：
```bash
# 1. 检查文件路径和权限
ls -la /var/www/html/
stat /var/www/html/index.html

# 2. 检查目录所有者
sudo chown -R www-data:www-data /var/www/html

# 3. 验证 Web 服务器配置
# Nginx: nginx -t
# Apache: apache2ctl configtest

# 4. 查看访问日志
tail -f /var/log/nginx/access.log

# 5. 测试路径映射
curl -v http://localhost/static/style.css
```

## 性能优化建议

1. **启用 Gzip 压缩**：减少传输数据量
2. **配置静态资源缓存**：设置合理的 Cache-Control 和 Expires 头
3. **启用 HTTP/2**：提升并发性能
4. **使用 CDN**：分发静态资源到边缘节点
5. **连接池优化**：调整后端连接数和超时参数
6. **日志异步写入**：减少 I/O 阻塞
7. **反向代理缓存**：缓存后端响应减少计算压力

## 相关资源

- [Nginx 反向代理文档](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Apache 反向代理文档](https://httpd.apache.org/docs/2.4/howto/reverse_proxy.html)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)
- [OWASP 安全头配置](https://owasp.org/www-project-secure-headers/)
- [Mozilla SSL 配置生成器](https://ssl-config.mozilla.org/)
