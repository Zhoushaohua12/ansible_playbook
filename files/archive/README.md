# archive 模块使用指南

## 模块用途
`ansible.builtin.archive` 模块用于在远程主机上创建文件和目录的压缩归档。它支持多种压缩格式，适用于应用部署备份、日志归档、配置文件打包等场景。

## 主要参数

### 基础参数
- `path`：要归档的文件或目录路径 - 必需参数
- `dest`：归档文件的输出路径 - 必需参数
- `format`：归档格式（默认 gz，支持：zip、tar、tar.gz、tar.bz2、tar.xz）

### 归档控制
- `remove`：归档成功后删除源文件（默认 false，危险操作）
- `force`：目标文件存在时是否强制覆盖（默认 true）

### 排除选项
- `exclude_path`：要排除的文件或目录路径列表

## 返回值
- `changed`：归档文件是否被创建或修改
- `dest`：归档文件的完整路径
- `archived`：已归档的文件列表
- `state`：归档文件的状态（file、absent、directory）
- `size`：归档文件大小（字节）
- `uid`：归档文件的用户 ID
- `gid`：归档文件的组 ID

## 使用场景

### 应用代码备份
将应用代码目录打包备份，便于版本回滚和灾难恢复。

### 日志文件归档
定期将历史日志文件打包压缩，节省磁盘空间并便于长期存储。

### 配置文件打包
将配置文件和目录打包，用于环境迁移或备份。

### 数据归档
将业务数据文件打包归档，满足数据保留和合规要求。

## 最佳实践

### 基础归档操作
```yaml
# 创建目录的 gzip 压缩归档
- name: 备份应用代码目录
  ansible.builtin.archive:
    path: /opt/app/
    dest: /backup/app_backup_{{ ansible_date_time.epoch }}.tar.gz
    format: tar.gz
    # 中文提示：使用时间戳避免文件名冲突
```

### 排除不需要的文件
```yaml
# 归档时排除临时文件和日志
- name: 创建应用归档（排除临时文件）
  ansible.builtin.archive:
    path: /opt/app/
    dest: /backup/app_clean.tar.gz
    format: tar.gz
    exclude_path:
      - /opt/app/tmp/
      - /opt/app/logs/*.log
      - /opt/app/cache/
      - /opt/app/node_modules/
    # 中文提示：exclude_path 排除不需要归档的文件和目录
```

### 多格式归档
```yaml
# 创建不同格式的归档文件
- name: 创建 ZIP 格式归档（Windows 兼容）
  ansible.builtin.archive:
    path: /opt/app/
    dest: /backup/app_backup.zip
    format: zip

- name: 创建高压缩率归档
  ansible.builtin.archive:
    path: /opt/app/
    dest: /backup/app_backup.tar.bz2
    format: tar.bz2
```

### 多文件/目录归档
```yaml
# 同时归档多个目录
- name: 归档多个重要目录
  ansible.builtin.archive:
    path:
      - /etc/nginx/
      - /etc/ssl/
      - /var/log/nginx/
    dest: /backup/nginx_config_backup.tar.gz
    format: tar.gz
    # 中文提示：path 参数支持列表形式同时归档多个路径
```

## 高级用法

### 条件性归档
```yaml
# 仅在目录存在且文件数超过阈值时归档
- name: 检查目录文件数量
  ansible.builtin.find:
    paths: /var/log/app/
    file_type: file
  register: log_files

- name: 归档日志文件（文件数超过 100 时）
  ansible.builtin.archive:
    path: /var/log/app/
    dest: /backup/logs_{{ ansible_date_time.epoch }}.tar.gz
    format: tar.gz
  when: log_files.files | length > 100
```

### 安全归档（带校验）
```yaml
# 创建归档并校验完整性
- name: 安全归档配置文件
  ansible.builtin.archive:
    path: /etc/app/
    dest: /backup/config_{{ ansible_date_time.epoch }}.tar.gz
    format: tar.gz
    owner: root
    group: backup
    mode: '0640'

- name: 校验归档文件完整性
  ansible.builtin.stat:
    path: /backup/config_{{ ansible_date_time.epoch }}.tar.gz
  register: archive_stat

- name: 显示归档信息
  ansible.builtin.debug:
    msg:
      - "归档文件: {{ archive_stat.stat.path }}"
      - "文件大小: {{ archive_stat.stat.size }} 字节"
      - "创建时间: {{ archive_stat.stat.mtime }}"
```

### 版本化归档
```yaml
# 版本化归档管理
- name: 创建版本化应用归档
  ansible.builtin.archive:
    path: /opt/app/
    dest: /backup/releases/app_{{ app_version }}_{{ ansible_date_time.epoch }}.tar.gz
    format: tar.gz
    exclude_path:
      - /opt/app/tmp/
      - /opt/app/logs/

- name: 清理旧版本归档（保留最近 5 个）
  ansible.builtin.shell: |
    cd /backup/releases/
    ls -t app_*.tar.gz | tail -n +6 | xargs -r rm
  # 中文提示：保留最近 5 个版本，删除更旧的归档
```

## 安全注意事项

### ⚠️ remove 参数的危险性
```yaml
# ❌ 危险操作：归档后删除源文件
- name: 危险：归档后删除源文件
  ansible.builtin.archive:
    path: /important/data/
    dest: /backup/data.tar.gz
    remove: true  # ⚠️ 会删除原始数据！

# ✅ 安全操作：先备份再删除
- name: 安全：先创建归档备份
  ansible.builtin.archive:
    path: /important/data/
    dest: /backup/data_{{ ansible_date_time.epoch }}.tar.gz
    format: tar.gz

- name: 验证归档完整性后再删除源文件
  ansible.builtin.stat:
    path: /backup/data_{{ ansible_date_time.epoch }}.tar.gz
  register: archive_check

- name: 删除源文件（仅在归档成功后）
  ansible.builtin.file:
    path: /important/data/
    state: absent
  when: archive_check.stat.exists and archive_check.stat.size > 0
  # 中文提示：先验证归档完整性，再安全删除源文件
```

### 路径安全
```yaml
# 避免路径遍历攻击
- name: 安全归档（验证路径）
  ansible.builtin.archive:
    path: "{{ validated_path }}"
    dest: /backup/safe_archive.tar.gz
  vars:
    validated_path: "{{ user_input_path if user_input_path.startswith('/opt/app/') else '/opt/app/' }}"
```

### 权限控制
```yaml
# 设置安全的归档文件权限
- name: 创建安全的配置归档
  ansible.builtin.archive:
    path: /etc/app/
    dest: /backup/config.tar.gz
    owner: root
    group: backup
    mode: '0640'  # 仅 root 和 backup 组可读
  become: true
```

## 常见问题

### 磁盘空间不足
**问题**：归档过程中磁盘空间不足。

**解决方案**：
```yaml
# 检查磁盘空间
- name: 检查目标目录磁盘空间
  ansible.builtin.command: df -h /backup/
  register: disk_space

- name: 仅在有足够空间时创建归档
  ansible.builtin.archive:
    path: /opt/app/
    dest: /backup/app.tar.gz
  when: "'10G' in disk_space.stdout"
```

### 权限问题
**问题**：无法访问某些文件或目录。

**解决方案**：
```yaml
# 使用 become 提升权限
- name: 归档系统配置文件
  ansible.builtin.archive:
    path: /etc/systemd/
    dest: /backup/systemd.tar.gz
  become: true
```

### 归档格式不支持
**问题**：目标系统不支持特定的压缩格式。

**解决方案**：
```yaml
# 检查并安装必要的工具
- name: 确保压缩工具已安装
  ansible.builtin.package:
    name:
      - tar
      - gzip
      - bzip2
      - zip
    state: present

- name: 创建兼容的归档格式
  ansible.builtin.archive:
    path: /opt/app/
    dest: /backup/app.tar.gz
    format: tar.gz  # 使用最通用的格式
```

## 测试步骤

1. **准备测试环境**
```bash
# 创建测试文件和目录
mkdir -p /tmp/archive_test/{config,logs,temp}
echo "config data" > /tmp/archive_test/config/app.conf
echo "log data" > /tmp/archive_test/logs/app.log
echo "temp data" > /tmp/archive_test/temp/cache.tmp
```

2. **执行归档任务**
```bash
ansible-playbook playbook.yml --check  # 预览模式
ansible-playbook playbook.yml         # 实际执行
```

3. **验证归档结果**
```bash
# 检查归档文件
ls -la /tmp/archive_result.tar.gz

# 验证归档内容
tar -tzf /tmp/archive_result.tar.gz

# 测试解压
tar -xzf /tmp/archive_result.tar.gz -C /tmp/test_extract/
```

## 依赖说明

### 系统依赖
- `tar`：处理 tar 格式归档
- `gzip`：处理 gz 压缩格式
- `bzip2`：处理 bz2 压缩格式（可选）
- `xz`：处理 xz 压缩格式（可选）
- `zip`：处理 zip 格式（可选）

### Python 依赖
- 无额外 Python 依赖

### 磁盘空间要求
- 源文件大小的 1.1-2 倍空间（取决于压缩格式和文件类型）

## 相关示例

- [unarchive 模块](../unarchive/README.md) - 解压缩文件
- [copy 模块](../copy/README.md) - 文件复制
- [fetch 模块](../fetch/README.md) - 文件获取
- [synchronize 模块](../synchronize/README.md) - 目录同步

## 参考资源

- [Ansible 官方文档 - archive 模块](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/archive_module.html)
- [tar 命令手册](https://man7.org/linux/man-pages/man1/tar.1.html)
- [压缩格式对比](https://en.wikipedia.org/wiki/Comparison_of_file_archivers)