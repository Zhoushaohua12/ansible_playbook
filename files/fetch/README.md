# fetch 模块使用指南

## 模块用途
`ansible.builtin.fetch` 模块用于从远程主机获取文件到控制节点，与 copy 模块方向相反。它主要用于收集日志文件、配置文件备份、系统信息收集等场景。

## 主要参数

### 基础参数
- `src`：远程主机上的源文件路径 - 必需参数
- `dest`：控制节点上的目标目录路径 - 必需参数
- `flat`：是否扁平化存储（默认 false，保持目录结构）
- `fail_on_missing`：源文件不存在时是否失败（默认 true）

### 校验参数
- `validate_checksum`：是否校验文件校验和（默认 true）

### 权限控制
- `mode`：设置目标文件权限

## 返回值
- `changed`：文件是否被获取
- `dest`：目标文件的完整路径
- `checksum`：文件的 SHA1 校验和
- `md5sum`：文件的 MD5 校验和
- `remote_md5sum`：远程文件 MD5 校验和
- `remote_checksum`：远程文件 SHA1 校验和
- `size`：文件大小（字节）

## 使用场景

### 日志文件收集
从多台服务器收集应用日志、系统日志、错误日志等文件到控制节点进行集中分析。

### 配置文件备份
定期获取关键配置文件（如 nginx.conf、数据库配置）作为备份，便于故障恢复。

### 系统信息收集
收集系统信息文件（如 /etc/passwd、/etc/hosts、进程列表）用于审计和监控。

### 证书和密钥备份
安全地获取 SSL 证书、SSH 密钥等重要文件进行集中备份管理。

## 最佳实践

### 扁平化存储
```yaml
# 扁平化存储：所有文件保存在同一目录
- name: 收集服务器日志文件（扁平化）
  ansible.builtin.fetch:
    src: "/var/log/app/{{ item }}"
    dest: "/tmp/collected_logs/"
    flat: true  # 不保持远程目录结构
  loop:
    - "access.log"
    - "error.log"
    - "debug.log"
```

### 保持目录结构
```yaml
# 保持目录结构：按主机名组织文件
- name: 收集配置文件（保持结构）
  ansible.builtin.fetch:
    src: "/etc/nginx/nginx.conf"
    dest: "/backup/configs/"
    # flat: false（默认），文件将保存为 /backup/configs/hostname/etc/nginx/nginx.conf
```

### 校验文件完整性
```yaml
# 启用校验和验证确保文件完整性
- name: 安全获取关键配置文件
  ansible.builtin.fetch:
    src: "/etc/ssh/sshd_config"
    dest: "/backup/ssh_configs/"
    validate_checksum: true  # 验证文件传输完整性
    fail_on_missing: true   # 文件不存在时失败
```

### 条件性获取
```yaml
# 仅在文件存在且较新时获取
- name: 获取更新的日志文件
  ansible.builtin.fetch:
    src: "/var/log/app/application.log"
    dest: "/logs/{{ inventory_hostname }}/"
    flat: true
  when: app_log_check.stat.exists and app_log_check.stat.mtime > ansible_date_time.epoch - 3600
```

## 安全注意事项

### 敏感文件处理
```yaml
# 获取敏感文件时使用 no_log 保护
- name: 收集数据库配置（敏感信息）
  ansible.builtin.fetch:
    src: "/etc/mysql/my.cnf"
    dest: "/secure_backup/mysql_configs/"
    mode: '0600'  # 限制文件权限
  no_log: true    # 避免在日志中暴露敏感信息
```

### 磁盘空间管理
```yaml
# 检查控制节点磁盘空间
- name: 检查本地磁盘空间
  ansible.builtin.command: df -h /tmp
  register: local_disk_space
  delegate_to: localhost
  run_once: true

- name: 获取大型日志文件
  ansible.builtin.fetch:
    src: "/var/log/large_app.log"
    dest: "/tmp/collected_logs/"
    flat: true
  when: "'10G' in local_disk_space.stdout"  # 确保有足够空间
```

## 常见问题

### 文件权限问题
**问题**：获取的文件权限不正确，导致无法访问。

**解决方案**：
```yaml
- name: 获取文件并设置正确权限
  ansible.builtin.fetch:
    src: "/var/log/app.log"
    dest: "/collected_logs/"
    mode: '0644'  # 明确设置权限
```

### 路径冲突
**问题**：多个主机的同名文件覆盖。

**解决方案**：
```yaml
# 使用 inventory_hostname 区分文件
- name: 按主机名收集日志
  ansible.builtin.fetch:
    src: "/var/log/app.log"
    dest: "/logs/{{ inventory_hostname }}_app.log"
    flat: true
```

### 大文件传输
**问题**：大文件传输超时或占用过多带宽。

**解决方案**：
```yaml
# 先压缩再获取
- name: 压缩大日志文件
  ansible.builtin.shell: "tar -czf /tmp/{{ inventory_hostname }}_logs.tar.gz /var/log/app/"

- name: 获取压缩后的日志文件
  ansible.builtin.fetch:
    src: "/tmp/{{ inventory_hostname }}_logs.tar.gz"
    dest: "/collected_logs/"
    flat: true
```

## 测试步骤

1. **准备测试环境**
```bash
# 在远程主机创建测试文件
ssh remote-host "mkdir -p /tmp/test_fetch && echo 'test content' > /tmp/test_fetch/test.log"
```

2. **执行 fetch 任务**
```bash
ansible-playbook playbook.yml --check  # 预览模式
ansible-playbook playbook.yml         # 实际执行
```

3. **验证结果**
```bash
# 检查控制节点上的文件
ls -la /tmp/collected_logs/
cat /tmp/collected_logs/hostname/tmp/test_fetch/test.log
```

## 依赖说明

### 系统依赖
- 无额外系统依赖，使用 Ansible 内置模块

### Python 依赖
- 无额外 Python 依赖

### 网络要求
- SSH 连接正常
- 控制节点有足够的磁盘空间存储获取的文件

## 相关示例

- [copy 模块](../copy/README.md) - 文件复制到远程主机
- [synchronize 模块](../synchronize/README.md) - 双向文件同步
- [unarchive 模块](../unarchive/README.md) - 解压缩文件
- [archive 模块](../archive/README.md) - 压缩文件

## 参考资源

- [Ansible 官方文档 - fetch 模块](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/fetch_module.html)
- [Ansible 最佳实践 - 文件管理](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)