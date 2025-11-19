# SSL 证书自动化管理

## 服务简介

SSL/TLS 证书是 HTTPS 通信的基础，用于加密客户端与服务器之间的通信。本示例展示如何使用 Ansible 自动化获取、部署、验证和续期 SSL 证书。我们重点关注使用 Let's Encrypt 提供的免费证书，通过 `community.crypto.acme_certificate` 模块实现自动化管理，并配合定时任务实现证书自动续期与到期提醒。

核心特性：
- **自动证书获取**：使用 ACME 协议从 Let's Encrypt 或其他 CA 获取证书
- **多种验证方法**：支持 HTTP-01、DNS-01、TLS-ALPN-01 等验证方式
- **证书链管理**：自动获取完整证书链（包含中间证书）
- **证书续期**：自动检查证书过期时间并续期
- **到期提醒**：通过监控和告警机制提醒管理员
- **多域名支持**：支持单域名和多域名（SAN）证书
- **安全存储**：集成 Ansible Vault 保护私钥安全

## 常用 Ansible 模块

### ansible.builtin.package / ansible.builtin.apt / ansible.builtin.yum
**用途**：安装证书管理所需的依赖工具

**常用参数**：
- `name`：包名称（如 `python3-openssl`、`python3-cryptography`）
- `state`：期望状态（`present` 安装、`absent` 卸载）
- `update_cache`：是否更新包缓存（apt 专用）

**示例**：
```yaml
- name: 安装 SSL 证书依赖
  ansible.builtin.package:
    name:
      - python3-openssl
      - python3-cryptography
    state: present
```

### community.crypto.acme_certificate
**用途**：使用 ACME 协议从 Let's Encrypt 等 CA 获取或续期 SSL 证书

**常用参数**：
- `account_key_src`：ACME 账户私钥路径
- `account_email`：ACME 账户邮箱（用于接收到期提醒）
- `challenge`：验证方式（`http-01`、`dns-01`、`tls-alpn-01`）
- `csr_src`：证书签名请求（CSR）文件路径
- `dest`：证书文件输出路径
- `fullchain_dest`：完整证书链输出路径
- `chain_dest`：中间证书链输出路径
- `terms_agreed`：是否同意 Let's Encrypt 服务条款
- `acme_directory`：ACME 服务器地址（如 `https://acme-v02.api.letsencrypt.org/directory`）
- `acme_version`：ACME 协议版本（通常为 `2`）

**示例**：
```yaml
- name: 申请 Let's Encrypt 证书
  community.crypto.acme_certificate:
    account_key_src: /etc/pki/acme/account.key
    account_email: admin@example.com
    challenge: http-01
    csr_src: /etc/pki/tls/certs/server.csr
    dest: /etc/pki/tls/certs/server.crt
    fullchain_dest: /etc/pki/tls/certs/fullchain.pem
    chain_dest: /etc/pki/tls/certs/chain.pem
    terms_agreed: yes
    acme_directory: "https://acme-v02.api.letsencrypt.org/directory"
    acme_version: 2
    state: present
  register: cert_result
```

### community.crypto.openssl_privatekey
**用途**：生成私钥文件

**常用参数**：
- `path`：私钥文件路径
- `size`：密钥长度（默认 4096）
- `type`：密钥类型（`RSA`、`ECC`）
- `passphrase`：私钥密码保护（可选）
- `force`：是否覆盖已存在的文件

**示例**：
```yaml
- name: 生成 RSA 私钥
  community.crypto.openssl_privatekey:
    path: /etc/pki/tls/private/server.key
    size: 4096
    type: RSA
    force: no
```

### community.crypto.openssl_csr
**用途**：生成证书签名请求（CSR）

**常用参数**：
- `path`：CSR 文件路径
- `privatekey_path`：关联的私钥路径
- `common_name`：证书 CN（通常为域名）
- `subject_alt_name`：主体备用名称（支持多域名 SAN）
- `country_name`、`state_or_province_name`、`locality_name`、`organization_name`：证书主体信息

**示例**：
```yaml
- name: 生成证书签名请求（CSR）
  community.crypto.openssl_csr:
    path: /etc/pki/tls/certs/server.csr
    privatekey_path: /etc/pki/tls/private/server.key
    common_name: example.com
    subject_alt_name:
      - "DNS:example.com"
      - "DNS:*.example.com"
      - "DNS:www.example.com"
    country_name: CN
    state_or_province_name: Beijing
    locality_name: Beijing
    organization_name: Example Corp
```

### ansible.builtin.template
**用途**：部署证书配置文件（如 Nginx/Apache 虚拟主机配置）

**常用参数**：
- `src`：模板文件路径
- `dest`：目标路径
- `owner`、`group`、`mode`：文件权限
- `validate`：验证命令
- `backup`：备份原文件

**示例**：
```yaml
- name: 部署 Nginx HTTPS 虚拟主机配置
  ansible.builtin.template:
    src: templates/nginx_https.conf.j2
    dest: /etc/nginx/sites-available/example.conf
    owner: root
    group: root
    mode: '0644'
    validate: 'nginx -t -c %s'
  notify: 重载 Nginx
```

### ansible.builtin.service
**用途**：管理 Web 服务状态，使新证书配置生效

**常用参数**：
- `name`：服务名称（如 `nginx`、`apache2`）
- `state`：期望状态（`started` 启动、`stopped` 停止、`restarted` 重启、`reloaded` 重载）
- `enabled`：是否开机自启

**示例**：
```yaml
- name: 重启 Nginx 使新证书生效
  ansible.builtin.service:
    name: nginx
    state: restarted
    enabled: yes
```

### ansible.builtin.cron
**用途**：配置定时任务自动续期证书

**常用参数**：
- `name`：任务名称
- `job`：执行的命令
- `minute`、`hour`、`day`、`month`、`weekday`：执行时间
- `state`：任务状态（`present` 或 `absent`）

**示例**：
```yaml
- name: 配置证书自动续期定时任务
  ansible.builtin.cron:
    name: Let's Encrypt 证书续期
    minute: "0"
    hour: "2"
    job: "/usr/local/bin/renew_certificate.sh"
    state: present
```

## 主要参数说明

### Let's Encrypt 账户配置
- `account_email`：接收证书过期提醒的邮箱（重要）
- `account_key_src`：ACME 账户私钥路径（需保密）
- `terms_agreed`：同意 Let's Encrypt 服务条款（必须为 `yes`）
- `acme_version`：通常使用版本 2（最新版本）

### 证书配置
- `common_name`：证书主体（通常为主域名）
- `subject_alt_name`：主体备用名称（支持多个域名）
- `organization_name`：组织名称
- `country_name`、`state_or_province_name`、`locality_name`：地理位置信息

### 验证方式
- **HTTP-01**：通过 HTTP 访问 `.well-known/acme-challenge` 进行域名验证
  - 适用于可公网访问的域名
  - 需要在 Web 服务器配置特定路径的访问
  
- **DNS-01**：通过 DNS TXT 记录进行域名验证
  - 适用于所有类型域名（包括非公网）
  - 需要 DNS API 访问权限（如 Route 53、Cloudflare）
  
- **TLS-ALPN-01**：通过 TLS 连接进行验证
  - 较新的验证方式

### 证书续期参数
- `renewal_days`：距离到期日期的天数阈值（到期前多少天开始续期）
- `renewal_retry_attempts`：续期重试次数
- `renewal_email_days`：距离到期日期的天数阈值（到期前多少天发送邮件提醒）

## 日志路径

### 证书存储位置
- **私钥**：`/etc/pki/tls/private/server.key`（权限 `600`，只有 root 可读）
- **证书**：`/etc/pki/tls/certs/server.crt`
- **完整证书链**：`/etc/pki/tls/certs/fullchain.pem`
- **中间证书**：`/etc/pki/tls/certs/chain.pem`

### 日志文件
- **Certbot 日志**：`/var/log/letsencrypt/letsencrypt.log`
- **Ansible 日志**：可通过 `ansible-playbook playbook.yml -v` 查看详细日志

### 自动续期日志
- **Cron 日志**：`/var/log/syslog` 或 `/var/log/messages`（查看定时任务执行记录）
- **续期脚本日志**：通常在 `/var/log/certificate_renewal.log`

## 常见部署场景

### 场景 1：从零开始申请新 Let's Encrypt 证书
**需求**：为 example.com 申请 Let's Encrypt 证书

**步骤**：
1. 生成 ACME 账户私钥
2. 生成服务器私钥
3. 生成 CSR 文件
4. 申请 Let's Encrypt 证书（HTTP-01 验证）
5. 部署证书到 Web 服务器

**关键任务**：
```yaml
# 1. 生成账户私钥
- name: 生成 ACME 账户私钥
  community.crypto.openssl_privatekey:
    path: /etc/pki/acme/account.key
    size: 4096
    force: no

# 2. 生成服务器私钥
- name: 生成服务器私钥
  community.crypto.openssl_privatekey:
    path: /etc/pki/tls/private/server.key
    size: 4096
    force: no

# 3. 生成 CSR
- name: 生成证书签名请求
  community.crypto.openssl_csr:
    path: /etc/pki/tls/certs/server.csr
    privatekey_path: /etc/pki/tls/private/server.key
    common_name: example.com
    subject_alt_name:
      - "DNS:example.com"
      - "DNS:*.example.com"

# 4. 申请证书
- name: 申请 Let's Encrypt 证书
  community.crypto.acme_certificate:
    account_key_src: /etc/pki/acme/account.key
    account_email: admin@example.com
    challenge: http-01
    csr_src: /etc/pki/tls/certs/server.csr
    dest: /etc/pki/tls/certs/server.crt
    fullchain_dest: /etc/pki/tls/certs/fullchain.pem
    terms_agreed: yes
    state: present
```

### 场景 2：自动续期与到期提醒
**需求**：配置定时任务自动续期证书，并在到期前发送提醒

**步骤**：
1. 创建续期脚本
2. 配置续期定时任务
3. 配置到期提醒告警

**关键配置**：
```yaml
# 1. 创建续期脚本
- name: 创建证书续期脚本
  ansible.builtin.copy:
    dest: /usr/local/bin/renew_certificate.sh
    content: |
      #!/bin/bash
      # Let's Encrypt 证书自动续期脚本
      
      ACCOUNT_KEY="/etc/pki/acme/account.key"
      SERVER_KEY="/etc/pki/tls/private/server.key"
      SERVER_CSR="/etc/pki/tls/certs/server.csr"
      SERVER_CRT="/etc/pki/tls/certs/server.crt"
      FULLCHAIN="/etc/pki/tls/certs/fullchain.pem"
      
      # 检查证书过期时间
      EXPIRY=$(openssl x509 -in $SERVER_CRT -noout -dates | grep notAfter | cut -d= -f2)
      EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
      CURRENT_EPOCH=$(date +%s)
      DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
      
      # 如果剩余天数小于 30，则续期
      if [ $DAYS_LEFT -lt 30 ]; then
        echo "证书即将过期（剩余 $DAYS_LEFT 天），开始续期..." >> /var/log/certificate_renewal.log
        # 这里调用 ansible-playbook 或 certbot 进行续期
      fi
    mode: '0755'

# 2. 配置续期定时任务
- name: 配置证书自动续期任务
  ansible.builtin.cron:
    name: Let's Encrypt 证书续期
    minute: "0"
    hour: "2"
    day: "1"  # 每月第一天
    job: "/usr/local/bin/renew_certificate.sh"
    state: present

# 3. 配置到期提醒（监控任务）
- name: 配置证书到期检查任务
  ansible.builtin.cron:
    name: 证书过期提醒
    minute: "0"
    hour: "8"
    job: "/usr/local/bin/check_cert_expiry.sh"
    state: present
```

### 场景 3：多域名证书（SAN）管理
**需求**：为 example.com 及其所有子域名申请单一多域名证书

**步骤**：
1. 在 CSR 中指定多个 SAN
2. 申请多域名证书
3. 配置 Web 服务器使用多域名证书

**关键任务**：
```yaml
- name: 生成多域名 CSR
  community.crypto.openssl_csr:
    path: /etc/pki/tls/certs/server.csr
    privatekey_path: /etc/pki/tls/private/server.key
    common_name: example.com
    subject_alt_name:
      - "DNS:example.com"
      - "DNS:*.example.com"
      - "DNS:www.example.com"
      - "DNS:api.example.com"
      - "DNS:admin.example.com"
    country_name: CN
    state_or_province_name: Beijing
    locality_name: Beijing
    organization_name: Example Corp

- name: 申请多域名 Let's Encrypt 证书
  community.crypto.acme_certificate:
    account_key_src: /etc/pki/acme/account.key
    account_email: admin@example.com
    challenge: http-01
    csr_src: /etc/pki/tls/certs/server.csr
    dest: /etc/pki/tls/certs/server.crt
    fullchain_dest: /etc/pki/tls/certs/fullchain.pem
    terms_agreed: yes
    state: present
```

### 场景 4：DNS-01 验证（用于非公网域名）
**需求**：使用 DNS-01 验证方式为私有域名申请证书

**步骤**：
1. 准备 DNS API 凭证
2. 生成 DNS 验证请求
3. 自动更新 DNS 记录
4. 申请证书

**关键任务**：
```yaml
# 该场景需要 DNS 提供商的 API 支持，例如 Cloudflare、Route 53 等
- name: 使用 DNS-01 验证申请证书
  community.crypto.acme_certificate:
    account_key_src: /etc/pki/acme/account.key
    account_email: admin@example.com
    challenge: dns-01
    csr_src: /etc/pki/tls/certs/server.csr
    dest: /etc/pki/tls/certs/server.crt
    fullchain_dest: /etc/pki/tls/certs/fullchain.pem
    terms_agreed: yes
    state: present
  # 需要配合 DNS 提供商的 webhook 或 API 集成
```

## 如何在本地测试

### 1. 语法检查
```bash
ansible-playbook playbook.yml --syntax-check
```

### 2. Check 模式（模拟运行）
```bash
ansible-playbook playbook.yml -i localhost, --connection=local --check
```

### 3. 安装依赖集合
```bash
ansible-galaxy collection install community.crypto
ansible-galaxy collection install community.general
```

### 4. 测试证书申请
```bash
# 申请单个域名证书
ansible-playbook playbook.yml -i localhost, --connection=local --tags cert_generate

# 申请多域名证书
ansible-playbook playbook.yml -i localhost, --connection=local --tags cert_san
```

### 5. 验证证书
```bash
# 检查私钥与证书匹配
openssl x509 -noout -modulus -in /etc/pki/tls/certs/server.crt | openssl md5
openssl rsa -noout -modulus -in /etc/pki/tls/private/server.key | openssl md5

# 查看证书详细信息
openssl x509 -in /etc/pki/tls/certs/server.crt -noout -text

# 检查证书有效期
openssl x509 -in /etc/pki/tls/certs/server.crt -noout -dates
```

### 6. 部署到 Web 服务器
```bash
# 运行完整 playbook
ansible-playbook playbook.yml -i hosts.ini

# 验证 Web 服务器配置
nginx -t
apachectl configtest
```

## 证书安全最佳实践

1. **密钥保管**：
   - 私钥文件权限设为 `600`（仅 root 可读）
   - 使用 Ansible Vault 加密敏感变量
   - 定期备份并异地存储私钥

2. **证书验证**：
   - 始终验证证书链的完整性
   - 使用 `fullchain.pem` 而非仅单个证书文件
   - 定期检查 CA 根证书更新

3. **到期管理**：
   - 配置多层到期提醒（30天、14天、7天）
   - 定期检查证书有效期
   - 自动续期机制应该冗余（至少两个方案）

4. **安全审计**：
   - 记录所有证书申请和续期操作
   - 监控证书访问日志
   - 定期审计密钥文件权限

5. **多证书策略**：
   - 为不同服务准备独立证书
   - 使用通配符证书时谨慎（降低安全性）
   - 考虑分离生产和测试证书

## 故障排查

### 常见问题 1：证书申请失败
**症状**：申请 Let's Encrypt 证书时出错

**排查步骤**：
```bash
# 检查账户私钥是否存在
ls -la /etc/pki/acme/account.key

# 检查域名是否可公网访问
dig example.com @8.8.8.8

# 查看详细错误日志
ansible-playbook playbook.yml -vvv
```

### 常见问题 2：证书续期失败
**症状**：自动续期任务没有执行或失败

**排查步骤**：
```bash
# 检查 cron 任务
crontab -l

# 查看 cron 日志
grep CRON /var/log/syslog | tail -20

# 手动执行续期脚本
/usr/local/bin/renew_certificate.sh -v
```

### 常见问题 3：证书文件权限错误
**症状**：Web 服务无法读取证书文件

**排查步骤**：
```bash
# 检查文件权限
ls -la /etc/pki/tls/certs/
ls -la /etc/pki/tls/private/

# 修复权限
sudo chmod 644 /etc/pki/tls/certs/server.crt
sudo chmod 600 /etc/pki/tls/private/server.key
```

## 相关资源

- [Let's Encrypt 官方网站](https://letsencrypt.org/)
- [Certbot 文档](https://certbot.eff.org/)
- [Ansible community.crypto 模块](https://docs.ansible.com/ansible/latest/collections/community/crypto/index.html)
- [ACME 协议规范](https://tools.ietf.org/html/rfc8555)
- [OpenSSL 命令参考](https://www.openssl.org/docs/man1.1.1/)
- [SSL/TLS 最佳实践](https://ssl-config.mozilla.org/)
