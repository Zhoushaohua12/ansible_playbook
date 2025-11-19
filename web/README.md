# Web 服务管理指南

本目录提供 Nginx、Apache 以及通用 Web 配置的 Ansible 自动化示例，帮助你快速完成反向代理、静态站点发布以及站点配置管理等常见任务。所有 Playbook 均包含中文注释，遵循教学最佳实践，适合在测试环境中学习与验证。

## 目录结构

- **nginx/**：Nginx Web 服务器安装、配置与管理示例
- **apache2/**：Apache HTTP Server 安装、配置与虚拟主机管理示例
- **web_config/**：通用 Web 配置场景，包含反向代理、静态站点发布等示例

## Web 服务章节说明

### Nginx 服务管理
Nginx 是一款高性能的 HTTP 服务器和反向代理服务器，广泛应用于负载均衡、静态内容服务和 API 网关等场景。本章节提供：
- Nginx 包安装（apt/yum）
- 配置文件模板部署（template 模块）
- 服务启动与重启管理（service 模块）
- 防火墙规则配置（ufw 模块）
- 日志轮转与监控集成

参考：[nginx/README.md](nginx/README.md)

### Apache2 服务管理
Apache HTTP Server 是久经考验的开源 Web 服务器，支持丰富的模块生态和虚拟主机配置。本章节提供：
- Apache2 包安装与模块启用
- 虚拟主机配置模板
- SSL/TLS 证书管理
- 服务状态监控与日志管理
- 与 PHP/Python WSGI 应用集成

参考：[apache2/README.md](apache2/README.md)

### 通用 Web 配置
涵盖跨 Web 服务器的通用配置场景，包括：
- 反向代理配置（代理后端应用服务）
- 静态站点发布（HTML/CSS/JS 资源部署）
- SSL 证书管理与自动更新
- 安全加固（禁用不安全协议、配置 HTTP 头）
- 性能优化（缓存、压缩、连接池）

参考：[web_config/README.md](web_config/README.md)

## 与 system/applications 的配合关系

本目录的 Web 服务配置通常与 `system/applications` 目录中的应用部署配合使用：

1. **分层部署**：`system/applications` 负责应用层（如 Django、Flask、Node.js）的安装与配置，`web/` 负责 Web 服务层的反向代理与静态资源服务。

2. **典型工作流**：
   - 先执行 `system/applications/` 中的 Playbook 部署应用（如启动 Gunicorn 监听 8000 端口）
   - 再执行 `web/nginx/` 或 `web/apache2/` Playbook 配置反向代理（如将 80 端口请求转发至 8000）
   - 最后使用 `web/web_config/` 中的 SSL 配置为站点启用 HTTPS

3. **变量共享**：应用端口、域名、日志路径等信息可通过 Ansible 变量在两个目录间传递，避免硬编码。

4. **Handler 联动**：应用配置变更可触发 Web 服务重载，Web 配置变更也可触发健康检查任务，确保端到端的服务可用性。

示例组合场景：
```yaml
# 场景 1: 部署 Django 应用 + Nginx 反向代理
# 1. 运行 system/applications/django/playbook.yml 启动 Gunicorn
# 2. 运行 web/nginx/playbook.yml 配置反向代理到 127.0.0.1:8000

# 场景 2: 静态网站发布 + Apache 虚拟主机
# 1. 运行 web/apache2/playbook.yml 创建虚拟主机配置
# 2. 使用 web/web_config/playbook.yml 部署静态资源到 DocumentRoot

# 场景 3: 微服务架构 + 负载均衡
# 1. 运行 system/applications/ 启动多个后端服务实例
# 2. 运行 web/nginx/playbook.yml 配置 upstream 负载均衡
```

## 常用 Ansible 模块

### 包管理模块
- `ansible.builtin.apt`：Debian/Ubuntu 系统包安装（nginx、apache2）
- `ansible.builtin.yum`：RedHat/CentOS 系统包安装
- `ansible.builtin.package`：跨发行版通用包管理（自动检测包管理器）

### 配置管理模块
- `ansible.builtin.template`：基于 Jinja2 模板生成配置文件（支持变量替换）
- `ansible.builtin.copy`：复制静态配置文件或证书
- `ansible.builtin.file`：创建目录、设置权限与所有者
- `ansible.builtin.lineinfile`：修改配置文件单行内容

### 服务管理模块
- `ansible.builtin.service`：启动、停止、重启、重载服务
- `ansible.builtin.systemd`：Systemd 特定操作（daemon-reload、enable/disable）

### 防火墙模块
- `community.general.ufw`：Ubuntu/Debian 防火墙规则管理（开放 80/443 端口）
- `ansible.posix.firewalld`：RedHat/CentOS 防火墙规则管理

### 验证模块
- `ansible.builtin.uri`：HTTP 端点健康检查（验证 Web 服务可用性）
- `ansible.builtin.wait_for`：等待端口监听或文件生成

## 参数说明

### 服务参数
- `web_service_name`：服务名称（如 `nginx`、`apache2`）
- `web_listen_port`：监听端口（默认 80/443）
- `web_server_name`：服务器域名（用于虚拟主机配置）
- `web_root_dir`：Web 根目录（静态文件路径）

### 反向代理参数
- `proxy_backend_host`：后端应用地址（如 `127.0.0.1`）
- `proxy_backend_port`：后端应用端口（如 `8000`）
- `proxy_timeout`：代理超时时间（秒）
- `proxy_buffering`：是否启用代理缓冲（on/off）

### SSL/TLS 参数
- `ssl_certificate_path`：SSL 证书路径
- `ssl_certificate_key_path`：SSL 私钥路径
- `ssl_protocols`：支持的 SSL 协议版本（如 `TLSv1.2 TLSv1.3`）
- `ssl_ciphers`：加密套件配置

## 日志路径

### Nginx 日志
- 访问日志：`/var/log/nginx/access.log`
- 错误日志：`/var/log/nginx/error.log`
- 虚拟主机日志：`/var/log/nginx/{server_name}_access.log`

### Apache 日志
- 访问日志：`/var/log/apache2/access.log` (Debian) 或 `/var/log/httpd/access_log` (RedHat)
- 错误日志：`/var/log/apache2/error.log` (Debian) 或 `/var/log/httpd/error_log` (RedHat)
- 虚拟主机日志：由 VirtualHost 配置指定

## 常见部署场景

### 场景 1：静态网站发布
1. 安装 Nginx 或 Apache
2. 配置虚拟主机指向静态文件目录
3. 开放防火墙 80 端口
4. 重载 Web 服务

### 场景 2：反向代理后端应用
1. 确保后端应用已启动并监听指定端口
2. 配置 Nginx/Apache 反向代理规则
3. 设置负载均衡策略（可选）
4. 配置健康检查与故障转移

### 场景 3：HTTPS 站点部署
1. 准备 SSL 证书（自签名或 Let's Encrypt）
2. 配置 443 端口监听与证书路径
3. 设置 HTTP 到 HTTPS 自动跳转
4. 开放防火墙 443 端口

### 场景 4：多域名虚拟主机
1. 为每个域名创建独立配置文件
2. 配置 server_name 指令（Nginx）或 ServerName 指令（Apache）
3. 分别设置 DocumentRoot 或 proxy_pass
4. 测试配置并重载服务

## 如何在本地测试

### 语法检查
在运行 Playbook 前，先进行语法检查：
```bash
ansible-playbook web/nginx/playbook.yml --syntax-check
ansible-playbook web/apache2/playbook.yml --syntax-check
ansible-playbook web/web_config/playbook.yml --syntax-check
```

### Check 模式（Dry-Run）
使用 `--check` 模式预览变更，不实际修改系统：
```bash
ansible-playbook web/nginx/playbook.yml -i localhost, --connection=local --check
```

### 本地测试环境准备
1. 使用虚拟机或容器（Docker/Podman）搭建隔离环境
2. 准备测试用域名（如添加 `/etc/hosts` 条目 `127.0.0.1 test.example.com`）
3. 备份现有 Web 服务配置（如 `/etc/nginx/nginx.conf`）
4. 运行 Playbook 并验证结果：
   ```bash
   # 安装与配置
   ansible-playbook web/nginx/playbook.yml -i hosts.ini
   
   # 验证服务状态
   systemctl status nginx
   
   # 测试 HTTP 访问
   curl -I http://localhost
   ```

### 调试技巧
- 使用 `-v`、`-vv`、`-vvv` 参数增加输出详细度
- 在 playbook 中添加 `debug` 任务输出变量值
- 检查服务日志：`journalctl -u nginx -n 50` 或 `tail -f /var/log/nginx/error.log`
- 验证配置文件语法：`nginx -t` 或 `apachectl configtest`

## 安全注意事项

1. **凭证管理**：使用 Ansible Vault 加密敏感信息（SSL 私钥、HTTP 认证密码）
2. **最小权限**：Web 服务进程应以非 root 用户运行（如 `www-data`、`nginx`）
3. **防火墙规则**：仅开放必要端口，限制源 IP 范围（生产环境）
4. **SSL 配置**：禁用 SSLv3、TLSv1.0 等不安全协议，使用强加密套件
5. **日志审计**：定期检查访问日志，监控异常请求模式
6. **配置备份**：在修改配置前备份原文件，便于回滚

## 教学声明

⚠️ **重要提示**：本目录下的所有示例主要用于教学和学习目的。在生产环境使用前，请务必：
1. 根据实际需求调整配置参数（如缓冲区大小、超时时间）
2. 进行充分的安全加固（如禁用不必要的模块、配置 WAF）
3. 在预发布环境进行压力测试，验证性能表现
4. 建立监控与告警机制，及时发现服务异常
5. 制定回滚预案，确保配置变更可快速恢复

建议先在测试环境中运行示例，理解每个任务的作用后，再根据生产需求定制化。

## 相关资源

- [Nginx 官方文档](https://nginx.org/en/docs/)
- [Apache HTTP Server 文档](https://httpd.apache.org/docs/)
- [Ansible Template 模块文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html)
- [Let's Encrypt 证书申请](https://letsencrypt.org/getting-started/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)

## 快速导航

- [Nginx 配置示例](nginx/README.md)
- [Apache2 配置示例](apache2/README.md)
- [通用 Web 配置](web_config/README.md)
- [监控集成](../monitoring/README.md)（与 Web 服务健康检查结合使用）
