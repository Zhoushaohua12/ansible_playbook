# blockinfile 模块使用指南

## 模块用途
`ansible.builtin.blockinfile` 模块用于在文件中插入、更新或删除文本块，支持标记文本块、备份文件、验证插入结果等功能。适用于配置文件管理、脚本插入、注释块维护等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `path` | str | 目标文件路径（必需） | `/etc/hosts`、`/etc/crontab`、`/etc/motd` 等 |
| `block` | str | 要插入的文本块内容（可选） | 多行文本、配置片段、脚本代码等 |
| `state` | str | 文本块状态（present 插入/更新，absent 删除） | present、absent |
| `marker` | str | 文本块标记模板（默认包含 Ansible 管理） | `# {mark} MANAGED BLOCK` |
| `marker_begin` | str | 开始标记（可选） | `# BEGIN ANSIBLE MANAGED BLOCK` |
| `marker_end` | str | 结束标记（可选） | `# END ANSIBLE MANAGED BLOCK` |
| `insertafter` | str | 在此内容之后插入（可选） | `EOF`、`^# .*`、特定行等 |
| `insertbefore` | str | 在此内容之前插入（可选） | `BOF`、`^# .*`、特定行等 |
| `create` | bool | 文件不存在时是否创建（默认 false） | true、false |
| `backup` | bool | 是否备份原文件（默认 false） | true、false |
| `validate` | str | 验证命令（可选） | `visudo -cf %s`、`crontab %s` 等 |
| `mode` | str | 文件权限模式（可选） | `0644`、`0755` 等 |
| `owner` | str | 文件所有者（可选） | `root`、`www-data` 等 |
| `group` | str | 文件所属组（可选） | `root`、`www-data` 等 |
| `selevel`、`serole`、`setype`、`seuser` | str | SELinux 相关参数（可选） | 各种 SELinux 值 |
| `unsafe_writes` | bool | 是否允许不安全写入（默认 false） | true、false |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了修改 | true/false |
| `msg` | 操作结果消息 | "Block inserted" |
| `backup` | 备份文件路径 | `/path/to/file.12345.backup` |
| `diff` | 文件差异信息 | 显示具体变更内容 |

## 使用情境

### 配置文件管理
- **服务配置**：在 Nginx、Apache 等配置文件中插入配置块
- **系统配置**：在 `/etc/hosts`、`/etc/fstab` 等文件中添加配置
- **应用配置**：在应用配置文件中添加功能模块配置
- **环境配置**：在环境变量文件中添加配置块

### 脚本和代码管理
- **脚本插入**：在 shell 脚本中插入功能代码块
- **函数添加**：在配置文件中添加自定义函数
- **注释维护**：在代码文件中添加说明注释块
- **模板扩展**：在模板文件中添加可重用代码块

### 系统维护
- **定时任务**：在 crontab 文件中添加定时任务块
- **用户管理**：在用户配置文件中添加用户信息块
- **权限配置**：在权限配置文件中添加权限规则块
- **日志配置**：在日志配置中添加日志处理规则

## 安全注意事项

### 文件操作安全
1. **备份策略**：重要文件修改前必须备份
2. **权限控制**：确保文件权限符合安全要求
3. **验证机制**：修改后验证文件语法正确性
4. **原子操作**：使用安全的文件写入方式

### 内容安全
1. **敏感信息**：敏感配置内容使用 Ansible Vault 保护
2. **代码审查**：插入的代码块需要经过安全审查
3. **权限最小化**：只给文件必要的权限
4. **访问控制**：限制对配置文件的访问

### 标记管理
1. **标记唯一性**：确保标记在文件中是唯一的
2. **标记可见性**：使用清晰的标记便于识别管理内容
3. **标记一致性**：在多个文件中使用一致的标记格式
4. **标记文档**：在文档中说明标记的作用和格式

## 环境依赖

### 必需
- 目标主机上的 Python 环境
- 对目标文件的读写权限

### 推荐
- 安装相关服务的验证工具（如 `visudo`、`crontab`）
- 配置合理的文件权限和 SELinux 策略

## 常见问题

### 1. 标记冲突
**可能原因**：
- 文件中已存在相同标记
- 标记格式不匹配
- 嵌套标记问题

**解决方案**：
```yaml
- name: 使用自定义标记避免冲突
  ansible.builtin.blockinfile:
    path: /etc/someconfig
    marker: "# {mark} CUSTOM CONFIG BLOCK"
    block: |
      # 自定义配置内容
      setting1 = value1
      setting2 = value2
```

### 2. 插入位置错误
**可能原因**：
- `insertafter` 或 `insertbefore` 参数设置错误
- 正则表达式匹配失败
- 文件结构变化

**解决方案**：
```yaml
- name: 使用精确的插入位置
  ansible.builtin.blockinfile:
    path: /etc/somefile
    insertafter: '^# Configuration Section'
    block: |
      # 新增配置
      new_setting = value
```

### 3. 文件权限问题
**解决方案**：
```yaml
- name: 使用 become 权限
  ansible.builtin.blockinfile:
    path: /etc/important.conf
    block: |
      # 重要配置
      important_setting = value
  become: yes
```

### 4. 验证失败
**解决方案**：
```yaml
- name: 带验证的插入操作
  ansible.builtin.blockinfile:
    path: /etc/sudoers
    block: |
      # 用户权限配置
      deploy ALL=(ALL) NOPASSWD: /usr/local/bin/deploy.sh
    validate: 'visudo -cf %s'
    backup: yes
```

## 最佳实践

### 基础插入示例
```yaml
- name: 在配置文件中插入配置块
  ansible.builtin.blockinfile:
    path: /etc/nginx/nginx.conf
    block: |
      # 自定义服务器配置
      server {
          listen 8080;
          server_name localhost;
          location / {
              root /var/www/html;
              index index.html;
          }
      }
    marker: "# {mark} ANSIBLE MANAGED NGINX BLOCK"
    backup: yes
```

### 带位置控制的插入示例
```yaml
- name: 在文件末尾插入配置块
  ansible.builtin.blockinfile:
    path: /etc/hosts
    block: |
      # 应用服务器集群
      192.168.1.10 app01.example.com
      192.168.1.11 app02.example.com
      192.168.1.12 app03.example.com
    insertafter: EOF
    marker: "# {mark} APP SERVERS"
```

### 条件插入示例
```yaml
- name: 根据环境插入不同的配置块
  ansible.builtin.blockinfile:
    path: /etc/app/config.ini
    block: |
      [development]
      debug = true
      log_level = DEBUG
      database = dev_db.example.com
    marker: "# {mark} DEVELOPMENT CONFIG"
    when: app_environment == 'development'
```

### 带验证的插入示例
```yaml
- name: 在 sudoers 文件中插入权限配置
  ansible.builtin.blockinfile:
    path: /etc/sudoers.d/ansible_managed
    block: |
      # 部署用户权限
      deploy ALL=(ALL) NOPASSWD: /usr/local/bin/deploy.sh
      # 监控用户权限
      monitor ALL=(ALL) NOPASSWD: /usr/local/bin/monitor.sh
    create: yes
    mode: '0440'
    validate: 'visudo -cf %s'
    backup: yes
```

### 多环境配置管理示例
```yaml
- name: 插入生产环境配置块
  ansible.builtin.blockinfile:
    path: /etc/app/production.conf
    block: |
      # 生产环境配置
      max_connections = 1000
      timeout = 30
      log_level = ERROR
      backup_enabled = true
    marker: "# {mark} PRODUCTION CONFIG"
    when: app_environment == 'production'

- name: 插入开发环境配置块
  ansible.builtin.blockinfile:
    path: /etc/app/production.conf
    block: |
      # 开发环境配置
      max_connections = 100
      timeout = 60
      log_level = DEBUG
      backup_enabled = false
    marker: "# {mark} DEVELOPMENT CONFIG"
    when: app_environment == 'development'
```

### 脚本代码插入示例
```yaml
- name: 在 shell 脚本中插入函数块
  ansible.builtin.blockinfile:
    path: /usr/local/bin/deploy.sh
    block: |
      # 部署函数
      deploy_application() {
          echo "开始部署应用..."
          # 停止旧版本
          systemctl stop app.service
          # 部署新版本
          cp -r /opt/app/new/* /opt/app/current/
          # 启动新版本
          systemctl start app.service
          echo "部署完成"
      }
    marker: "# {mark} DEPLOY FUNCTION"
    insertbefore: EOF
    backup: yes
```

### 删除配置块示例
```yaml
- name: 删除过时的配置块
  ansible.builtin.blockinfile:
    path: /etc/app/config.conf
    state: absent
    marker: "# {mark} DEPRECATED CONFIG"
```

### 批量文件插入示例
```yaml
- name: 在多个配置文件中插入通用配置块
  ansible.builtin.blockinfile:
    path: "{{ item }}"
    block: |
      # 通用安全配置
      ssl_protocols TLSv1.2 TLSv1.3
      ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512
      ssl_prefer_server_ciphers off
    marker: "# {mark} SSL SECURITY CONFIG"
    backup: yes
  loop:
    - /etc/nginx/sites-available/default
    - /etc/nginx/sites-available/api.example.com
    - /etc/nginx/sites-available/admin.example.com
```

### 带文件属性设置的插入示例
```yaml
- name: 创建并插入配置文件
  ansible.builtin.blockinfile:
    path: /etc/app/custom.conf
    block: |
      # 应用自定义配置
      app_name = {{ app_name }}
      app_version = {{ app_version }}
      app_port = {{ app_port }}
      app_host = {{ app_host }}
    create: yes
    mode: '0644'
    owner: 'appuser'
    group: 'appuser'
    marker: "# {mark} APP CUSTOM CONFIG"
    backup: yes
```

### 复杂标记管理示例
```yaml
- name: 使用自定义标记格式
  ansible.builtin.blockinfile:
    path: /etc/complex/config.conf
    block: |
      # 复杂配置示例
      section1 {
          parameter1 = value1
          parameter2 = value2
      }
      
      section2 {
          parameter3 = value3
          parameter4 = value4
      }
    marker_begin: "### BEGIN CUSTOM CONFIG - {{ ansible_date_time.iso8601 }}"
    marker_end: "### END CUSTOM CONFIG - {{ ansible_date_time.iso8601 }}"
    backup: yes
```

### 带错误处理的插入示例
```yaml
- name: 安全插入配置块（带回滚机制）
  ansible.builtin.blockinfile:
    path: /etc/critical/config.conf
    block: |
      # 关键配置
      critical_setting = {{ critical_value }}
      backup_enabled = true
    validate: '/usr/sbin/config-validator %s'
    backup: yes
  register: insert_result

- name: 检查插入结果
  ansible.builtin.debug:
    msg: "插入结果: {{ insert_result.msg }}"

- name: 如果失败则回滚
  ansible.builtin.copy:
    src: "{{ insert_result.backup }}"
    dest: /etc/critical/config.conf
  when: insert_result.failed | default(false)
```

## 相关示例
- [lineinfile 模块](../lineinfile/README.md) - 行级配置修改
- [replace 模块](../replace/README.md) - 文本替换
- [template 模块](../template/README.md) - 模板渲染
- [copy 模块](../copy/README.md) - 文件复制