# Ansible Playbook 风格指南

本文档定义 **ansible_playbook** 项目的统一编码规范和文档风格，所有贡献者在提交代码前应遵循本指南。

## 目录

- [1. Playbook 结构规范](#1-playbook-结构规范)
- [2. 变量文件规范](#2-变量文件规范)
- [3. 文档规范](#3-文档规范)
- [4. 命名规范](#4-命名规范)
- [5. 安全规范](#5-安全规范)
- [6. 测试规范](#6-测试规范)
- [7. 元数据规范](#7-元数据规范)

---

## 1. Playbook 结构规范

### 1.1 文件结构

所有 Playbook 文件必须遵循以下结构：

```yaml
---
- name: 中文 Play 名称（简洁明确）
  hosts: all
  gather_facts: false  # 或 true，必须显式声明
  become: false        # 或 true，根据需要设置
  vars_files:
    - vars/example_vars.yml
  
  tasks:
    - name: 中文任务名称
      ansible.builtin.debug:
        msg: "使用 FQCN 调用模块"
  
  handlers:
    - name: 中文 Handler 名称
      ansible.builtin.service:
        name: nginx
        state: restarted
```

### 1.2 字段顺序

Play 级别字段按以下顺序排列：

1. `name` - Play 名称（必填，中文）
2. `hosts` - 目标主机（必填）
3. `gather_facts` - 事实收集开关（必填，显式声明）
4. `become` - 权限提升（可选，但建议显式声明）
5. `vars_files` - 变量文件（推荐使用）
6. `vars` - 内联变量（可选）
7. `tasks` - 任务列表（必填）
8. `handlers` - 处理器列表（可选）

### 1.3 模块调用规范

**所有模块调用必须使用 FQCN（完全限定集合名称）**：

✅ **正确示例**：
```yaml
- name: 复制配置文件
  ansible.builtin.copy:
    src: app.conf
    dest: /etc/app.conf
```

❌ **错误示例**：
```yaml
- name: 复制配置文件
  copy:  # 缺少 FQCN
    src: app.conf
    dest: /etc/app.conf
```

**常用 FQCN 对照表**：

| 模块简称 | FQCN |
|---------|------|
| `copy`, `file`, `template` | `ansible.builtin.copy`, `ansible.builtin.file`, `ansible.builtin.template` |
| `service`, `systemd` | `ansible.builtin.service`, `ansible.builtin.systemd` |
| `user`, `group` | `ansible.builtin.user`, `ansible.builtin.group` |
| `apt`, `yum`, `package` | `ansible.builtin.apt`, `ansible.builtin.yum`, `ansible.builtin.package` |
| `shell`, `command`, `raw` | `ansible.builtin.shell`, `ansible.builtin.command`, `ansible.builtin.raw` |
| `debug`, `set_fact`, `include_tasks` | `ansible.builtin.debug`, `ansible.builtin.set_fact`, `ansible.builtin.include_tasks` |
| `docker_container`, `docker_image` | `community.docker.docker_container`, `community.docker.docker_image` |
| `k8s` | `kubernetes.core.k8s` |
| `postgresql_db`, `mysql_db` | `community.postgresql.postgresql_db`, `community.mysql.mysql_db` |

### 1.4 Check Mode 支持

关键变更任务应提供 `check_mode` 示例，用于安全预演：

```yaml
- name: 删除旧配置文件（支持 check_mode 预演）
  ansible.builtin.file:
    path: /etc/old_app.conf
    state: absent
  check_mode: true  # 仅预演，不实际执行
```

### 1.5 幂等性要求

所有任务必须具备幂等性，避免重复执行导致状态不一致：

```yaml
- name: 确保服务已启动
  ansible.builtin.service:
    name: nginx
    state: started  # 使用 started 而非 restarted，保证幂等性
    enabled: true
```

---

## 2. 变量文件规范

### 2.1 文件头部警告

**所有 `vars/example_vars.yml` 文件必须以 `⚠️` 警告开头**：

```yaml
# ⚠️ 本文件仅为示例，占位符必须使用 Ansible Vault 或环境变量替换
# ⚠️ 请勿在生产环境中直接使用这些示例值
# ⚠️ 敏感信息应使用 ansible-vault encrypt_string 加密

# 应用配置
app_name: my_application
app_port: 8080

# 数据库配置（敏感信息使用 vault_ 前缀）
database_host: localhost
database_name: app_db
database_user: app_user
database_password: "{{ vault_database_password }}"

# API 密钥（敏感信息使用 vault_ 前缀）
api_token: "{{ vault_api_token }}"
```

### 2.2 敏感信息处理

所有敏感信息（密码、Token、密钥）必须：

1. **使用 `vault_` 前缀命名**：`vault_database_password`、`vault_api_token`
2. **不允许硬编码真实值**：使用占位符或 Vault 变量引用
3. **在注释中提供加密示例**：

```yaml
# 数据库密码（使用 Ansible Vault 加密）
# 加密命令示例：
#   ansible-vault encrypt_string 'my_secret_password' --name 'vault_database_password'
database_password: "{{ vault_database_password }}"
```

### 2.3 变量分组与注释

变量应按功能分组，每组前添加中文注释：

```yaml
# ========================================
# 基础配置
# ========================================
app_name: my_application
app_version: "1.0.0"

# ========================================
# 网络配置
# ========================================
app_host: 0.0.0.0
app_port: 8080

# ========================================
# 数据库配置（敏感信息）
# ========================================
database_host: localhost
database_password: "{{ vault_database_password }}"
```

---

## 3. 文档规范

### 3.1 README.md 标准章节

每个模块的 `README.md` 必须包含以下章节（顺序固定）：

1. **模块标题** - 使用一级标题，简洁明确
2. **模块用途** - 简要说明模块功能和适用场景
3. **主要参数** - 列出关键参数及其说明
4. **返回值** - 说明模块执行后的返回信息（可选）
5. **使用情境** - 提供 3-5 个实际应用场景
6. **中文安全提示** - 安全注意事项和风险说明
7. **环境依赖** - 列出所需软件包、集合、权限
8. **常见问题** - 常见错误及解决方案
9. **最佳实践** - 推荐的使用方法和优化建议
10. **相关示例** - 指向相关 Playbook 和文档

### 3.2 中文优先原则

**所有文档内容必须以中文叙述**，英文术语仅作为括号补充：

✅ **正确示例**：
```markdown
## Docker 容器（Container）管理

使用 `community.docker.docker_container` 模块管理 Docker 容器的生命周期，
包括创建、启动、停止和删除容器。
```

❌ **错误示例**：
```markdown
## Docker Container Management

Use the `community.docker.docker_container` module to manage Docker containers.
```

### 3.3 命令注解

引用命令时，必须在下方提供中文注解：

```markdown
## 安装依赖

```bash
ansible-galaxy collection install community.docker
```

**命令说明**：安装 Docker 相关的 Ansible 集合，用于容器管理模块。
```

---

## 4. 命名规范

### 4.1 Play 名称

- **必须使用中文**
- **简洁明确**，概括整个 Play 的目的
- **以动词开头**，如"配置"、"部署"、"检查"

✅ **正确示例**：
```yaml
- name: 配置 Nginx Web 服务器
- name: 部署 Django 应用
- name: 检查磁盘空间
```

❌ **错误示例**：
```yaml
- name: Setup Nginx  # 使用英文
- name: 配置        # 过于简略
- name: 这是一个非常详细的配置Nginx和PHP-FPM以及MySQL的完整流程  # 过长
```

### 4.2 任务名称

- **必须使用中文**
- **清晰描述任务动作**
- **包含关键信息**（文件名、服务名、路径等）

✅ **正确示例**：
```yaml
- name: 复制 Nginx 主配置文件
- name: 启动并启用 Docker 服务
- name: 检查应用端口 8080 是否监听
```

### 4.3 Handler 名称

- **必须使用中文**
- **描述触发的动作**
- **与 `notify` 字段保持一致**

✅ **正确示例**：
```yaml
handlers:
  - name: 重启 Nginx 服务
    ansible.builtin.service:
      name: nginx
      state: restarted

tasks:
  - name: 更新 Nginx 配置
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: 重启 Nginx 服务
```

### 4.4 多语言兼容（可选）

如需兼容旧引用，可使用 `listen` 提供中英文别名：

```yaml
handlers:
  - name: 重启 Nginx 服务
    ansible.builtin.service:
      name: nginx
      state: restarted
    listen:
      - "重启 Nginx 服务"
      - "restart nginx"  # 兼容旧代码
```

---

## 5. 安全规范

### 5.1 敏感信息保护

**所有涉及密码、Token、证书、密钥的任务必须设置 `no_log: true`**：

```yaml
- name: 创建数据库用户（敏感操作）
  community.postgresql.postgresql_user:
    name: "{{ database_user }}"
    password: "{{ vault_database_password }}"
    state: present
  no_log: true  # 防止密码泄露到日志
```

### 5.2 条件性日志控制

如需调试，可通过变量开关控制：

```yaml
- name: 创建数据库用户（敏感操作）
  community.postgresql.postgresql_user:
    name: "{{ database_user }}"
    password: "{{ vault_database_password }}"
    state: present
  no_log: "{{ not enable_sensitive_logging | default(true) }}"
```

### 5.3 Shell 命令安全

使用 `shell`/`command`/`raw` 模块时，必须：

1. **优先使用 `command` 而非 `shell`**（避免 Shell 注入）
2. **使用 `set -e` 确保错误中断**（如必须使用 `shell`）
3. **添加注释说明安全考虑**

✅ **正确示例**：
```yaml
- name: 执行备份脚本（使用 set -e 确保错误中断）
  ansible.builtin.shell: |
    set -e
    backup_dir="/var/backups/$(date +%Y%m%d)"
    mkdir -p "$backup_dir"
    tar -czf "$backup_dir/app.tar.gz" /opt/app
  args:
    executable: /bin/bash
```

### 5.4 权限最小化

只在必要时使用 `become`，避免全局提权：

✅ **正确示例**：
```yaml
- name: 安装软件包（需要 root 权限）
  ansible.builtin.apt:
    name: nginx
    state: present
  become: true  # 仅此任务提权

- name: 创建应用配置文件（普通用户权限）
  ansible.builtin.copy:
    src: app.conf
    dest: ~/app.conf
  # 无需 become
```

---

## 6. 测试规范

### 6.1 必须通过的检查项

每个目录的 `pytest` 测试必须校验：

1. ✅ **README 章节齐全**
2. ✅ **Playbook 含 `gather_facts` 声明**
3. ✅ **Playbook 含 `check_mode` 示例**（至少一个任务）
4. ✅ **vars 文件含 `⚠️` 警告标识**
5. ✅ **模块调用使用 FQCN**
6. ✅ **任务和 Handler 名称中文化**

### 6.2 通用辅助函数

推荐在测试中使用以下辅助函数（减少重复代码）：

```python
def assert_has_warning(vars_file_path: Path):
    """检查变量文件是否包含 ⚠️ 警告"""
    content = vars_file_path.read_text(encoding='utf-8')
    assert '⚠️' in content[:500], f"{vars_file_path} 缺少 ⚠️ 警告标识"

def assert_has_gather_facts(playbook_path: Path):
    """检查 Playbook 是否声明 gather_facts"""
    content = playbook_path.read_text(encoding='utf-8')
    assert 'gather_facts' in content, f"{playbook_path} 缺少 gather_facts 声明"
```

---

## 7. 元数据规范

### 7.1 新增模块流程

添加新模块时，必须同步更新以下文件：

1. **创建目录结构**：
   ```
   category/module_name/
   ├── README.md
   ├── playbook.yml
   ├── vars/
   │   └── example_vars.yml
   └── templates/  # 如有需要
   ```

2. **更新 `metadata/modules.yaml`**：
   ```yaml
   category:
     topics:
       - id: module_name
         name: 模块中文名称
         doc: category/module_name/README.md
         example: category/module_name/playbook.yml
         summary: "一句话功能说明"
   ```

3. **更新根 `README.md`**：
   - 在对应分类的表格中添加模块链接

4. **运行生成脚本校验**（如有）：
   ```bash
   python3 tools/audit_check.py
   ```

### 7.2 ID 命名规则

- **使用 `snake_case` 命名**
- **与目录名保持一致**
- **避免使用前缀**（如 `storage_mount` 应简化为 `mount`）

✅ **正确示例**：
```yaml
storage:
  topics:
    - id: mount        # 目录: storage/mount
    - id: lvol         # 目录: storage/lvol
```

❌ **错误示例**：
```yaml
storage:
  topics:
    - id: storage_mount      # 冗余前缀
    - id: storage-lvol       # 使用连字符而非下划线
```

---

## 附录：快速检查清单

提交代码前，请确保：

- [ ] Playbook 显式声明 `gather_facts`
- [ ] 所有模块使用 FQCN
- [ ] Play/Task/Handler 名称使用中文
- [ ] `vars/example_vars.yml` 包含 `⚠️` 警告
- [ ] 敏感信息使用 `vault_` 前缀
- [ ] 涉及密码/Token 的任务设置 `no_log: true`
- [ ] README.md 包含标准章节且全中文
- [ ] 元数据已同步更新
- [ ] 测试全部通过

---

**版本**: 1.0  
**最后更新**: 2024-11-20  
**维护者**: ansible_playbook 项目团队
