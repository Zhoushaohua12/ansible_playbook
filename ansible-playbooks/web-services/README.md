# Web Services Playbooks - Nginx 场景合集

> ⚠️ **教学与演示用途**：以下 Nginx Playbooks 旨在帮助学习包管理器/源码安装、虚拟主机、HTTPS、自签名证书、反向代理、负载均衡与性能调优等场景。正式生产环境请根据实际安全策略与审计要求审慎调整。

## 📦 功能矩阵

| 场景 | 安装方式 | HTTPS/SSL | 反向代理 | 负载均衡 | 性能调优 | 默认启用 |
|------|----------|-----------|-----------|-----------|-----------|-----------|
| `nginx-install-configure.yml` | 包管理器 / 源码二选一 | 可选 | 否 | 否 | 是 | ✅ |
| `nginx-vhost-https.yml` | 继承通用安装 | ✅（支持自签名与已有证书） | 可选 | 否 | 是 | ✅ |
| `nginx-loadbalancer.yml` | 继承通用安装 | 可选 | 是 | ✅（最少连接 / IP Hash / Hash） | 是 | ✅ |
| `nginx-reverse-proxy.yml` | 继承通用安装 | 可选 | ✅（Header 强化） | 可选 | 是 | ✅ |

## 📂 目录结构

```
web-services/
├── nginx-install-configure.yml
├── nginx-vhost-https.yml
├── nginx-loadbalancer.yml
├── nginx-reverse-proxy.yml
├── vars/
│   └── default.yml              # 中文注释变量示例
├── templates/                   # nginx.conf.j2、虚拟主机、SSL、反向代理模板
├── handlers/
│   └── main.yml                 # 重载/重启/验证/防火墙等 Handler
└── roles/
    ├── nginx_common             # 安装、基础配置、服务管理
    ├── nginx_ssl                # 证书生成、SSL 片段
    └── nginx_proxy              # 反向代理、负载均衡、上游配置
```

## 🖥️ 操作系统与依赖

- **受测 OS**：CentOS 7/8/9、RHEL 8/9、Rocky Linux、Ubuntu 20.04+/22.04+、Debian 11+
- **Ansible 版本**：>= 2.13（需要 `community.crypto`, `community.general`, `ansible.posix`）
- **SSL 功能**：依赖 `community.crypto` 生成自签名证书；生产环境请替换为可信 CA
- **防火墙**：RedHat 系列使用 firewalld，Debian/Ubuntu 使用 UFW
- **SELinux**：默认启用布尔值 `httpd_can_network_connect` / `httpd_can_network_relay`

## ⚙️ 关键变量速览（`vars/default.yml`）

| 分类 | 变量 | 默认值 | 说明 |
|------|------|--------|------|
| 安装 | `nginx_install_method` | `package` | `package` 或 `source` 控制安装方式 |
| 版本 | `nginx_version` | `1.24.0` | 支持稳定版 / mainline |
| Worker | `nginx_worker_processes` | `auto` | 自动匹配 CPU 数量 |
| SSL | `nginx_ssl_enabled` | `true` | 控制是否渲染 SSL 片段 |
| 证书 | `nginx_ssl_self_signed_enabled` | `true` | 演示自签名证书生成（使用 `community.crypto`） |
| VHost | `nginx_vhosts` | `[]` | HTTP 虚拟主机定义，含 `php_enabled`、`locations` |
| HTTPS | `nginx_https_vhosts` | `[]` | HTTPS 虚拟主机，含 HSTS、HTTP 跳转开关 |
| 反向代理 | `nginx_reverse_proxy_vhosts` | `[]` | 自定义头部、WebSocket、缓存、速率限制 |
| 负载均衡 | `nginx_load_balancers` | `[]` | 定义算法、后端列表、健康检查、黏性会话 |
| 缓存 | `nginx_cache_enabled` | `true` | 控制 `proxy_cache_path` 及缓存策略 |
| 限流 | `nginx_rate_limit_enabled` | `true` | 速率限制与连接数限制 |
| 安全 | `nginx_security_enabled` | `true` | 统一控制安全头部 / HSTS / Referrer-Policy |
| 防火墙 | `nginx_firewall_enabled` | `true` | 自动开放 80/443 端口 |
| 备份 | `nginx_backup_enabled` | `true` | 触发配置归档处理程序 |

> 变量文件顶部包含中文安全提示，提醒修改默认密码/证书与限制来源。

## 🔁 Handlers（`handlers/main.yml`）

| Handler 名称 | 描述 |
|--------------|------|
| `restart nginx` / `reload nginx` | 使用 `ansible.builtin.service` 重启或平滑重载 |
| `verify nginx config` | 执行 `nginx -t` 校验配置语法 |
| `update firewall rules` | firewalld 或 UFW 同步开放端口 |
| `regenerate ssl certificates` | 触发 `nginx_ssl` 角色重新生成证书 |
| `rotate nginx logs` / `cleanup old logs` | 日志轮转与陈旧文件删除 |
| `clear nginx cache` | 移除并重建 `proxy_cache_path` |
| `backup nginx config` | 归档 `/etc/nginx` 配置，保留时间可配置 |
| `check nginx health` | `uri` 模块本地探测 + 服务状态输出 |

## 🚀 运行示例

```bash
# 1. 安装 + 基础配置（含包/源码切换）
ansible-playbook -i inventory web-services/nginx-install-configure.yml --syntax-check
ansible-playbook -i inventory web-services/nginx-install-configure.yml --tags install,config

# 2. HTTPS 虚拟主机（指定分组与标签）
ansible-playbook -i inventory web-services/nginx-vhost-https.yml --limit web_frontend --tags ssl,config

# 3. 负载均衡场景
ansible-playbook -i inventory web-services/nginx-loadbalancer.yml --tags install,loadbalancer,verify

# 4. 反向代理 / 头部加固 / 缓存 & 限流
ansible-playbook -i inventory web-services/nginx-reverse-proxy.yml --tags proxy,security
```

## 🧪 场景说明

1. **安装与调优**：`nginx_common` 角色根据 `nginx_install_method` 自动安装，并使用 `templates/nginx.conf.j2` 写入 worker、Gzip、缓存、限流等参数。
2. **HTTPS / 自签名**：`nginx_ssl` 调用 `community.crypto.openssl_*` 生成私钥/CSR/自签名证书并渲染 `ssl.conf.j2`。
3. **虚拟主机**：`virtual_host.conf.j2` 与 `reverse_proxy.conf.j2` 根据变量自动注入安全头、限流、PHP-FPM、WebSocket、缓存策略。
4. **负载均衡**：`nginx_proxy` 角色动态生成 `upstream_map.j2`、`upstreams.conf.j2` 及 `load_balancer.conf.j2`，支持 least_conn / ip_hash 等算法与健康检查定义。
5. **反向代理安全**：模板默认添加基于 Header 的安全加固、`proxy_headers.j2`、速率限制与缓存控制，并在 Handler 中验证 `nginx -t`。

## 🛠️ 故障排查

| 问题 | 现象 | 排查建议 |
|------|------|----------|
| 配置测试失败 | Handler 输出 `nginx -t` 失败 | 检查变量拼写、模板渲染后的配置；执行 `ansible-playbook ... -vvv` 获取详细错误 |
| SELinux 拒绝访问 | `permission denied`、`auditd` 报警 | 确认 `httpd_can_network_connect` / `httpd_can_network_relay` 已设置 `yes`，必要时添加自定义策略 |
| 防火墙阻断 | 外部无法访问 80/443 | 确保 `nginx_firewall_enabled=true` 或手动开放端口；RedHat 使用 `firewalld`, Debian/Ubuntu 使用 `ufw` |
| SSL 自签名无法被浏览器信任 | 浏览器提示不安全 | 仅供测试；生产环境请替换为受信任 CA 证书或 ACME/Let’s Encrypt |
| 负载均衡后端异常 | 某节点故障未自动摘除 | 调整 `health_check` 参数（interval/fails/passes）并查看 `error_log` |
| 反向代理头部错误 | 上游看到错误 IP/协议 | 检查 `proxy_set_headers` 值，确保 `X-Forwarded-*` 与 HSTS/HSTS 需求一致 |

## 📚 参考与最佳实践

- 所有 Playbook 均在 `vars_files: vars/default.yml` 中集中控制，可通过 `--extra-vars` 或 `group_vars` 细化。
- 模板包含中文注释，方便学习 Jinja2 条件与循环写法。
- 每个 Playbook 包含 `block/rescue` 与 `ansible.builtin.assert` 前置检查，务必在测试环境演练后再推广。
- 安全相关任务默认启用（限流、缓存、头部、HSTS、日志轮转），如需停用可设置对应布尔变量。

祝使用顺利，记得在实验环境充分验证后再上生产环境！
