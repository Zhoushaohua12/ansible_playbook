# 文件操作模块实践指南

## 章节目标

文件操作是 Ansible 自动化的基础能力，本章节覆盖从基础文件管理到高级同步操作的完整场景：
- **文件传输与分发**：将配置文件、脚本、静态资源从控制节点分发到远程主机
- **动态配置生成**：使用 Jinja2 模板根据主机变量生成个性化配置文件
- **精确配置修改**：在不替换整个文件的情况下修改配置项或添加配置行
- **文件状态检查**：获取文件属性、权限、大小、修改时间等元数据
- **批量文件管理**：创建、删除、设置权限、符号链接等基础文件系统操作
- **文件查找与清理**：根据条件查找文件并批量处理（如清理日志、临时文件）
- **高效目录同步**：使用 rsync 实现快速增量同步和备份

## 适用场景

### 应用配置管理
- Web 服务器虚拟主机配置（Nginx/Apache）
- 应用配置文件分发（数据库连接、API 密钥、环境变量）
- SSL 证书和密钥文件部署
- 日志轮转和清理策略配置

### 系统运维场景
- 批量创建目录结构和文件权限设置
- 配置文件备份和恢复
- 定时任务脚本分发
- 系统配置文件修改（sshd_config、sysctl.conf）

### 开发与部署
- 静态资源发布（HTML、CSS、JS、图片）
- 应用代码包传输和解压
- 配置文件模板渲染（多环境、多区域）
- 版本控制文件同步

## 模块列表

| 模块 | 用途 | 典型场景 | 幂等性 |
|------|------|----------|--------|
| **copy** | 复制文件到远程主机 | 分发配置文件、脚本、证书 | ✓ |
| **template** | 渲染 Jinja2 模板并部署 | 生成动态配置（多环境适配） | ✓ |
| **lineinfile** | 确保文件中存在或修改特定行 | 修改配置项、添加环境变量 | ✓ |
| **stat** | 获取文件/目录状态信息 | 检查文件是否存在、获取权限 | ✓（只读） |
| **file** | 管理文件/目录/符号链接 | 创建目录、设置权限、删除文件 | ✓ |
| **find** | 按条件查找文件 | 清理旧日志、查找大文件 | ✓（只读） |
| **synchronize** | 使用 rsync 同步目录 | 增量备份、代码部署、镜像同步 | ✓ |

## 学习路线指引

### 初学者路线（必修）
1. **file** → 掌握基础文件系统操作（创建目录、设置权限、符号链接）
2. **copy** → 学习静态文件分发和简单配置部署
3. **stat** → 了解如何检查文件状态并在任务中使用条件判断
4. **lineinfile** → 掌握配置文件的精确修改技巧

### 进阶路线（推荐）
5. **template** → 学习 Jinja2 模板语法，实现配置文件的动态生成
6. **find** → 掌握文件查找和批量处理模式
7. **synchronize** → 学习高效目录同步和备份策略

### 实战项目建议
- **项目 1：Web 应用部署**  
  结合 `file` 创建目录 → `copy` 分发静态资源 → `template` 生成 Nginx 配置 → `lineinfile` 修改系统参数
  
- **项目 2：配置管理自动化**  
  使用 `stat` 检查配置文件 → `lineinfile` 修改参数 → `template` 渲染完整配置 → `copy` 备份原始文件
  
- **项目 3：日志清理与备份**  
  使用 `find` 查找旧日志 → `file` 删除过期文件 → `synchronize` 增量备份到远程存储

## 常见陷阱与最佳实践

### 文件编码问题
**陷阱**：不同系统的默认编码不同（Linux 通常 UTF-8，Windows 可能 GBK），导致中文乱码。

**最佳实践**：
```yaml
# copy 模块明确指定编码
- name: 复制包含中文的配置文件
  ansible.builtin.copy:
    src: files/app.conf
    dest: /etc/app/app.conf
    # 源文件和目标文件都使用 UTF-8 编码
```

```yaml
# template 模块使用 UTF-8 编码
- name: 渲染包含中文注释的配置模板
  ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    # 模板文件需保存为 UTF-8 编码
```

**提示**：在 Windows 控制节点上，确保文本编辑器保存文件为 UTF-8（无 BOM）编码。

### 幂等性验证
**陷阱**：频繁执行导致不必要的变更通知（触发 handler 重启服务）。

**最佳实践**：
```yaml
# 使用 checksum 确保仅在文件实际变化时触发
- name: 复制配置文件（仅变化时触发重启）
  ansible.builtin.copy:
    src: files/app.conf
    dest: /etc/app/app.conf
    mode: '0644'
  notify: 重启应用服务

# template 默认使用 checksum 比较
- name: 渲染配置模板（仅变化时触发重启）
  ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: 重新加载 Nginx
```

**验证技巧**：
```bash
# 第一次执行应该 changed
ansible-playbook playbook.yml

# 第二次执行应该 ok（未变化）
ansible-playbook playbook.yml
```

### 备份策略
**陷阱**：直接覆盖配置文件后无法回滚，导致服务异常。

**最佳实践**：
```yaml
# 自动备份原文件
- name: 修改配置文件（自动备份）
  ansible.builtin.lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^PermitRootLogin'
    line: 'PermitRootLogin no'
    backup: yes  # 自动创建 .backup 文件
  notify: 重启 SSH 服务

# 手动备份到指定位置
- name: 备份原配置文件
  ansible.builtin.copy:
    src: /etc/nginx/nginx.conf
    dest: /etc/nginx/nginx.conf.backup.{{ ansible_date_time.epoch }}
    remote_src: yes  # 远程主机本地复制

- name: 部署新配置文件
  ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
```

### 权限与所有者管理
**陷阱**：文件权限不正确导致应用无法读取或存在安全风险。

**最佳实践**：
```yaml
# 明确指定文件权限和所有者
- name: 部署应用配置（设置正确权限）
  ansible.builtin.copy:
    src: files/database.yml
    dest: /opt/app/config/database.yml
    owner: appuser
    group: appgroup
    mode: '0640'  # 仅所有者和组可读，避免泄露敏感信息

# 证书文件应使用更严格的权限
- name: 部署 SSL 私钥
  ansible.builtin.copy:
    src: files/ssl/private.key
    dest: /etc/ssl/private/app.key
    owner: root
    group: ssl-cert
    mode: '0440'  # 仅 root 和 ssl-cert 组可读
```

### synchronize 模块陷阱
**陷阱**：`synchronize` 使用 rsync，需要在控制节点和目标主机都安装 rsync。

**最佳实践**：
```yaml
# 检查 rsync 是否安装
- name: 确保 rsync 已安装
  ansible.builtin.package:
    name: rsync
    state: present

# 使用 synchronize 同步目录
- name: 同步应用代码到远程主机
  ansible.posix.synchronize:
    src: /local/app/dist/
    dest: /var/www/html/
    delete: yes  # 删除目标目录中多余文件
    rsync_opts:
      - "--exclude=.git"
      - "--exclude=node_modules"
```

**注意**：`synchronize` 在使用 `delegate_to` 时行为会改变，建议阅读模块文档。

## 快速开始

```bash
# 1. 进入模块目录
cd files/copy  # 或其他模块目录

# 2. 查看模块文档
cat README.md

# 3. 检查示例变量
cat vars/example_vars.yml

# 4. 语法检查
ansible-playbook playbook.yml --syntax-check

# 5. Dry-Run 预览（不实际执行）
ansible-playbook playbook.yml --check

# 6. 实际执行
ansible-playbook playbook.yml
```

## 调试技巧

### 查看文件内容变化
```bash
# 查看 template 渲染后的实际内容（不部署）
ansible-playbook playbook.yml --check --diff

# --diff 会显示文件内容差异
```

### 验证文件权限
```bash
# 检查远程文件权限
ansible all -m ansible.builtin.stat -a "path=/etc/app/app.conf"

# 检查文件内容
ansible all -m ansible.builtin.shell -a "cat /etc/app/app.conf"
```

### 测试 Jinja2 模板
```bash
# 在本地测试模板渲染（需要安装 jinja2-cli）
pip install jinja2-cli

# 渲染模板查看结果
jinja2 templates/nginx.conf.j2 vars/example_vars.yml
```

## 相关链接

- [copy 模块](copy/README.md) - 静态文件复制和分发
- [template 模块](template/README.md) - Jinja2 模板渲染和配置生成
- [lineinfile 模块](lineinfile/README.md) - 配置文件行级精确修改
- [stat 模块](stat/README.md) - 文件状态检查和条件判断
- [file 模块](file/README.md) - 文件系统基础操作
- [find 模块](find/README.md) - 文件查找和批量处理
- [synchronize 模块](synchronize/README.md) - 目录增量同步和备份

## 参考资源

- [Ansible 官方文档 - File Modules](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/index.html#plugins-in-ansible-builtin)
- [Jinja2 模板语法](https://jinja.palletsprojects.com/en/latest/templates/)
- [rsync 使用指南](https://rsync.samba.org/documentation.html)
