# Apache2 Web 服务器管理

## 服务简介

Apache HTTP Server（通常简称 Apache）是世界上使用最广泛的开源 Web 服务器软件，具有高度模块化、跨平台、稳定可靠等特点。Apache 支持丰富的第三方模块，可轻松集成 PHP、Python、Perl 等动态语言，适合构建传统 Web 应用和内容管理系统。

核心特性：
- **模块化架构**：通过 LoadModule 指令灵活加载所需功能模块
- **虚拟主机**：支持基于 IP、端口、域名的多站点托管
- **.htaccess 支持**：允许目录级别的配置覆盖
- **多种 MPM**：支持 prefork、worker、event 等多进程/多线程模型
- **完善的认证授权**：内置 HTTP 基本认证、摘要认证、LDAP 集成

## 常用 Ansible 模块

### ansible.builtin.apt / ansible.builtin.yum
**用途**：安装 Apache2 包及常用模块

**常用参数**：
- `name`：包名称（Debian 系为 `apache2`，RedHat 系为 `httpd`）
- `state`：期望状态（`present` 安装、`latest` 最新版）
- `update_cache`：是否更新包缓存

**示例**：
```yaml
- name: 安装 Apache2 及常用模块
  ansible.builtin.apt:
    name:
      - apache2
      - apache2-utils
      - libapache2-mod-wsgi-py3  # Python WSGI 模块
    state: present
    update_cache: yes
```

### ansible.builtin.template
**用途**：生成 Apache 配置文件和虚拟主机配置

**常用参数**：
- `src`：模板文件路径（如 `templates/apache.conf.j2`）
- `dest`：目标路径（如 `/etc/apache2/sites-available/site.conf`）
- `owner`：文件所有者（建议 `root`）
- `mode`：文件权限（建议 `0644`）
- `validate`：配置生效前的语法检查（如 `apachectl -t -f %s`）

**示例**：
```yaml
- name: 部署虚拟主机配置
  ansible.builtin.template:
    src: templates/vhost.conf.j2
    dest: "/etc/apache2/sites-available/{{ apache_server_name }}.conf"
    owner: root
    group: root
    mode: '0644'
  notify: 重载 Apache 服务
```

### ansible.builtin.service
**用途**：管理 Apache 服务状态

**常用参数**：
- `name`：服务名称（Debian 系为 `apache2`，RedHat 系为 `httpd`）
- `state`：期望状态（`started`、`stopped`、`restarted`、`reloaded`）
- `enabled`：是否开机自启

**示例**：
```yaml
- name: 启动 Apache 服务并设置开机自启
  ansible.builtin.service:
    name: apache2
    state: started
    enabled: yes
```

### ansible.builtin.apache2_module
**用途**：启用或禁用 Apache 模块（Debian/Ubuntu 专用）

**常用参数**：
- `name`：模块名称（如 `rewrite`、`ssl`、`proxy`）
- `state`：期望状态（`present` 启用、`absent` 禁用）

**示例**：
```yaml
- name: 启用 Apache 常用模块
  ansible.builtin.apache2_module:
    name: "{{ item }}"
    state: present
  loop:
    - rewrite
    - ssl
    - proxy
    - proxy_http
    - headers
  notify: 重启 Apache 服务
```

### community.general.ufw
**用途**：配置防火墙规则

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
- `ServerRoot`：Apache 根目录（默认 `/etc/apache2` 或 `/etc/httpd`）
- `Listen`：监听端口和地址（如 `80`、`443`）
- `User` / `Group`：运行用户和组（如 `www-data` 或 `apache`）
- `ServerAdmin`：管理员邮箱（显示在错误页面）
- `ServerTokens`：服务器响应头信息详细度（建议 `Prod` 隐藏版本）
- `ServerSignature`：是否在页面底部显示服务器签名（建议 `Off`）

### MPM 配置参数（多进程模块）
- `StartServers`：启动时创建的子进程数
- `MinSpareServers` / `MaxSpareServers`：最小/最大空闲进程数
- `MaxRequestWorkers`：最大并发请求数
- `MaxConnectionsPerChild`：每个子进程处理的最大请求数

### 虚拟主机参数
- `ServerName`：主服务器域名
- `ServerAlias`：服务器别名（支持多个域名）
- `DocumentRoot`：网站根目录
- `DirectoryIndex`：默认首页文件（如 `index.html index.php`）
- `ErrorLog`：错误日志路径
- `CustomLog`：访问日志路径及格式

### 反向代理参数
- `ProxyPass`：反向代理规则（如 `ProxyPass / http://127.0.0.1:8000/`）
- `ProxyPassReverse`：调整响应头中的 Location 和 Content-Location
- `ProxyPreserveHost`：是否保留原始 Host 请求头（建议 `On`）
- `ProxyTimeout`：代理超时时间（秒）

### SSL/TLS 参数
- `SSLEngine`：是否启用 SSL（`on` 或 `off`）
- `SSLCertificateFile`：SSL 证书路径
- `SSLCertificateKeyFile`：SSL 私钥路径
- `SSLCertificateChainFile`：证书链文件（可选）
- `SSLProtocol`：支持的协议版本（推荐 `-all +TLSv1.2 +TLSv1.3`）
- `SSLCipherSuite`：加密套件配置

## 日志路径

### Debian/Ubuntu 系统
- **访问日志**：`/var/log/apache2/access.log`
- **错误日志**：`/var/log/apache2/error.log`
- **虚拟主机日志**：由 `CustomLog` 和 `ErrorLog` 指令指定

### RedHat/CentOS 系统
- **访问日志**：`/var/log/httpd/access_log`
- **错误日志**：`/var/log/httpd/error_log`

### 日志格式
```apache
# Combined 格式（包含 Referer 和 User-Agent）
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined

# Common 格式（基础访问信息）
LogFormat "%h %l %u %t \"%r\" %>s %b" common
```

### 日志轮转
- 默认配置：`/etc/logrotate.d/apache2` 或 `/etc/logrotate.d/httpd`
- 轮转频率：每周或每日
- 保留时间：默认 52 周

## 常见部署场景

### 场景 1：静态网站托管
**需求**：托管 HTML/CSS/JS 静态资源

**步骤**：
1. 安装 Apache2
2. 创建网站根目录并设置权限
3. 配置虚拟主机
4. 启用站点并重载配置

**关键配置**：
```apache
<VirtualHost *:80>
    ServerName www.example.com
    ServerAlias example.com
    DocumentRoot /var/www/html
    
    <Directory /var/www/html>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/example_error.log
    CustomLog ${APACHE_LOG_DIR}/example_access.log combined
</VirtualHost>
```

### 场景 2：PHP 应用部署
**需求**：运行 WordPress、Drupal 等 PHP 应用

**步骤**：
1. 安装 Apache2 和 PHP 模块（`libapache2-mod-php`）
2. 配置虚拟主机支持 PHP 文件解析
3. 设置目录权限允许 PHP 写入
4. 启用 rewrite 模块支持伪静态

**关键配置**：
```apache
<VirtualHost *:80>
    ServerName blog.example.com
    DocumentRoot /var/www/wordpress
    
    <Directory /var/www/wordpress>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    <FilesMatch \.php$>
        SetHandler application/x-httpd-php
    </FilesMatch>
    
    DirectoryIndex index.php index.html
</VirtualHost>
```

### 场景 3：反向代理配置
**需求**：代理后端 Python/Node.js 应用

**步骤**：
1. 启用 `proxy`、`proxy_http` 模块
2. 配置 ProxyPass 和 ProxyPassReverse
3. 设置必要的请求头
4. 配置超时和缓冲参数

**关键配置**：
```apache
<VirtualHost *:80>
    ServerName api.example.com
    
    ProxyPreserveHost On
    ProxyTimeout 300
    
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    <Proxy *>
        Require all granted
    </Proxy>
    
    # 传递客户端真实 IP
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "80"
</VirtualHost>
```

### 场景 4：HTTPS 站点配置
**需求**：启用 SSL/TLS 加密

**步骤**：
1. 启用 `ssl` 模块
2. 准备 SSL 证书和私钥
3. 配置 443 端口虚拟主机
4. 设置 HTTP 到 HTTPS 自动跳转

**关键配置**：
```apache
# HTTP 跳转到 HTTPS
<VirtualHost *:80>
    ServerName secure.example.com
    Redirect permanent / https://secure.example.com/
</VirtualHost>

# HTTPS 虚拟主机
<VirtualHost *:443>
    ServerName secure.example.com
    DocumentRoot /var/www/secure
    
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/cert.pem
    SSLCertificateKeyFile /etc/ssl/private/key.pem
    SSLCertificateChainFile /etc/ssl/certs/chain.pem
    
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite HIGH:!aNULL:!MD5
    SSLHonorCipherOrder on
    
    <Directory /var/www/secure>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
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

### 3. Apache 配置语法验证
```bash
# Debian/Ubuntu
sudo apache2ctl configtest

# RedHat/CentOS
sudo apachectl configtest
```

### 4. 本地测试环境
```bash
# 使用 Docker 测试环境
docker run -d --name apache-test -p 8080:80 httpd:2.4

# 或使用虚拟机
vagrant init ubuntu/focal64
vagrant up
```

### 5. 端到端验证
```bash
# 运行 Playbook
ansible-playbook playbook.yml -i hosts.ini

# 检查服务状态
systemctl status apache2

# 测试 HTTP 访问
curl -I http://localhost

# 查看已启用的模块
apache2ctl -M

# 查看虚拟主机配置
apache2ctl -S
```

### 6. 调试技巧
```bash
# 查看详细错误信息
sudo journalctl -u apache2 -n 50

# 实时监控日志
sudo tail -f /var/log/apache2/error.log

# 启用调试级别日志
# 在配置文件中设置 LogLevel debug
```

## 安全注意事项

1. **最小化安装**：仅启用必要的模块，禁用 autoindex、status 等信息泄露模块
2. **隐藏版本信息**：设置 `ServerTokens Prod` 和 `ServerSignature Off`
3. **目录权限控制**：使用 `Options -Indexes` 禁止目录浏览
4. **防止路径遍历**：限制 `FollowSymLinks` 的使用范围
5. **请求大小限制**：设置 `LimitRequestBody` 防止大文件上传攻击
6. **超时配置**：调整 `Timeout` 参数防止慢速攻击
7. **SSL 加固**：禁用弱加密协议和算法
8. **日志脱敏**：避免记录敏感信息（密码、Token）

## 故障排查

### 常见问题 1：Apache 启动失败
**症状**：`systemctl start apache2` 报错

**排查步骤**：
```bash
# 检查配置语法
sudo apache2ctl configtest

# 查看详细错误
sudo journalctl -u apache2 -n 50

# 常见原因：
# - 端口被占用（netstat -tlnp | grep :80）
# - 配置文件语法错误
# - SSL 证书路径错误或权限不足
```

### 常见问题 2：虚拟主机不生效
**症状**：访问域名返回默认页面

**排查步骤**：
```bash
# 检查站点是否已启用
ls -la /etc/apache2/sites-enabled/

# 启用站点（Debian/Ubuntu）
sudo a2ensite example.conf
sudo systemctl reload apache2

# 检查虚拟主机配置
sudo apache2ctl -S
```

### 常见问题 3：502/504 代理错误
**症状**：反向代理返回 502 或 504 错误

**排查步骤**：
```bash
# 检查后端服务是否运行
curl http://127.0.0.1:8000

# 检查 proxy 模块是否启用
sudo apache2ctl -M | grep proxy

# 查看错误日志
sudo tail -f /var/log/apache2/error.log

# 常见原因：
# - 后端服务未启动
# - ProxyPass 配置错误
# - 防火墙阻止内网连接
```

## 性能优化建议

1. **选择合适的 MPM**：高并发场景使用 event MPM
2. **启用 KeepAlive**：减少 TCP 连接开销
3. **启用压缩**：配置 `mod_deflate` 压缩文本内容
4. **静态资源缓存**：设置 `Expires` 和 `Cache-Control` 头
5. **禁用 .htaccess**：设置 `AllowOverride None` 提升性能
6. **启用操作系统缓存**：配置 `EnableSendfile On`
7. **反向代理缓存**：使用 `mod_cache` 缓存后端响应

## 相关资源

- [Apache HTTP Server 官方文档](https://httpd.apache.org/docs/2.4/)
- [Apache 中文文档](https://httpd.apache.org/docs/2.4/zh-cn/)
- [Ansible Apache2 Module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apache2_module_module.html)
- [Mozilla SSL 配置生成器](https://ssl-config.mozilla.org/)
- [Let's Encrypt 证书申请](https://certbot.eff.org/instructions?ws=apache&os=ubuntufocal)
