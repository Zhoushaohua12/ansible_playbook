# Ansible Playbook 最佳实践

本文档总结 **ansible_playbook** 项目的最佳实践和安全建议，帮助用户更好地使用 Ansible 进行自动化运维。

## 目录

- [1. Playbook 运行流程](#1-playbook-运行流程)
- [2. Ansible Vault 使用指南](#2-ansible-vault-使用指南)
- [3. Check Mode（干运行）实践](#3-check-mode干运行实践)
- [4. 安全加固指南](#4-安全加固指南)
- [5. 性能优化建议](#5-性能优化建议)
- [6. 错误处理与调试](#6-错误处理与调试)
- [7. 团队协作规范](#7-团队协作规范)

---

## 1. Playbook 运行流程

### 1.1 标准执行流程

推荐按以下顺序执行 Playbook：

```bash
# 1. 语法检查
ansible-playbook playbook.yml --syntax-check

# 2. 干运行（Check Mode）
ansible-playbook playbook.yml --check

# 3. Diff 模式（查看变更）
ansible-playbook playbook.yml --check --diff

# 4. 限制主机范围（测试）
ansible-playbook playbook.yml --limit test-host

# 5. 正式执行
ansible-playbook playbook.yml

# 6. 详细输出（调试）
ansible-playbook playbook.yml -vvv
```

### 1.2 使用变量文件

**永远不要直接修改 `vars/example_vars.yml`**，应创建自己的变量文件：

```bash
# 1. 复制示例变量文件
cp vars/example_vars.yml vars/production_vars.yml

# 2. 编辑变量（替换占位符）
vim vars/production_vars.yml

# 3. 使用自定义变量文件执行
ansible-playbook playbook.yml -e @vars/production_vars.yml
```

### 1.3 使用标签（Tags）

为任务添加标签，实现部分执行：

```yaml
tasks:
  - name: 安装软件包
    ansible.builtin.apt:
      name: nginx
      state: present
    tags:
      - install
      - nginx

  - name: 配置 Nginx
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    tags:
      - config
      - nginx
```

```bash
# 只执行安装任务
ansible-playbook playbook.yml --tags install

# 跳过配置任务
ansible-playbook playbook.yml --skip-tags config
```

---

## 2. Ansible Vault 使用指南

### 2.1 加密单个变量

**推荐方式**：加密单个敏感变量而非整个文件

```bash
# 加密字符串
ansible-vault encrypt_string 'my_secret_password' --name 'vault_database_password'
```

输出：
```yaml
vault_database_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653765653765653765653735343...
```

将输出复制到变量文件中：

```yaml
# vars/production_vars.yml
database_host: localhost
database_user: app_user
vault_database_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653765653765653765653735343...
```

### 2.2 执行带 Vault 的 Playbook

```bash
# 方式 1: 交互式输入密码
ansible-playbook playbook.yml --ask-vault-pass

# 方式 2: 从文件读取密码
echo "my_vault_password" > .vault_pass
chmod 600 .vault_pass
ansible-playbook playbook.yml --vault-password-file .vault_pass

# 方式 3: 使用环境变量
export ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass
ansible-playbook playbook.yml
```

### 2.3 管理多个 Vault 密码

对不同环境使用不同的 Vault ID：

```bash
# 加密开发环境密码
ansible-vault encrypt_string 'dev_password' --name 'vault_db_password' --vault-id dev@prompt

# 加密生产环境密码
ansible-vault encrypt_string 'prod_password' --name 'vault_db_password' --vault-id prod@prompt

# 执行时指定 Vault ID
ansible-playbook playbook.yml --vault-id dev@.vault_dev_pass --vault-id prod@.vault_prod_pass
```

### 2.4 Vault 安全建议

1. ✅ **将 `.vault_pass` 加入 `.gitignore`**
2. ✅ **使用密码管理器生成强密码**
3. ✅ **定期轮换 Vault 密码**
4. ✅ **限制 Vault 密码文件权限** (`chmod 600`)
5. ❌ **不要将 Vault 密码提交到版本控制系统**

---

## 3. Check Mode（干运行）实践

### 3.1 什么是 Check Mode

Check Mode（检查模式，也称 Dry-Run）允许在不实际修改系统的情况下预览 Playbook 的执行结果。

### 3.2 全局 Check Mode

```bash
# 启用全局 Check Mode
ansible-playbook playbook.yml --check

# 结合 Diff 查看变更内容
ansible-playbook playbook.yml --check --diff
```

### 3.3 任务级 Check Mode 控制

某些任务可以强制执行或跳过：

```yaml
- name: 收集系统信息（总是执行，即使在 Check Mode 中）
  ansible.builtin.setup:
  check_mode: false  # 强制执行

- name: 删除旧文件（仅在 Check Mode 中预览）
  ansible.builtin.file:
    path: /tmp/old_file
    state: absent
  check_mode: true  # 强制检查模式
```

### 3.4 Check Mode 最佳实践

1. ✅ **在生产环境执行前，先运行 Check Mode**
2. ✅ **结合 `--diff` 参数查看文件变更**
3. ✅ **对关键操作任务添加 `check_mode: true` 示例**
4. ⚠️ **注意 Check Mode 的局限性**（某些模块不支持）

### 3.5 Check Mode 不支持的场景

以下操作在 Check Mode 中无法准确模拟：

- 命令执行结果（`shell`、`command`）
- 远程 API 调用（某些云模块）
- 依赖前置任务结果的任务

**解决方案**：使用 `check_mode: false` 强制执行前置任务

```yaml
- name: 创建临时目录（必须实际执行）
  ansible.builtin.file:
    path: /tmp/app_temp
    state: directory
  check_mode: false  # 即使在 Check Mode 中也执行

- name: 复制文件到临时目录
  ansible.builtin.copy:
    src: app.conf
    dest: /tmp/app_temp/app.conf
  # 依赖上一个任务，可以正常检查
```

---

## 4. 安全加固指南

### 4.1 敏感信息管理

#### 4.1.1 变量命名规范

- ✅ 敏感变量使用 `vault_` 前缀：`vault_database_password`
- ✅ 在 README 中明确标注哪些变量包含敏感信息
- ❌ 避免在变量名中直接暴露用途：`admin_password` → `vault_admin_password`

#### 4.1.2 任务日志保护

```yaml
# 错误示例：密码会出现在日志中
- name: 创建数据库用户
  community.postgresql.postgresql_user:
    name: app_user
    password: "{{ vault_database_password }}"
    state: present

# 正确示例：使用 no_log 隐藏日志
- name: 创建数据库用户
  community.postgresql.postgresql_user:
    name: app_user
    password: "{{ vault_database_password }}"
    state: present
  no_log: true  # 防止密码泄露
```

#### 4.1.3 调试模式安全

```yaml
# 通过变量控制日志输出
- name: 创建数据库用户
  community.postgresql.postgresql_user:
    name: app_user
    password: "{{ vault_database_password }}"
    state: present
  no_log: "{{ not enable_sensitive_logging | default(true) }}"
```

```bash
# 临时启用敏感日志（仅用于调试）
ansible-playbook playbook.yml -e "enable_sensitive_logging=true"
```

### 4.2 权限最小化原则

#### 4.2.1 避免全局 become

❌ **错误示例**：全局 root 权限
```yaml
- name: 配置应用
  hosts: all
  become: true  # 所有任务都使用 root 权限
  tasks:
    - name: 安装软件包
      ansible.builtin.apt:
        name: nginx
        state: present
    
    - name: 创建配置文件  # 不需要 root 权限
      ansible.builtin.copy:
        src: app.conf
        dest: ~/app.conf
```

✅ **正确示例**：按需提权
```yaml
- name: 配置应用
  hosts: all
  become: false  # 默认普通用户权限
  tasks:
    - name: 安装软件包
      ansible.builtin.apt:
        name: nginx
        state: present
      become: true  # 仅此任务使用 root 权限
    
    - name: 创建配置文件
      ansible.builtin.copy:
        src: app.conf
        dest: ~/app.conf
```

### 4.3 命令注入防护

#### 4.3.1 优先使用专用模块

❌ **危险示例**：使用 shell 模块
```yaml
- name: 创建用户
  ansible.builtin.shell: "useradd {{ username }}"  # 存在命令注入风险
```

✅ **安全示例**：使用 user 模块
```yaml
- name: 创建用户
  ansible.builtin.user:
    name: "{{ username }}"
    state: present
```

#### 4.3.2 使用 command 而非 shell

```yaml
# 危险：shell 会解析变量和特殊字符
- name: 删除文件
  ansible.builtin.shell: "rm -f {{ file_path }}"

# 安全：command 不解析特殊字符
- name: 删除文件
  ansible.builtin.file:
    path: "{{ file_path }}"
    state: absent
```

### 4.4 SSH 安全配置

#### 4.4.1 使用 SSH 密钥认证

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "ansible@example.com"

# 分发公钥
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@target-host

# Ansible 配置
ansible-playbook playbook.yml --private-key ~/.ssh/id_ed25519
```

#### 4.4.2 禁用密码认证（推荐）

```ini
# ansible.cfg
[defaults]
host_key_checking = True
private_key_file = ~/.ssh/id_ed25519

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o StrictHostKeyChecking=yes
```

---

## 5. 性能优化建议

### 5.1 并行执行

```ini
# ansible.cfg
[defaults]
forks = 50  # 默认 5，根据目标主机数量调整
```

```bash
# 命令行临时调整
ansible-playbook playbook.yml --forks 50
```

### 5.2 关闭 gather_facts

如果不需要主机信息，可以禁用事实收集：

```yaml
- name: 简单任务
  hosts: all
  gather_facts: false  # 节省 2-5 秒
  tasks:
    - name: 执行命令
      ansible.builtin.command: echo "Hello"
```

### 5.3 使用 Strategy 插件

```yaml
- name: 快速执行
  hosts: all
  strategy: free  # 不等待所有主机完成当前任务
  tasks:
    - name: 长时间运行的任务
      ansible.builtin.command: /opt/app/long_running_script.sh
```

### 5.4 缓存事实信息

```ini
# ansible.cfg
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_fact_cache
fact_caching_timeout = 3600
```

---

## 6. 错误处理与调试

### 6.1 错误处理策略

#### 6.1.1 忽略错误

```yaml
- name: 尝试启动服务（失败不中断）
  ansible.builtin.service:
    name: optional-service
    state: started
  ignore_errors: true
```

#### 6.1.2 条件失败

```yaml
- name: 检查磁盘空间
  ansible.builtin.shell: df -h / | awk 'NR==2 {print $5}' | sed 's/%//'
  register: disk_usage
  failed_when: disk_usage.stdout | int > 90
```

#### 6.1.3 Block/Rescue 机制

```yaml
- name: 部署应用（带回滚）
  block:
    - name: 停止服务
      ansible.builtin.service:
        name: app
        state: stopped
    
    - name: 更新代码
      ansible.builtin.git:
        repo: https://github.com/example/app.git
        dest: /opt/app
        version: v2.0.0
    
    - name: 启动服务
      ansible.builtin.service:
        name: app
        state: started
  
  rescue:
    - name: 回滚到旧版本
      ansible.builtin.git:
        repo: https://github.com/example/app.git
        dest: /opt/app
        version: v1.0.0
    
    - name: 启动服务
      ansible.builtin.service:
        name: app
        state: started
  
  always:
    - name: 记录部署结果
      ansible.builtin.debug:
        msg: "部署流程已完成"
```

### 6.2 调试技巧

#### 6.2.1 使用 debug 模块

```yaml
- name: 调试变量
  ansible.builtin.debug:
    var: ansible_facts
    verbosity: 2  # 只在 -vv 时显示
```

#### 6.2.2 注册变量查看结果

```yaml
- name: 执行命令
  ansible.builtin.command: ls -la /opt/app
  register: command_result

- name: 显示命令输出
  ansible.builtin.debug:
    var: command_result.stdout_lines
```

#### 6.2.3 使用 verbosity 级别

```bash
# -v: 基本输出
# -vv: 显示任务和主机信息
# -vvv: 显示连接和模块调用细节
# -vvvv: 显示所有插件和回调信息
ansible-playbook playbook.yml -vvv
```

---

## 7. 团队协作规范

### 7.1 版本控制最佳实践

#### 7.1.1 .gitignore 配置

```gitignore
# Ansible
*.retry
.vault_pass
vault_*.yml
!vars/example_vars.yml

# Python
__pycache__/
*.py[cod]
venv/

# IDE
.vscode/
.idea/
```

#### 7.1.2 提交规范

```bash
# 好的提交信息
git commit -m "feat(nginx): 添加 SSL 证书自动续期功能"
git commit -m "fix(database): 修复 PostgreSQL 连接超时问题"
git commit -m "docs(readme): 更新安装依赖说明"

# 不好的提交信息
git commit -m "fix bug"
git commit -m "update"
```

### 7.2 代码审查清单

提交 Pull Request 前，确保：

- [ ] 所有测试通过（`pytest`）
- [ ] Playbook 语法检查通过（`--syntax-check`）
- [ ] Check Mode 运行无错误（`--check`）
- [ ] 遵循风格指南（见 `docs/STYLE_GUIDE.md`）
- [ ] 更新了相关文档（README、元数据）
- [ ] 敏感信息已加密（Vault）
- [ ] 添加了适当的注释和说明

### 7.3 环境隔离

```bash
# 使用不同的 inventory 文件
ansible-playbook playbook.yml -i inventory/dev.ini      # 开发环境
ansible-playbook playbook.yml -i inventory/staging.ini  # 预发布环境
ansible-playbook playbook.yml -i inventory/prod.ini     # 生产环境

# 使用不同的变量文件
ansible-playbook playbook.yml -e @vars/dev_vars.yml
ansible-playbook playbook.yml -e @vars/prod_vars.yml
```

---

## 8. 常见陷阱与解决方案

### 8.1 变量优先级问题

Ansible 变量优先级（从高到低）：

1. 命令行 `-e` 参数
2. Task 级别 `vars`
3. Block 级别 `vars`
4. Play 级别 `vars`
5. `vars_files`
6. Role defaults

**建议**：使用 `vars_files` 管理环境变量，使用 `-e` 覆盖敏感信息。

### 8.2 幂等性陷阱

❌ **非幂等示例**：
```yaml
- name: 追加配置（每次执行都会重复追加）
  ansible.builtin.shell: echo "new_config" >> /etc/app.conf
```

✅ **幂等示例**：
```yaml
- name: 确保配置存在
  ansible.builtin.lineinfile:
    path: /etc/app.conf
    line: "new_config"
    state: present
```

### 8.3 Handler 不触发

Handler 只在任务状态为 `changed` 时触发：

```yaml
- name: 更新配置
  ansible.builtin.copy:
    src: nginx.conf
    dest: /etc/nginx/nginx.conf
  notify: 重启 Nginx  # 只有文件变更时才触发

handlers:
  - name: 重启 Nginx
    ansible.builtin.service:
      name: nginx
      state: restarted
```

**强制触发**（不推荐）：
```yaml
- name: 强制重启 Nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
  changed_when: true
```

---

## 附录：学习资源

- 📖 [Ansible 官方文档](https://docs.ansible.com/)
- 📖 [Ansible Galaxy](https://galaxy.ansible.com/)
- 📖 [本项目风格指南](STYLE_GUIDE.md)
- 📖 [本项目审计报告](../AUDIT_REPORT.md)

---

**版本**: 1.0  
**最后更新**: 2024-11-20  
**维护者**: ansible_playbook 项目团队
