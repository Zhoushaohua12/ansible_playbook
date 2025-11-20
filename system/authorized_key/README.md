# authorized_key 模块使用指南

## 模块用途
`ansible.builtin.authorized_key` 模块用于管理用户的 SSH 授权密钥，支持添加、删除和更新 SSH 公钥。适用于自动化服务器访问权限管理、批量密钥分发、权限回收等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `user` | str | 目标用户名（必需） | deploy、appuser、root 等 |
| `state` | str | 密钥状态（present 添加，absent 删除） | present、absent |
| `key` | str | SSH 公钥内容（必需） | "ssh-rsa AAAA..." |
| `key_options` | str | SSH 密钥选项（可选） | "no-port-forwarding,no-agent-forwarding" |
| `path` | str | authorized_keys 文件路径（可选） | `~/.ssh/authorized_keys` |
| `manage_dir` | bool | 是否管理 `.ssh` 目录（默认 true） | true、false |
| `exclusive` | bool | 是否排他模式（仅保留指定密钥） | true、false |
| `comment` | str | 密钥注释（可选） | "deploy@workstation" |
| `validate_certs` | bool | 是否验证证书（默认 true） | true、false |
| `follow` | bool | 是否跟随符号链接（默认 false） | true、false |

## SSH 密钥选项

| 选项 | 说明 |
|------|------|
| `no-port-forwarding` | 禁止端口转发 |
| `no-agent-forwarding` | 禁止认证代理转发 |
| `no-X11-forwarding` | 禁止 X11 转发 |
| `no-pty` | 禁止 PTY 分配 |
| `command="command"` | 限制只能执行特定命令 |
| `from="pattern"` | 限制来源 IP 或主机 |
| `restrict` | 启用所有限制选项 |
| `cert-authority` | 标记为证书颁发机构密钥 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否修改了授权密钥 | true/false |
| `key` | 操作的密钥内容 | "ssh-rsa AAAA..." |
| `user` | 目标用户 | deploy |
| `path` | authorized_keys 文件路径 | "/home/deploy/.ssh/authorized_keys" |
| `msg` | 操作结果消息 | "ssh key added" |

## 使用情境

### 运维人员权限管理
- **部署账号密钥**：为部署团队添加 SSH 公钥，实现自动化部署
- **临时访问权限**：为外部顾问添加有时限的访问密钥
- **权限回收**：离职人员密钥删除，确保系统安全
- **多环境管理**：开发、测试、生产环境分别配置不同密钥

### 应用服务管理
- **应用账号密钥**：为应用服务配置 SSH 密钥，用于代码拉取
- **Git 访问配置**：配置 Git 仓库访问的 SSH 密钥
- **服务间通信**：配置微服务之间的 SSH 通信密钥
- **备份服务密钥**：为备份服务配置访问目标服务器的密钥

### 自动化运维
- **批量密钥分发**：在新服务器上批量添加管理密钥
- **密钥轮换**：定期更新 SSH 密钥，提升安全性
- **灾备恢复**：快速恢复服务器访问权限
- **审计合规**：集中管理和审计所有 SSH 访问权限

## 安全注意事项

### 密钥管理
1. **密钥强度**：使用至少 2048 位的 RSA 密钥或 Ed25519 密钥
2. **密钥保护**：私钥使用强密码保护，存储在安全位置
3. **定期轮换**：建立定期更换 SSH 密钥的流程
4. **最小权限**：每个用户只拥有必要的访问权限

### 访问控制
1. **来源限制**：使用 `from` 选项限制访问来源 IP
2. **功能限制**：使用 `command` 选项限制可执行命令
3. **端口限制**：禁用不必要的端口转发功能
4. **时间控制**：配合 cron 任务实现临时访问权限

### 文件安全
1. **文件权限**：确保 `.ssh` 目录权限为 700，authorized_keys 为 600
2. **目录所有者**：确保 `.ssh` 目录和文件的所有者正确
3. **符号链接**：谨慎使用符号链接，避免安全风险
4. **备份管理**：定期备份 authorized_keys 文件

## 环境依赖

### 必需
- 目标主机必须支持 SSH 服务
- OpenSSH 客户端和服务器
- 目标用户必须存在

### 推荐
- OpenSSH 7.0+ 版本（支持更多密钥选项）
- 配置合理的 SSH 服务安全策略
- 启用 SSH 访问日志记录

## 常见问题

### 1. 密钥添加失败
**可能原因**：
- 目标用户不存在
- `.ssh` 目录权限不正确
- 磁盘空间不足
- SELinux/AppArmor 限制

**排查方法**：
```bash
# 检查用户是否存在
id username

# 检查目录权限
ls -la /home/username/.ssh/

# 检查 SELinux 状态
sestatus

# 手动测试 SSH 连接
ssh -i keyfile username@hostname
```

### 2. 密钥无法使用
**可能原因**：
- 公钥格式错误
- SSH 服务配置问题
- 防火墙阻止连接
- 用户 shell 限制

**排查方法**：
```bash
# 检查 SSH 服务状态
sudo systemctl status sshd

# 检查 SSH 配置
sudo sshd -T

# 测试密钥认证
ssh -v -i keyfile username@hostname

# 查看 SSH 日志
sudo tail -f /var/log/auth.log
```

### 3. 权限问题
**解决方案**：
```yaml
- name: 确保 SSH 目录权限正确
  ansible.builtin.file:
    path: "/home/{{ item }}/.ssh"
    state: directory
    owner: "{{ item }}"
    group: "{{ item }}"
    mode: '0700'
  loop:
    - deploy
    - appuser
```

### 4. 密钥格式问题
**常见格式**：
- RSA: `ssh-rsa AAAAB3NzaC1yc2EAAA...`
- ECDSA: `ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTY...`
- Ed25519: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...`

## 最佳实践

### 基础密钥管理示例
```yaml
- name: 为部署用户添加 SSH 公钥
  ansible.builtin.authorized_key:
    user: deploy
    state: present
    key: "{{ deploy_public_key }}"
    manage_dir: yes
```

### 带安全选项的密钥示例
```yaml
- name: 添加受限的运维密钥
  ansible.builtin.authorized_key:
    user: ops
    state: present
    key: "{{ ops_public_key }}"
    key_options: "no-port-forwarding,no-agent-forwarding,no-X11-forwarding,from=\"192.168.1.0/24\""
    comment: "ops_team@company.com"
```

### 排他模式密钥管理示例
```yaml
- name: 设置应用用户的唯一授权密钥
  ansible.builtin.authorized_key:
    user: appuser
    state: present
    key: "{{ app_public_key }}"
    exclusive: yes  # 仅保留此密钥，删除其他所有密钥
    comment: "app_service@production"
```

### 批量密钥管理示例
```yaml
- name: 为多个用户添加管理密钥
  ansible.builtin.authorized_key:
    user: "{{ item.user }}"
    state: present
    key: "{{ item.key }}"
    comment: "{{ item.comment }}"
  loop:
    - { user: 'deploy', key: '{{ deploy_key }}', comment: 'deploy@ci-server' }
    - { user: 'backup', key: '{{ backup_key }}', comment: 'backup@backup-server' }
    - { user: 'monitor', key: '{{ monitor_key }}', comment: 'monitor@monitoring-server' }
```

### 密钥删除示例
```yaml
- name: 删除离职人员的 SSH 密钥
  ansible.builtin.authorized_key:
    user: former_employee
    state: absent
    key: "{{ former_employee_key }}"
```

### 限制命令执行的密钥示例
```yaml
- name: 添加只能执行备份脚本的密钥
  ansible.builtin.authorized_key:
    user: backup_user
    state: present
    key: "{{ backup_script_key }}"
    key_options: 'command="/usr/local/bin/backup_script.sh",no-pty,no-agent-forwarding,no-port-forwarding'
    comment: "backup_only@automation"
```

### 自定义 authorized_keys 路径示例
```yaml
- name: 管理自定义位置的授权密钥
  ansible.builtin.authorized_key:
    user: custom_user
    state: present
    key: "{{ custom_key }}"
    path: "/etc/ssh/custom_authorized_keys"
    manage_dir: no
```

### 密钥验证示例
```yaml
- name: 验证密钥格式并添加
  ansible.builtin.authorized_key:
    user: "{{ target_user }}"
    state: present
    key: "{{ ssh_public_key }}"
    validate_certs: yes
  when: ssh_public_key is match('ssh-(rsa|dsa|ecdsa|ed25519) ')
```

## 相关示例
- [user 模块](../user/README.md) - 用户管理
- [file 模块](../../files/file/README.md) - 文件权限管理
- [service 模块](../service/README.md) - SSH 服务管理
- [cron 模块](../cron/README.md) - 定时任务管理