# Web Services - Web 服务器部署套件

本目录包含 Web 服务器（Nginx、Apache）的自动化部署与配置 Playbooks。

## 📋 目录结构

```
web-services/
├── nginx-install.yml          # Nginx 安装与配置
├── apache-install.yml         # Apache 安装与配置
├── ssl-certificate-setup.yml  # SSL/TLS 证书部署
├── vars/
│   └── default.yml           # 默认变量配置
├── templates/
│   ├── nginx.conf.j2         # Nginx 主配置模板
│   ├── vhost.conf.j2         # 虚拟主机配置模板
│   └── apache-vhost.conf.j2  # Apache 虚拟主机模板
├── handlers/
│   └── main.yml              # 服务重启处理程序
└── README.md                 # 本文档
```

## 🚀 快速开始

### 部署 Nginx

```bash
# 语法检查
ansible-playbook --syntax-check web-services/nginx-install.yml

# 试运行（检查模式）
ansible-playbook -i inventory/hosts web-services/nginx-install.yml --check

# 执行部署
ansible-playbook -i inventory/hosts web-services/nginx-install.yml

# 仅部署配置文件
ansible-playbook -i inventory/hosts web-services/nginx-install.yml --tags config

# 仅重载服务
ansible-playbook -i inventory/hosts web-services/nginx-install.yml --tags service
```

### 部署 Apache

```bash
ansible-playbook -i inventory/hosts web-services/apache-install.yml
```

### 配置 SSL 证书

```bash
ansible-playbook -i inventory/hosts web-services/ssl-certificate-setup.yml
```

## 📦 功能特性

- **Nginx 部署**：自动安装、配置虚拟主机、负载均衡、SSL/TLS
- **Apache 部署**：模块化配置、虚拟主机、性能优化
- **SSL/TLS 支持**：Let's Encrypt 自动化、自签名证书生成
- **安全加固**：HTTP 头部配置、版本隐藏、访问控制
- **性能优化**：Gzip 压缩、缓存配置、连接池调优

## ⚙️ 配置说明

编辑 `vars/default.yml` 或使用 `inventory/group_vars/nginx_servers.yml` 覆盖默认值：

```yaml
nginx_version: "latest"
nginx_worker_processes: "auto"
nginx_worker_connections: 2048

nginx_vhosts:
  - server_name: "example.com"
    root: "/var/www/html"
    enable_ssl: true
```

## 🏷️ 可用标签

| 标签 | 说明 |
|-----|------|
| `packages` | 安装软件包 |
| `config` | 配置文件部署 |
| `ssl` | SSL/TLS 证书配置 |
| `service` | 服务启动与重载 |
| `verify` | 验证配置与连通性 |

## 📚 相关文档

- [Nginx 官方文档](https://nginx.org/en/docs/)
- [Apache 官方文档](https://httpd.apache.org/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)

## ⚠️ 重要提示

本套件主要用于教学和学习目的。生产环境使用前请：
- 审查并调整安全配置（SSL/TLS 版本、密码套件）
- 使用 Ansible Vault 加密证书私钥
- 配置防火墙规则和访问控制
- 启用日志审计和监控集成
