# replace 模块使用指南

## 模块用途
`ansible.builtin.replace` 模块用于根据正则表达式替换文件中的内容，支持多行替换、备份文件、验证替换结果等功能。适用于配置文件修改、日志处理、批量文本替换等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `path` | str | 目标文件路径（必需） | `/etc/hosts`、`/etc/nginx/nginx.conf` 等 |
| `regexp` | str | 正则表达式模式（必需） | `^(#\s*)?Listen\s+80`、`password\s*=\s*.*` 等 |
| `replace` | str | 替换字符串（必需） | `Listen 8080`、`password = "{{ new_password }}"` 等 |
| `backup` | bool | 是否备份原文件（默认 false） | true、false |
| `before` | str | 在此内容之前替换（可选） | `</VirtualHost>`、`</configuration>` 等 |
| `after` | str | 在此内容之后替换（可选） | `<VirtualHost`、`<configuration>` 等 |
| `mode` | str | 文件权限模式（可选） | `0644`、`0755` 等 |
| `validate` | str | 验证命令（可选） | `nginx -t %s`、`httpd -t %s` 等 |
| `encoding` | str | 文件编码（默认 utf-8） | `utf-8`、`gbk` 等 |
| `selevel` | str | SELinux 安全级别（可选） | `s0`、`s0:c123.c456` 等 |
| `serole` | str | SELinux 角色（可选） | `object_r`、`staff_object_r` 等 |
| `setype` | str | SELinux 类型（可选） | `etc_t`、`httpd_config_t` 等 |
| `seuser` | str | SELinux 用户（可选） | `system_u`、`unconfined_u` 等 |
| `unsafe_writes` | bool | 是否允许不安全写入（默认 false） | true、false |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了替换 | true/false |
| `msg` | 操作结果消息 | "1 replacements made" |
| `backup` | 备份文件路径 | `/path/to/file.12345.backup` |
| `replacement_count` | 替换次数 | 3 |

## 使用情境

### 配置文件修改
- **服务配置**：修改 Nginx、Apache、MySQL 等服务配置
- **系统配置**：修改 `/etc/hosts`、`/etc/fstab`、`/etc/sysctl.conf` 等
- **应用配置**：修改应用配置文件中的数据库连接、端口等参数
- **环境配置**：修改环境变量文件、启动脚本等

### 日志和数据处理
- **日志清理**：删除或脱敏日志文件中的敏感信息
- **数据转换**：批量转换数据格式或编码
- **内容过滤**：过滤或替换文件中的特定内容
- **批量更新**：更新多个文件中的版本号、URL 等

### 安全和合规
- **密码更新**：定期更新配置文件中的密码
- **证书路径**：更新 SSL 证书路径和配置
- **权限配置**：修改权限相关的配置参数
- **合规修改**：根据安全要求修改配置

## 安全注意事项

### 文件操作安全
1. **备份策略**：重要配置文件修改前必须备份
2. **权限控制**：确保文件权限符合安全要求
3. **验证机制**：修改后验证配置文件语法正确性
4. **原子操作**：使用原子写入避免文件损坏

### 正则表达式安全
1. **精确匹配**：使用精确的正则表达式避免误替换
2. **测试验证**：在生产环境前充分测试正则表达式
3. **边界控制**：使用 `before` 和 `after` 参数限制替换范围
4. **转义处理**：正确处理特殊字符的转义

### 敏感信息处理
1. **密码保护**：使用 Ansible Vault 保护敏感替换内容
2. **日志控制**：使用 `no_log: true` 防止敏感信息泄露
3. **临时文件**：及时清理临时文件和备份文件
4. **访问控制**：限制对配置文件的访问权限

## 环境依赖

### 必需
- 目标主机上的 Python 环境
- 对目标文件的读写权限

### 推荐
- 安装相关服务的验证工具（如 `nginx -t`）
- 配置合理的文件权限和 SELinux 策略

## 常见问题

### 1. 正则表达式匹配失败
**可能原因**：
- 正则表达式语法错误
- 文件编码不匹配
- 特殊字符未正确转义

**解决方案**：
```yaml
- name: 使用简单正则表达式
  ansible.builtin.replace:
    path: /etc/hosts
    regexp: '^127\.0\.0\.1.*localhost'
    replace: '127.0.0.1 localhost'
```

### 2. 权限不足
**解决方案**：
```yaml
- name: 使用 become 权限
  ansible.builtin.replace:
    path: /etc/nginx/nginx.conf
    regexp: 'worker_processes\s+\d+;'
    replace: 'worker_processes 4;'
  become: yes
```

### 3. 文件编码问题
**解决方案**：
```yaml
- name: 指定文件编码
  ansible.builtin.replace:
    path: /path/to/file
    regexp: '旧内容'
    replace: '新内容'
    encoding: 'gbk'
```

### 4. 替换范围过大
**解决方案**：
```yaml
- name: 使用 before/after 限制范围
  ansible.builtin.replace:
    path: /etc/ssh/sshd_config
    regexp: 'PasswordAuthentication\s+yes'
    replace: 'PasswordAuthentication no'
    before: '# End of file'
    after: '# Authentication settings'
```

## 最佳实践

### 基础替换示例
```yaml
- name: 修改 Nginx 监听端口
  ansible.builtin.replace:
    path: /etc/nginx/nginx.conf
    regexp: 'listen\s+80;'
    replace: 'listen 8080;'
    backup: yes
```

### 带验证的替换示例
```yaml
- name: 修改 Apache 配置并验证
  ansible.builtin.replace:
    path: /etc/httpd/conf/httpd.conf
    regexp: '^Listen\s+80'
    replace: 'Listen 8080'
    backup: yes
    validate: 'httpd -t %s'
```

### 多行替换示例
```yaml
- name: 替换多行配置
  ansible.builtin.replace:
    path: /etc/my.cnf
    regexp: '^\[mysqld\](?:\n\s+.*)+?'
    replace: |
      [mysqld]
      port = 3306
      socket = /var/lib/mysql/mysql.sock
      datadir = /var/lib/mysql
    backup: yes
```

### 条件替换示例
```yaml
- name: 条件替换配置
  ansible.builtin.replace:
    path: /etc/app/config.ini
    regexp: '^debug\s*=.*$'
    replace: 'debug = true'
    backup: yes
  when: app_environment == 'development'
```

### 敏感信息替换示例
```yaml
- name: 更新数据库密码
  ansible.builtin.replace:
    path: /etc/app/database.conf
    regexp: 'password\s*=\s*.*$'
    replace: 'password = "{{ vault_db_password }}"'
    backup: yes
  no_log: true
```

### 批量文件替换示例
```yaml
- name: 批量更新配置文件中的版本号
  ansible.builtin.replace:
    path: "{{ item }}"
    regexp: 'version\s*=\s*[\d.]+'
    replace: 'version = {{ new_version }}'
    backup: yes
  loop:
    - /etc/app1/config.yml
    - /etc/app2/config.yml
    - /etc/app3/config.yml
```

### 使用边界控制的替换示例
```yaml
- name: 在特定范围内替换配置
  ansible.builtin.replace:
    path: /etc/ssh/sshd_config
    regexp: '^#\s*PermitRootLogin\s+.+$'
    replace: 'PermitRootLogin no'
    before: '# End of file'
    after: '# Authentication'
    backup: yes
```

### 正则表达式高级用法示例
```yaml
- name: 使用正则表达式组替换
  ansible.builtin.replace:
    path: /etc/hosts
    regexp: '^(\d+\.\d+\.\d+\.\d+)\s+(.+)$'
    replace: '\1 \2.localdomain'
    backup: yes

- name: 使用条件替换
  ansible.builtin.replace:
    path: /etc/app/config
    regexp: '^(#?\s*)(server\s+.+)$'
    replace: '\2'
    backup: yes
    when: enable_server | default(false)
```

### 文件权限和 SELinux 示例
```yaml
- name: 替换文件并设置权限
  ansible.builtin.replace:
    path: /etc/security/limits.conf
    regexp: '^\*\s+soft\s+nofile\s+\d+$'
    replace: '* soft nofile 65536'
    backup: yes
    mode: '0644'
    setype: 'etc_t'
```

### 错误处理和回滚示例
```yaml
- name: 安全替换配置（带回滚）
  ansible.builtin.replace:
    path: /etc/critical/config.conf
    regexp: 'critical_setting\s*=\s*.+$'
    replace: 'critical_setting = {{ new_value }}'
    backup: yes
    validate: '/usr/sbin/config-validator %s'
  register: replace_result

- name: 检查替换结果
  ansible.builtin.debug:
    msg: "替换结果: {{ replace_result.msg }}"

- name: 如果失败则回滚
  ansible.builtin.copy:
    src: "{{ replace_result.backup }}"
    dest: /etc/critical/config.conf
  when: replace_result.failed | default(false)
```

## 相关示例
- [lineinfile 模块](../lineinfile/README.md) - 行级配置修改
- [template 模块](../template/README.md) - 模板渲染
- [copy 模块](../copy/README.md) - 文件复制
- [file 模块](../file/README.md) - 文件权限管理