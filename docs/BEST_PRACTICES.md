# Ansible Playbook 最佳实践指南

本文档总结了 ansible_playbook 项目中的最佳实践和编码规范，供开发团队参考。

---

## 📋 目录

1. [项目结构规范](#项目结构规范)
2. [Playbook 编写规范](#playbook-编写规范)
3. [变量和密钥管理](#变量和密钥管理)
4. [安全最佳实践](#安全最佳实践)
5. [测试和质量保证](#测试和质量保证)
6. [文档编写规范](#文档编写规范)
7. [命名约定](#命名约定)
8. [常见陷阱和解决方案](#常见陷阱和解决方案)

---

## 项目结构规范

### 标准模块结构

每个模块应遵循以下目录结构：

```
category/
  module_name/
    README.md              # 模块说明文档（必需）
    playbook.yml          # 主 playbook 文件（必需）
    vars/
      example_vars.yml    # 示例变量文件（必需）
    files/                # 静态文件（可选）
    templates/            # Jinja2 模板（可选）
    handlers/             # Handler 文件（可选）
```

### 模块分类

项目支持以下模块分类：

- **system/** - 系统管理（用户、服务、主机配置等）
- **files/** - 文件操作（复制、模板、同步等）
- **network/** - 网络配置（防火墙、路由、接口等）
- **database/** - 数据库管理（MySQL、PostgreSQL、MongoDB）
- **applications/** - 应用管理（软件包、容器、部署）
- **web/** - Web 服务器（Nginx、Apache）
- **storage/** - 存储管理（磁盘、LVM、文件系统）
- **monitoring/** - 监控系统（Prometheus、Zabbix、ELK）
- **message_queue/** - 消息队列（RabbitMQ、Kafka）
- **cloud/** - 云平台（AWS、Azure、GCP、阿里云）
- **virtualization/** - 虚拟化（libvirt、VMware）
- **version_control/** - 版本控制（Git）
- **advanced/** - 高级特性
- **network_protocols/** - 网络协议（HTTP、DNS、ICMP）
- **commands/** - 命令执行

---

## Playbook 编写规范

### 1. 基本结构

```yaml
---
- name: 模块功能的中文描述
  hosts: all
  gather_facts: true  # 明确声明是否收集 facts
  become: true        # 如果需要 sudo 权限
  
  vars_files:
    - vars/example_vars.yml
  
  tasks:
    - name: 任务的中文描述
      ansible.builtin.copy:  # 使用 FQCN
        src: "{{ source_file }}"
        dest: "{{ dest_path }}"
        owner: root
        group: root
        mode: '0644'
      tags:
        - config
        - files
```

### 2. 必需声明

#### gather_facts

**必须明确声明** `gather_facts`：

```yaml
# ✅ 正确
- name: 配置系统
  hosts: all
  gather_facts: true  # 需要 facts（如 ansible_distribution）

# ✅ 正确
- name: 简单任务
  hosts: all
  gather_facts: false  # 不需要 facts，提升性能

# ❌ 错误
- name: 配置系统
  hosts: all
  # 缺少 gather_facts 声明
```

**何时使用 `gather_facts: true`**：
- 需要访问系统信息（OS、IP、硬件等）
- 使用 `ansible_*` 变量
- 条件判断基于系统属性

**何时使用 `gather_facts: false`**：
- 纯文件操作
- 使用外部变量
- 性能敏感的场景

### 3. 使用 FQCN（完全限定集合名称）

从 Ansible 2.10 开始，推荐使用 FQCN 引用模块：

```yaml
# ✅ 推荐：使用 FQCN
- name: 复制配置文件
  ansible.builtin.copy:
    src: config.conf
    dest: /etc/myapp/config.conf

# ⚠️ 不推荐：短名称
- name: 复制配置文件
  copy:
    src: config.conf
    dest: /etc/myapp/config.conf
```

**常用 FQCN 对照表**：

| 模块 | FQCN |
|------|------|
| copy | ansible.builtin.copy |
| template | ansible.builtin.template |
| file | ansible.builtin.file |
| service | ansible.builtin.service |
| user | ansible.builtin.user |
| group | ansible.builtin.group |
| command | ansible.builtin.command |
| shell | ansible.builtin.shell |
| apt | ansible.builtin.apt |
| yum | ansible.builtin.yum |
| systemd | ansible.builtin.systemd |
| lineinfile | ansible.builtin.lineinfile |

### 4. 中文命名

所有面向用户的文本使用中文：

```yaml
# ✅ 正确
- name: 安装 Nginx Web 服务器
  ansible.builtin.apt:
    name: nginx
    state: present
  notify: 重启 Nginx

handlers:
  - name: 重启 Nginx
    ansible.builtin.service:
      name: nginx
      state: restarted

# ❌ 错误
- name: Install Nginx web server
  ansible.builtin.apt:
    name: nginx
    state: present
  notify: Restart Nginx
```

**命名原则**：
- 任务名（name）使用中文
- Handler 名称使用中文
- Play 名称使用中文
- 注释使用中文
- 技术术语保持英文（如 Nginx、MySQL、HTTP）

### 5. 变量引用

在 YAML 中引用变量时，必须使用引号：

```yaml
# ✅ 正确
tasks:
  - name: 设置内存大小
    vars:
      memory: "{{ vm_memory_mb }}"  # 用引号括起来
      
# ✅ 正确（整行是变量）
tasks:
  - name: 执行命令
    ansible.builtin.command: "{{ custom_command }}"

# ❌ 错误
tasks:
  - name: 设置内存大小
    vars:
      memory: {{ vm_memory_mb }}  # 会导致 YAML 语法错误
```

### 6. 支持 Check 模式

所有修改系统状态的 playbook 应支持 `--check` 模式：

```yaml
- name: 创建配置文件
  ansible.builtin.copy:
    src: config.conf
    dest: /etc/myapp/config.conf
  check_mode: yes  # 支持 dry-run

# 运行命令时
# ansible-playbook playbook.yml --check  # Dry-run
# ansible-playbook playbook.yml          # 实际执行
```

### 7. 幂等性

确保 playbook 可以重复执行而不产生副作用：

```yaml
# ✅ 幂等：使用 state 参数
- name: 确保 Nginx 已安装
  ansible.builtin.apt:
    name: nginx
    state: present

# ⚠️ 非幂等：重复执行会累积
- name: 添加配置行
  ansible.builtin.shell: |
    echo "option = value" >> /etc/config.conf

# ✅ 改进：使用 lineinfile
- name: 添加配置行
  ansible.builtin.lineinfile:
    path: /etc/config.conf
    line: "option = value"
    state: present
```

---

## 变量和密钥管理

### 1. 变量文件结构

```yaml
# vars/example_vars.yml
# ⚠️ 警告：本文件仅为示例配置
# ⚠️ 占位符必须使用 Ansible Vault 或环境变量替换
# ⚠️ 请勿在生产环境中直接使用这些示例值

---
# 基本配置
app_name: myapp
app_version: "1.0.0"

# 敏感信息（使用 vault_ 前缀）
db_host: localhost
db_port: 3306
db_name: "{{ app_name }}_db"
db_user: "{{ app_name }}_user"
db_password: "{{ vault_db_password }}"  # 从 Vault 读取

# 路径配置
app_install_dir: /opt/{{ app_name }}
app_config_dir: /etc/{{ app_name }}
app_log_dir: /var/log/{{ app_name }}
```

### 2. 敏感信息命名约定

**所有敏感信息必须使用 `vault_` 前缀**：

```yaml
# ✅ 正确
api_key: "{{ vault_api_key }}"
db_password: "{{ vault_db_password }}"
secret_token: "{{ vault_secret_token }}"
aws_access_key: "{{ vault_aws_access_key }}"

# ❌ 错误
api_key: "abc123def456"  # 硬编码
db_password: "P@ssw0rd"  # 硬编码
```

### 3. 使用 Ansible Vault

创建加密的变量文件：

```bash
# 创建新的 vault 文件
ansible-vault create vars/vault.yml

# 编辑 vault 文件
ansible-vault edit vars/vault.yml

# vault.yml 内容示例
---
vault_db_password: "actual_secure_password"
vault_api_key: "actual_api_key_value"
vault_secret_token: "actual_secret_token"
```

在 playbook 中引用：

```yaml
- name: 部署应用
  hosts: app_servers
  vars_files:
    - vars/example_vars.yml
    - vars/vault.yml  # 加密的敏感信息
  
  tasks:
    - name: 配置数据库连接
      ansible.builtin.template:
        src: config.j2
        dest: /etc/myapp/config.conf
      no_log: true  # 不记录敏感信息
```

运行 playbook：

```bash
# 使用密码提示
ansible-playbook playbook.yml --ask-vault-pass

# 使用密码文件
ansible-playbook playbook.yml --vault-password-file .vault_pass

# 使用多个 vault ID
ansible-playbook playbook.yml --vault-id dev@prompt --vault-id prod@.vault_pass
```

### 4. 环境变量方式

在 CI/CD 或容器环境中，可以使用环境变量：

```yaml
# playbook.yml
- name: 部署应用
  hosts: all
  vars:
    db_password: "{{ lookup('env', 'DB_PASSWORD') }}"
    api_key: "{{ lookup('env', 'API_KEY') }}"
  
  tasks:
    - name: 配置应用
      ansible.builtin.template:
        src: config.j2
        dest: /etc/myapp/config.conf
      no_log: true
```

运行时：

```bash
export DB_PASSWORD="secure_password"
export API_KEY="api_key_value"
ansible-playbook playbook.yml
```

---

## 安全最佳实践

### 1. 使用 no_log

所有涉及敏感信息的任务必须使用 `no_log: true`：

```yaml
# ✅ 正确
- name: 创建数据库用户
  community.mysql.mysql_user:
    name: "{{ db_user }}"
    password: "{{ db_password }}"
    priv: "{{ db_name }}.*:ALL"
  no_log: true  # 防止密码泄露到日志

# ✅ 正确
- name: 设置 API 密钥
  ansible.builtin.lineinfile:
    path: /etc/myapp/config
    line: "api_key={{ api_key }}"
    state: present
  no_log: true

# ❌ 错误（会泄露密码到日志）
- name: 创建数据库用户
  community.mysql.mysql_user:
    name: "{{ db_user }}"
    password: "{{ db_password }}"
    priv: "{{ db_name }}.*:ALL"
```

**需要 no_log 的场景**：
- 设置密码
- 配置 API 密钥
- 处理 Token
- 证书私钥操作
- OAuth 凭证
- 数据库连接字符串

### 2. 避免硬编码

**❌ 绝不允许**：

```yaml
# ❌ 硬编码密码
db_password: "MyPassword123"

# ❌ 硬编码 API 密钥
api_key: "sk_live_1234567890abcdef"

# ❌ 硬编码 Token
auth_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**✅ 正确做法**：

```yaml
# ✅ 使用占位符
db_password: "PLEASE_CHANGE_THIS"

# ✅ 使用 vault 变量
db_password: "{{ vault_db_password }}"

# ✅ 使用环境变量
api_key: "{{ lookup('env', 'API_KEY') }}"
```

### 3. 文件权限

设置适当的文件权限：

```yaml
# ✅ 配置文件使用严格权限
- name: 创建配置文件
  ansible.builtin.template:
    src: config.j2
    dest: /etc/myapp/config.conf
    owner: root
    group: myapp
    mode: '0640'  # rw-r-----

# ✅ 密钥文件使用最严格权限
- name: 部署 SSL 私钥
  ansible.builtin.copy:
    src: "{{ ssl_key_file }}"
    dest: /etc/ssl/private/myapp.key
    owner: root
    group: root
    mode: '0600'  # rw-------
  no_log: true
```

### 4. 安全的命令执行

使用 `command` 代替 `shell`，除非需要 shell 特性：

```yaml
# ✅ 推荐：使用 command
- name: 列出文件
  ansible.builtin.command:
    cmd: ls /var/log
  register: log_files

# ⚠️ 仅在需要时使用 shell
- name: 使用管道
  ansible.builtin.shell: |
    cat /var/log/app.log | grep ERROR | wc -l
  register: error_count

# 如果使用 shell，注意注入风险
# ❌ 危险：用户输入未过滤
- name: 危险的命令
  ansible.builtin.shell: |
    echo "{{ user_input }}" > /tmp/output

# ✅ 安全：使用 quote 过滤器
- name: 安全的命令
  ansible.builtin.shell: |
    echo {{ user_input | quote }} > /tmp/output
```

### 5. 变量文件警告头

所有示例变量文件必须包含警告头：

```yaml
# ⚠️ 警告：本文件仅为示例配置
# ⚠️ 占位符必须使用 Ansible Vault 或环境变量替换
# ⚠️ 请勿在生产环境中直接使用这些示例值
---
```

---

## 测试和质量保证

### 1. 测试结构

每个模块分类应有对应的测试文件：

```python
# tests/test_system.py
import pytest
from pathlib import Path

def test_system_modules_structure():
    """测试 system 模块的文件结构"""
    base_path = Path("system")
    assert base_path.exists(), "system 目录不存在"
    
    for module_dir in base_path.iterdir():
        if not module_dir.is_dir():
            continue
        
        # 检查必需文件
        assert (module_dir / "README.md").exists(), \
            f"{module_dir.name} 缺少 README.md"
        
        assert (module_dir / "playbook.yml").exists(), \
            f"{module_dir.name} 缺少 playbook.yml"
        
        assert (module_dir / "vars" / "example_vars.yml").exists(), \
            f"{module_dir.name} 缺少 vars/example_vars.yml"

def test_playbook_syntax():
    """测试 playbook YAML 语法"""
    import yaml
    
    for playbook in Path("system").rglob("playbook.yml"):
        with open(playbook, 'r') as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"{playbook} YAML 语法错误: {e}")
```

### 2. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_system.py

# 详细输出
pytest -v tests/

# 显示覆盖率
pytest --cov=. tests/
```

### 3. Syntax Check

```bash
# 检查单个 playbook
ansible-playbook playbook.yml --syntax-check

# 批量检查
find . -name "playbook.yml" -exec ansible-playbook --syntax-check {} \;
```

### 4. Dry Run

```bash
# Check 模式（不实际执行）
ansible-playbook playbook.yml --check

# Diff 模式（显示将要修改的内容）
ansible-playbook playbook.yml --check --diff
```

### 5. 使用审计工具

定期运行审计工具确保代码质量：

```bash
# 运行全面审计
venv/bin/python tools/comprehensive_audit.py

# 运行快速修复
tools/quick_fix.sh

# 监控审计趋势
tools/audit_monitor.sh
```

---

## 文档编写规范

### 1. README 结构

每个模块的 README.md 应包含：

````markdown
# 模块名称

简短描述模块的功能和用途（1-2句话）。

## 功能特性

- 功能点 1
- 功能点 2
- 功能点 3

## 使用场景

描述该模块的典型应用场景。

## 前置条件

- Ansible 版本要求
- 必需的 Collections
- 目标系统要求
- 其他依赖

## 变量说明

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| var1 | string | - | 变量说明 |
| var2 | boolean | true | 变量说明 |

## 使用示例

### 基础用法

```bash
# 1. 配置变量
cp vars/example_vars.yml vars/my_vars.yml
vim vars/my_vars.yml

# 2. 运行 playbook
ansible-playbook playbook.yml -e @vars/my_vars.yml

# 3. Dry-run 模式
ansible-playbook playbook.yml -e @vars/my_vars.yml --check
```

### 高级用法

提供更复杂的使用示例。

## 注意事项

- ⚠️ 重要注意事项 1
- ⚠️ 重要注意事项 2

## 故障排查

### 问题1: 描述
**解决方案**: 解决步骤

### 问题2: 描述
**解决方案**: 解决步骤

## 相关模块

- [相关模块1](../module1/README.md)
- [相关模块2](../module2/README.md)

## 参考文档

- [官方文档链接](https://...)
- 其他参考资料
````

### 2. 中文文档规范

- 使用简体中文
- 技术术语保持英文（Nginx、MySQL、HTTP 等）
- 命令和代码使用英文
- 说明和描述使用中文
- 避免中英混用（"使用 the 配置"）

### 3. 代码示例

文档中的代码示例应：
- 完整可运行
- 包含注释
- 遵循项目规范
- 提供实际场景

---

## 命名约定

### 1. 变量命名

```yaml
# ✅ 推荐：使用下划线分隔的小写字母
db_host: localhost
app_install_dir: /opt/myapp
max_connections: 100

# ❌ 避免：驼峰命名
dbHost: localhost
appInstallDir: /opt/myapp

# ❌ 避免：全大写（保留给常量）
DB_HOST: localhost
```

### 2. 任务命名

```yaml
# ✅ 推荐：动词开头，描述清晰
- name: 安装 Nginx 软件包
- name: 创建应用目录
- name: 启动 MySQL 服务
- name: 配置防火墙规则

# ❌ 避免：模糊不清
- name: 处理文件
- name: 设置
- name: 执行操作
```

### 3. 文件命名

```bash
# ✅ playbook 文件
playbook.yml         # 主 playbook
site.yml            # 站点级 playbook

# ✅ 变量文件
example_vars.yml    # 示例变量
vault.yml          # 加密变量
defaults.yml       # 默认值

# ✅ 模板文件
config.j2          # Jinja2 模板
nginx.conf.j2      # 带扩展名的模板

# ✅ 测试文件
test_system.py     # Python 测试
```

### 4. 标签命名

```yaml
tags:
  - config        # 配置相关
  - install       # 安装相关
  - security      # 安全相关
  - database      # 数据库相关
  - never         # 默认不执行
```

---

## 常见陷阱和解决方案

### 1. YAML 语法错误

**问题**：变量引用未加引号

```yaml
# ❌ 错误
memory: {{ vm_memory }}

# ✅ 正确
memory: "{{ vm_memory }}"
```

### 2. 幂等性问题

**问题**：使用 shell/command 导致重复执行

```yaml
# ❌ 问题：每次都执行
- name: 添加配置
  ansible.builtin.shell: |
    echo "setting=value" >> /etc/config

# ✅ 解决：使用幂等模块
- name: 添加配置
  ansible.builtin.lineinfile:
    path: /etc/config
    line: "setting=value"
    state: present
```

### 3. 性能问题

**问题**：不必要的 facts 收集

```yaml
# ❌ 问题：默认收集 facts，浪费时间
- name: 简单任务
  hosts: all
  tasks:
    - name: 创建文件
      ansible.builtin.file:
        path: /tmp/test
        state: touch

# ✅ 解决：禁用 facts 收集
- name: 简单任务
  hosts: all
  gather_facts: false
  tasks:
    - name: 创建文件
      ansible.builtin.file:
        path: /tmp/test
        state: touch
```

### 4. 敏感信息泄露

**问题**：日志中记录密码

```yaml
# ❌ 问题：密码会出现在日志中
- name: 创建用户
  ansible.builtin.user:
    name: myuser
    password: "{{ user_password }}"

# ✅ 解决：添加 no_log
- name: 创建用户
  ansible.builtin.user:
    name: myuser
    password: "{{ user_password }}"
  no_log: true
```

### 5. Handler 不执行

**问题**：Handler 名称不匹配

```yaml
# ❌ 问题
tasks:
  - name: 修改配置
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: restart nginx  # 小写

handlers:
  - name: Restart Nginx  # 大写，不匹配
    ansible.builtin.service:
      name: nginx
      state: restarted

# ✅ 解决：确保名称完全匹配
tasks:
  - name: 修改配置
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: 重启 Nginx

handlers:
  - name: 重启 Nginx  # 完全匹配
    ansible.builtin.service:
      name: nginx
      state: restarted
```

### 6. 条件判断错误

**问题**：字符串比较错误

```yaml
# ❌ 问题：类型不匹配
when: ansible_distribution == Ubuntu

# ✅ 解决：字符串用引号
when: ansible_distribution == "Ubuntu"

# ✅ 或使用 in
when: ansible_distribution in ["Ubuntu", "Debian"]
```

---

## 工具使用

### 审计工具

```bash
# 全面审计
venv/bin/python tools/comprehensive_audit.py

# 查看报告
cat reports/comprehensive_audit.md
```

### 快速修复

```bash
# 自动修复常见问题
./tools/quick_fix.sh

# 查看修复报告
cat reports/quick_fix_report.txt
```

### Pre-commit Hook

```bash
# 安装 pre-commit hook
cp tools/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 测试 hook
git add .
git commit -m "test"
```

### 监控审计

```bash
# 运行监控
./tools/audit_monitor.sh

# 查看趋势
cat reports/audit_history/audit_trend.csv
```

---

## 持续改进

### 定期审计

建议每周运行一次全面审计：

```bash
# 添加到 crontab
0 9 * * 1 cd /path/to/project && ./tools/audit_monitor.sh
```

### 代码审查清单

提交前检查：

- [ ] YAML 语法正确
- [ ] 使用了 FQCN
- [ ] 声明了 gather_facts
- [ ] 敏感任务使用了 no_log
- [ ] 变量文件有警告头
- [ ] 任务名使用中文
- [ ] 支持 check 模式
- [ ] 更新了文档
- [ ] 添加了测试

### 团队协作

- 使用统一的代码风格
- 定期分享最佳实践
- 记录常见问题和解决方案
- 更新本文档

---

**最后更新**: 2025-11-24  
**维护者**: Ansible Playbook 团队
