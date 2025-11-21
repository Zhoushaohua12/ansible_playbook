# 应用部署 Ansible Playbooks

本目录包含用于部署各种应用程序的 Ansible playbooks，涵盖 Docker、LAMP 栈、LNMP 栈和 Node.js 应用的自动化部署。

## 📋 目录结构

```
application-deploy/
├── docker-install.yml          # Docker 引擎与 Compose 安装
├── lamp-stack-deploy.yml        # LAMP 栈（Apache/PHP/MySQL）部署
├── lnmp-stack-deploy.yml        # LNMP 栈（Nginx/PHP-FPM/MySQL）部署
├── nodejs-app-deploy.yml        # Node.js 应用服务部署
├── vars/
│   └── default.yml              # 默认变量配置
├── templates/
│   ├── daemon.json.j2          # Docker 守护进程配置
│   ├── php.ini.j2              # PHP 配置文件
│   ├── apache-vhost.conf.j2    # Apache 虚拟主机配置
│   ├── db-test.php.j2          # 数据库连接测试页面
│   ├── php-fpm.ini.j2          # PHP-FPM 配置文件
│   ├── php-fpm-pool.conf.j2    # PHP-FPM 池配置
│   ├── nginx-lnmp.conf.j2      # Nginx 主配置文件
│   ├── nginx-lnmp-vhost.conf.j2 # Nginx 虚拟主机配置
│   ├── lnmp-db-test.php.j2     # LNMP 数据库测试页面
│   ├── ecosystem.config.js.j2  # PM2 配置文件
│   └── nodejs.service.j2       # Node.js systemd 服务文件
└── README.md                   # 本文档
```

## 🚀 快速开始

### 1. Docker 引擎安装

```bash
# 语法检查
ansible-playbook --syntax-check docker-install.yml

# 干运行（检查模式）
ansible-playbook --check docker-install.yml

# 执行安装
ansible-playbook docker-install.yml

# 仅安装软件包
ansible-playbook docker-install.yml --tags "packages"

# 仅配置 Docker
ansible-playbook docker-install.yml --tags "config"
```

**功能特性：**
- 安装 Docker 引擎和 Docker Compose
- 配置镜像仓库加速器
- 优化 Docker 守护进程配置
- 支持用户权限管理
- 包含测试容器验证
- 防火墙规则配置

### 2. LAMP 栈部署

```bash
# 语法检查
ansible-playbook --syntax-check lamp-stack-deploy.yml

# 干运行
ansible-playbook --check lamp-stack-deploy.yml

# 执行部署
ansible-playbook lamp-stack-deploy.yml

# 仅安装软件包
ansible-playbook lamp-stack-deploy.yml --tags "packages"

# 仅配置数据库
ansible-playbook lamp-stack-deploy.yml --tags "mysql"

# 仅配置 Web 服务器
ansible-playbook lamp-stack-deploy.yml --tags "apache"
```

**功能特性：**
- Apache Web 服务器配置
- PHP 8.1 + 常用扩展模块
- MySQL 数据库安装与安全配置
- 虚拟主机配置与 SSL 支持
- 数据库用户与权限管理
- 性能优化和安全加固
- 测试页面部署

### 3. LNMP 栈部署

```bash
# 语法检查
ansible-playbook --syntax-check lnmp-stack-deploy.yml

# 干运行
ansible-playbook --check lnmp-stack-deploy.yml

# 执行部署
ansible-playbook lnmp-stack-deploy.yml

# 仅安装软件包
ansible-playbook lnmp-stack-deploy.yml --tags "packages"

# 仅配置 PHP-FPM
ansible-playbook lnmp-stack-deploy.yml --tags "php"

# 仅配置 Nginx
ansible-playbook lnmp-stack-deploy.yml --tags "nginx"
```

**功能特性：**
- Nginx 高性能 Web 服务器
- PHP-FPM 进程管理优化
- MySQL 数据库集成
- 动态内容处理优化
- 静态文件缓存配置
- 安全头部和访问控制
- 性能监控端点

### 4. Node.js 应用部署

```bash
# 语法检查
ansible-playbook --syntax-check nodejs-app-deploy.yml

# 干运行
ansible-playbook --check nodejs-app-deploy.yml

# 执行部署
ansible-playbook nodejs-app-deploy.yml

# 使用 PM2 进程管理
ansible-playbook nodejs-app-deploy.yml -e "nodejs_use_pm2=true"

# 使用 systemd 服务
ansible-playbook nodejs-app-deploy.yml -e "nodejs_use_pm2=false"

# 从 Git 仓库部署
ansible-playbook nodejs-app-deploy.yml -e "nodejs_git_repo=https://github.com/user/repo.git"
```

**功能特性：**
- Node.js 18.x 安装与配置
- 支持 Git 仓库代码部署
- PM2 进程管理器集成
- systemd 服务管理
- 应用健康检查
- 优雅关闭处理
- 性能监控端点

## ⚙️ 配置说明

### 主要变量配置

编辑 `vars/default.yml` 文件来自定义部署参数：

```yaml
# Docker 配置
docker_enabled: true
docker_registry_mirror: "https://registry.docker-cn.com"

# LAMP 栈配置
lamp_mysql_root_password: "secure_password_change_me"
lamp_php_version: "8.1"

# LNMP 栈配置
lnmp_mysql_root_password: "secure_password_change_me"
lnmp_php_version: "8.1"

# Node.js 配置
nodejs_version: "18"
nodejs_use_pm2: true
nodejs_app_port: "3000"
```

### 安全配置

- 所有数据库密码使用 `no_log: true` 保护
- 支持 Vault 加密敏感变量
- 防火墙规则自动配置
- SSL/TLS 证书路径预留
- 访问控制和权限管理

## 🖥️ 操作系统支持

| 操作系统 | 版本 | 支持状态 |
|---------|------|----------|
| Ubuntu | 20.04 LTS | ✅ 完全支持 |
| Ubuntu | 22.04 LTS | ✅ 完全支持 |
| Debian | 10 (Buster) | ✅ 完全支持 |
| Debian | 11 (Bullseye) | ✅ 完全支持 |
| CentOS | 7 | ⚠️ 部分支持 |
| CentOS | 8 | ⚠️ 部分支持 |

## 📦 依赖要求

### Ansible 要求
- Ansible >= 2.9
- Python >= 3.6

### Ansible Collections
```bash
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.mysql
ansible-galaxy collection install community.general
```

### 系统要求
- 最小内存：2GB RAM
- 磁盘空间：20GB 可用空间
- 网络：互联网连接（用于软件包下载）

## 🏷️ 标签使用

所有 playbooks 都支持标签进行选择性执行：

| 标签 | 描述 |
|------|------|
| `packages` | 软件包安装 |
| `config` | 配置文件部署 |
| `service` | 服务管理 |
| `verify` | 验证和测试 |
| `firewall` | 防火墙配置 |
| `security` | 安全加固 |
| `database` | 数据库配置 |
| `web` | Web 服务器配置 |
| `php` | PHP 相关配置 |
| `nginx` | Nginx 配置 |
| `apache` | Apache 配置 |
| `mysql` | MySQL 配置 |
| `nodejs` | Node.js 配置 |
| `pm2` | PM2 进程管理 |
| `systemd` | systemd 服务管理 |
| `info` | 信息输出 |

## 🔧 故障排除

### 常见问题

1. **Docker 安装失败**
   ```bash
   # 检查系统版本
   lsb_release -a
   
   # 手动添加仓库
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   ```

2. **PHP 版本不兼容**
   ```bash
   # 检查可用 PHP 版本
   apt-cache search php | grep "php[0-9]"
   
   # 修改 vars/default.yml 中的 PHP 版本
   ```

3. **数据库连接失败**
   ```bash
   # 检查 MySQL 服务状态
   systemctl status mysql
   
   # 检查端口监听
   netstat -tlnp | grep 3306
   ```

4. **Node.js 应用无法启动**
   ```bash
   # 检查应用日志
   journalctl -u {{ nodejs_app_name }}
   
   # 或使用 PM2 日志
   pm2 logs {{ nodejs_pm2_app_name }}
   ```

### 调试技巧

```bash
# 详细输出模式
ansible-playbook docker-install.yml -vvv

# 仅在特定主机执行
ansible-playbook lamp-stack-deploy.yml --limit web01.example.com

# 跳过错误继续执行
ansible-playbook lnmp-stack-deploy.yml --skip-tags "verify"

# 使用自定义变量文件
ansible-playbook nodejs-app-deploy.yml -e @custom_vars.yml
```

## 📚 最佳实践

1. **生产环境部署前**
   - 在测试环境完整验证
   - 备份现有数据
   - 检查系统资源
   - 审查安全配置

2. **密码管理**
   - 使用 Ansible Vault 加密敏感信息
   - 定期更换数据库密码
   - 避免在版本控制中提交密码

3. **性能优化**
   - 根据服务器规格调整进程数
   - 配置适当的缓存策略
   - 启用压缩和静态文件缓存

4. **监控和维护**
   - 配置日志轮转
   - 设置监控告警
   - 定期更新软件包

## 📞 支持与反馈

如果遇到问题或有改进建议，请：

1. 检查日志文件获取详细错误信息
2. 参考本文档的故障排除部分
3. 在测试环境验证配置
4. 提交详细的问题报告

---

**⚠️ 重要提醒：** 本套 playbooks 主要用于教学和学习目的，在生产环境使用前请进行充分测试并根据实际需求调整配置。