# lineinfile 模块使用指南

## 模块用途
`ansible.builtin.lineinfile` 模块用于确保文件中存在或修改特定行，非常适合精确修改配置文件而不需要替换整个文件的场景。

## 主要参数
- `path`：目标文件路径（必需）
- `line`：要插入或确保存在的行内容
- `regexp`：匹配行的正则表达式（用于查找需要修改的行）
- `state`：`present`（默认，确保行存在）或 `absent`（删除匹配的行）
- `insertafter`：在匹配的行之后插入（配合正则使用）
- `insertbefore`：在匹配的行之前插入
- `create`：文件不存在时是否创建（默认 false）
- `backup`：修改前备份文件（默认 false）
- `backrefs`：启用后向引用（regexp 中捕获的组可在 line 中使用）
- `owner` / `group` / `mode`：设置文件所有者、组、权限
- `validate`：修改后验证文件（如配置文件语法检查）

## 返回值
- `changed`：文件是否被修改
- `msg`：操作结果消息（如 "line replaced" 或 "line added"）
- `backup_file`：备份文件路径（启用 backup 时）

## 典型场景

### 修改系统配置
修改 SSH 配置、sysctl 参数、系统服务配置等，无需替换整个文件。

### 环境变量管理
在 `.bashrc`、`.profile` 或应用的环境文件中添加或修改环境变量。

### 配置项更新
修改应用配置文件中的单个配置项（如数据库地址、日志级别）。

### 服务参数调整
调整 Nginx、Apache、MySQL 等服务的特定配置参数。

## 最佳实践

### 修改配置项
```yaml
# 修改 SSH 配置禁用 root 登录
- name: 禁用 SSH root 登录
  ansible.builtin.lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^PermitRootLogin'
    line: 'PermitRootLogin no'
    backup: yes
  notify: 重启 SSH 服务
```

### 添加环境变量
```yaml
# 在 bashrc 中添加环境变量
- name: 添加应用环境变量
  ansible.builtin.lineinfile:
    path: ~/.bashrc
    line: 'export APP_HOME=/opt/myapp'
    insertafter: EOF
```

### 删除配置行
```yaml
# 删除匹配的配置行
- name: 删除过时的配置项
  ansible.builtin.lineinfile:
    path: /etc/app.conf
    regexp: '^#\s*deprecated_option'
    state: absent
```

### 使用后向引用
```yaml
# 修改配置值但保留注释
- name: 更新监听端口
  ansible.builtin.lineinfile:
    path: /etc/app.conf
    regexp: '^(listen_port\s*=\s*).*'
    line: '\1{{ new_port }}'
    backrefs: yes
```

### 创建文件并添加内容
```yaml
# 文件不存在时自动创建
- name: 确保配置行存在
  ansible.builtin.lineinfile:
    path: /etc/app/app.conf
    line: 'debug=false'
    create: yes
    mode: '0644'
```

## 注意事项

### 编码问题
- lineinfile 会保留原文件编码
- 处理包含中文的配置文件时，确保文件为 UTF-8 编码
- 使用 `line` 参数时，中文字符会被正确写入

### 幂等性
- lineinfile 默认是幂等的，多次执行相同操作不会重复修改
- 使用 `regexp` 确保精确匹配，避免意外添加重复行
- 不使用 `regexp` 时，如果 `line` 已存在则不会重复添加

### 正则表达式
- `regexp` 参数使用 Python 正则表达式语法
- 使用 `^` 匹配行首，`$` 匹配行尾
- 注意转义特殊字符（如 `.` `*` `[` `]` 等）

### 备份策略
- 修改系统配置文件前务必启用 `backup: yes`
- 备份文件格式为 `原文件名.{timestamp}.backup`
- 可在出错时快速恢复原配置

### 配置验证
- 修改服务配置后，使用 `validate` 参数验证语法
- 示例：`validate: 'nginx -t -c %s'`（%s 为临时文件路径）

## 常见陷阱

### 不使用 regexp 导致重复行
```yaml
# ❌ 错误：每次执行都会添加新行
- name: 添加配置（错误示例）
  ansible.builtin.lineinfile:
    path: /etc/app.conf
    line: 'max_connections=100'

# ✅ 正确：使用 regexp 确保唯一性
- name: 添加配置（正确示例）
  ansible.builtin.lineinfile:
    path: /etc/app.conf
    regexp: '^max_connections='
    line: 'max_connections=100'
```

### 正则表达式不精确
```yaml
# ❌ 错误：可能匹配到注释行
- name: 修改配置（不精确）
  ansible.builtin.lineinfile:
    path: /etc/app.conf
    regexp: 'port'
    line: 'port=8080'

# ✅ 正确：精确匹配配置行
- name: 修改配置（精确）
  ansible.builtin.lineinfile:
    path: /etc/app.conf
    regexp: '^port\s*='
    line: 'port=8080'
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中定义配置参数
2. 准备测试配置文件（可在远程主机手动创建）
3. 使用 `--check` 模式预览修改
4. 使用 `--diff` 查看修改前后的差异
5. 实际执行并验证文件内容
6. 测试幂等性（再次执行应显示 ok）

## 常见问题
- **为什么会添加重复行？** 缺少 `regexp` 参数导致无法识别已存在的行
- **如何修改多个相同模式的行？** lineinfile 只会修改第一个匹配的行，需要使用 `replace` 模块
- **如何在特定位置插入？** 使用 `insertafter` 或 `insertbefore` 配合 `regexp`
- **如何保留注释？** 使用 `backrefs: yes` 并在 `line` 中使用捕获组

## 与其他模块的比较
- **lineinfile vs replace**：lineinfile 处理单行，replace 可批量替换多个匹配
- **lineinfile vs template**：lineinfile 适合小改动，template 适合整个文件重新生成
- **lineinfile vs blockinfile**：lineinfile 处理单行，blockinfile 处理多行块

## 相关示例
- [template 模块](../template/README.md) - 完整配置文件生成
- [copy 模块](../copy/README.md) - 静态文件分发
- [file 模块](../file/README.md) - 文件系统基础操作
