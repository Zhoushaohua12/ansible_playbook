# expect 模块使用指南

## 模块用途
`ansible.builtin.expect` 模块用于执行需要交互式输入的命令，自动响应预期的提示信息。适用于无法通过命令行参数传递密码或确认信息的场景，如 `passwd`、`ssh-keygen`、`mysql_secure_installation` 等需要交互确认的命令。

## 主要参数
- `command`：要执行的命令，必填参数
- `responses`：字典类型，键为预期的提示信息（支持正则表达式），值为响应内容
- `timeout`：等待响应的超时时间（秒），默认为 30 秒
- `echo`：是否回显命令输出，默认为 false
- `chdir`：执行命令前切换的工作目录
- `creates`：当指定文件存在时，跳过任务执行（幂等性控制）
- `removes`：当指定文件不存在时，跳过任务执行（幂等性控制）

## 返回值
- `changed`：命令执行是否导致系统状态变更
- `rc`：命令的返回码（0 表示成功）
- `stdout`：命令的标准输出内容
- `stderr`：命令的错误输出内容
- `stdout_lines`：标准输出按行分割的列表

## 安全注意事项
1. **敏感信息保护**：responses 中的密码等敏感信息应使用 Ansible Vault 加密，避免明文存储
2. **超时控制**：设置合理的 timeout 值，避免任务长时间挂起
3. **幂等性设计**：使用 `creates`/`removes` 参数确保重复执行的安全性
4. **正则表达式精确匹配**：responses 的键支持正则，需确保匹配精准，避免误响应
5. **日志敏感信息**：默认 echo=false 防止敏感信息输出到日志，生产环境务必保持此设置

## 最佳实践

### 交互式密码设置示例
```yaml
- name: 使用 expect 设置用户密码
  ansible.builtin.expect:
    command: passwd myuser
    responses:
      (?i)password: "{{ user_password }}"
    timeout: 10
  no_log: true  # 防止密码记录到日志
```

### SSH 密钥生成示例
```yaml
- name: 生成 SSH 密钥对（自动确认覆盖）
  ansible.builtin.expect:
    command: ssh-keygen -t rsa -b 4096 -f /home/user/.ssh/id_rsa -N ""
    responses:
      'Overwrite \(y/n\)\?': 'y'
    creates: /home/user/.ssh/id_rsa
    timeout: 30
```

### 数据库安全初始化示例
```yaml
- name: MySQL 安全配置（交互式）
  ansible.builtin.expect:
    command: mysql_secure_installation
    responses:
      'Enter current password for root': ''
      'Set root password\?': 'Y'
      'New password': "{{ mysql_root_password }}"
      'Re-enter new password': "{{ mysql_root_password }}"
      'Remove anonymous users\?': 'Y'
      'Disallow root login remotely\?': 'Y'
      'Remove test database': 'Y'
      'Reload privilege tables': 'Y'
    timeout: 60
  no_log: true
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置示例参数（敏感信息使用占位符）
2. 使用 `--check` 模式预览任务执行计划
3. 在测试环境验证交互式响应是否正确匹配
4. 生产环境使用 Ansible Vault 加密敏感变量

## 常见问题
- **为什么不推荐频繁使用 expect？** expect 绕过了命令的非交互式接口，应优先考虑命令行参数或配置文件方式
- **如何调试匹配失败？** 设置 `echo: true` 查看实际提示信息，调整 responses 的正则表达式
- **timeout 设置多少合适？** 根据命令复杂度设置，简单命令 10-30 秒，复杂安装可设置 300 秒以上
- **如何处理多种可能的提示？** responses 支持正则表达式，使用 `(?i)` 忽略大小写，`.*` 匹配任意字符

## 相关示例
- [shell 模块](../shell/README.md) - 执行 shell 命令
- [command 模块](../command/README.md) - 安全的命令执行
- [script 模块](../script/README.md) - 本地脚本传输执行
