# unarchive 模块使用指南

## 模块用途
`ansible.builtin.unarchive` 模块用于解压缩文件到远程主机，支持 tar、zip、gz、bz2、xz 等多种压缩格式。它是应用部署、软件安装、配置文件分发等场景的核心模块。

## 主要参数

### 基础参数
- `src`：压缩文件路径（控制节点本地或远程主机）
- `dest`：解压目标目录 - 必需参数
- `remote_src`：源文件是否在远程主机（默认 false，从控制节点传输）

### 解压控制
- `creates`：指定文件存在时跳过解压（幂等性控制）
- `extra_opts`：传递给解压命令的额外选项
- `exclude`：排除特定文件或目录
- `include`：仅包含特定文件或目录

### 权限和安全
- `owner`：设置解压文件的所有者
- `group`：设置解压文件的所属组
- `mode`：设置解压文件的权限
- `keep_newer`：保留目标目录中更新的文件（默认 false）

## 返回值
- `changed`：文件是否被解压或修改
- `dest`：目标目录路径
- `src`：源压缩文件路径
- `gid`：解压文件的组 ID
- `group`：解压文件的所属组
- `mode`：解压文件的权限
- `owner`：解压文件的所有者
- `size`：解压文件的总大小
- `uid`：解压文件的用户 ID

## 使用场景

### 应用部署
将应用代码包、静态资源、配置文件等压缩包解压到部署目录。

### 软件安装
解压软件安装包到指定目录，适用于二进制分发软件。

### 配置文件分发
批量分发配置文件模板，支持多环境配置管理。

### 数据恢复
解压备份文件恢复系统配置或用户数据。

## 最佳实践

### 基础应用部署
```yaml
# 从控制节点传输并解压应用包
- name: 部署应用代码包
  ansible.builtin.unarchive:
    src: files/app-v1.0.0.tar.gz
    dest: /opt/app/
    owner: appuser
    group: appgroup
    mode: '0755'
    creates: /opt/app/index.html  # 幂等性控制
```

### 远程压缩包解压
```yaml
# 解压远程主机上的压缩包
- name: 解压远程备份文件
  ansible.builtin.unarchive:
    src: /backup/configs.tar.gz
    dest: /etc/app/
    remote_src: true  # 源文件在远程主机
    extra_opts:
      - "--exclude=.git"
      - "--strip-components=1"  # 去除顶层目录
```

### 条件性解压
```yaml
# 仅在特定文件不存在时解压
- name: 解压配置文件（如果不存在）
  ansible.builtin.unarchive:
    src: files/config.tar.gz
    dest: /etc/app/
    creates: /etc/app/config.ini
```

### 安全解压
```yaml
# 解压后设置安全权限
- name: 安全解压应用包
  ansible.builtin.unarchive:
    src: files/secure_app.tar.gz
    dest: /opt/secure_app/
    owner: root
    group: appgroup
    mode: '0750'
    extra_opts:
      - "--no-same-owner"  # 使用指定 owner 而非压缩包中的 owner
```

## 高级用法

### 排除特定文件
```yaml
# 解压时排除特定文件和目录
- name: 解压应用代码（排除开发文件）
  ansible.builtin.unarchive:
    src: files/app_source.tar.gz
    dest: /var/www/html/
    exclude:
      - "*.log"
      - "tmp/"
      - ".git*"
      - "node_modules/"
    owner: www-data
    group: www-data
```

### 使用额外选项
```yaml
# 使用 tar 的额外选项
- name: 解压并覆盖文件
  ansible.builtin.unarchive:
    src: files/update.tar.gz
    dest: /opt/app/
    extra_opts:
      - "--overwrite"  # 覆盖现有文件
      - "--strip-components=1"  # 去除第一层目录
      - "--no-same-permissions"  # 不保持压缩包权限
```

### 版本化部署
```yaml
# 版本化应用部署
- name: 创建版本目录
  ansible.builtin.file:
    path: "/opt/app/releases/{{ app_version }}"
    state: directory
    mode: '0755'

- name: 解压应用到版本目录
  ansible.builtin.unarchive:
    src: "files/app-{{ app_version }}.tar.gz"
    dest: "/opt/app/releases/{{ app_version }}/"
    creates: "/opt/app/releases/{{ app_version }}/index.html"

- name: 更新符号链接到新版本
  ansible.builtin.file:
    src: "/opt/app/releases/{{ app_version }}"
    dest: /opt/app/current
    state: link
```

## 安全注意事项

### 校验压缩包
```yaml
# 先校验再解压
- name: 校验压缩包完整性
  ansible.builtin.stat:
    path: /tmp/app.tar.gz
  register: archive_check

- name: 解压应用包
  ansible.builtin.unarchive:
    src: /tmp/app.tar.gz
    dest: /opt/app/
  when: archive_check.stat.exists and archive_check.stat.size > 0
```

### 安全权限设置
```yaml
# 解压敏感配置文件
- name: 解压配置文件（安全权限）
  ansible.builtin.unarchive:
    src: files/configs.tar.gz
    dest: /etc/app/
    owner: root
    group: appgroup
    mode: '0640'  # 仅所有者和组可读
  no_log: true  # 避免日志中暴露敏感信息
```

### 路径遍历防护
```yaml
# 防止路径遍历攻击
- name: 安全解压（限制路径）
  ansible.builtin.unarchive:
    src: files/user_upload.tar.gz
    dest: /tmp/safe_extract/
    extra_opts:
      - "--no-same-owner"
      - "--no-same-permissions"
    # 验证解压后的文件路径
```

## 常见问题

### 权限问题
**问题**：解压后文件权限不正确。

**解决方案**：
```yaml
- name: 解压并设置权限
  ansible.builtin.unarchive:
    src: files/app.tar.gz
    dest: /opt/app/
    owner: appuser
    group: appgroup
    mode: '0755'
    extra_opts:
      - "--no-same-permissions"  # 不使用压缩包中的权限
```

### 磁盘空间不足
**问题**：解压时磁盘空间不足。

**解决方案**：
```yaml
# 检查磁盘空间
- name: 检查目标目录磁盘空间
  ansible.builtin.command: df -h /opt/app/
  register: disk_space

- name: 解压应用包
  ansible.builtin.unarchive:
    src: files/app.tar.gz
    dest: /opt/app/
  when: "'10G' in disk_space.stdout"
```

### 压缩格式不支持
**问题**：压缩格式不被支持。

**解决方案**：
```yaml
# 使用命令行解压特殊格式
- name: 解压 7z 格式文件
  ansible.builtin.command: 7z x archive.7z -o/opt/app/
  args:
    creates: /opt/app/deployed_marker
```

## 测试步骤

1. **准备压缩包**
```bash
# 创建示例压缩包
tar -czf app.tar.gz app/
```

2. **测试解压**
```bash
ansible-playbook playbook.yml --check  # 预览模式
ansible-playbook playbook.yml         # 实际执行
```

3. **验证结果**
```bash
# 检查解压结果
ls -la /opt/app/
find /opt/app/ -type f -exec ls -la {} \;
```

## 依赖说明

### 系统依赖
- `tar`：处理 tar 格式压缩包
- `unzip`：处理 zip 格式压缩包（可选）
- `gzip`：处理 gz 压缩格式
- `bzip2`：处理 bz2 压缩格式（可选）
- `xz`：处理 xz 压缩格式（可选）

### Python 依赖
- 无额外 Python 依赖

### 网络要求
- 从控制节点传输时需要足够的网络带宽
- 远程主机需要足够的磁盘空间

## 相关示例

- [archive 模块](../archive/README.md) - 创建压缩文件
- [copy 模块](../copy/README.md) - 文件复制
- [fetch 模块](../fetch/README.md) - 文件获取
- [synchronize 模块](../synchronize/README.md) - 目录同步

## 参考资源

- [Ansible 官方文档 - unarchive 模块](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/unarchive_module.html)
- [tar 命令手册](https://man7.org/linux/man-pages/man1/tar.1.html)