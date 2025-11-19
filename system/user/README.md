# user 模块使用指南

## 模块用途
`ansible.builtin.user` 模块用于创建、修改和删除 Linux 用户账号，支持管理用户的主组、辅助组、SSH 密钥、sudo 权限等。适用于运维账号创建、应用用户配置、权限隔离等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | 用户账号名称（必需） | deploy、app、nginx、redis 等 |
| `state` | str | 用户状态（present 创建/修改，absent 删除） | present、absent |
| `uid` | int | 用户 ID（UID），可指定固定值 | 1000、1001 等 |
| `group` | str | 用户的主组名称 | wheel、docker、sudo 等 |
| `groups` | str | 用户的辅助组，逗号分隔 | wheel,docker,adm 等 |
| `append` | bool | 添加辅助组时是否保留现有组（true 追加，false 覆盖） | true、false |
| `shell` | str | 用户登录 shell | /bin/bash、/bin/sh、/sbin/nologin 等 |
| `home` | str | 用户主目录 | /home/deploy、/opt/app 等 |
| `createhome` | bool | 是否创建主目录 | true、false |
| `password` | str | 用户密码（需加密，使用 password_hash 过滤器） | (加密后的哈希值) |
| `update_password` | str | 密码更新策略（always 每次更新，on_create 仅创建时） | always、on_create |
| `ssh_key_file` | str | SSH 公钥文件路径 | ~/.ssh/id_rsa.pub |
| `authorized_keys` | list | SSH 公钥列表 | ssh-rsa AAAA... |
| `generate_ssh_key` | bool | 是否生成 SSH 密钥对 | true、false |
| `ssh_key_passphrase` | str | SSH 密钥密码短语 | (占位符) |
| `comment` | str | 用户注释（GECOS 字段） | 运维账号、应用账号 等 |
| `expires` | float | 账号过期时间（Unix 时间戳） | 1704067200 等 |
| `force` | bool | 强制执行（删除用户时若有进程运行是否强制删除） | true、false |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `uid` | 用户 ID | 1000 |
| `gid` | 用户主组 ID | 1000 |
| `group` | 用户主组名称 | deploy |
| `home` | 用户主目录 | /home/deploy |
| `shell` | 用户登录 shell | /bin/bash |
| `name` | 用户名 | deploy |
| `ssh_public_key` | 生成的 SSH 公钥内容 | ssh-rsa AAAA... |
| `changed` | 是否修改了用户 | true/false |

## 使用情境

### 创建运维账号与权限隔离
**场景**：为不同的运维团队创建专用账号，通过组进行权限管理
- 创建部署账号：deploy 用户，加入 docker、sudo 组
- 创建数据库运维账号：dba 用户，加入 mysql、adm 组
- 创建监控账号：monitor 用户，仅读权限，不需要 sudo

### 应用专用账号
**场景**：为每个应用服务创建独立用户，实现权限隔离
- Nginx：nginx 用户，无 login shell
- 应用进程：app 用户，指定主目录为应用目录
- 数据库：mysql 用户，系统账号，无 home 目录

### SSH 密钥管理
**场景**：自动化 SSH 密钥生成与授权
- 为部署账号生成 SSH 密钥对
- 配置授权密钥以支持 SSH 公钥登录

## 安全注意事项

1. **最小权限原则**：仅赋予用户所需的最小权限，使用辅助组而非 root
2. **密码处理**：
   - 避免在 playbook 中硬编码密码
   - 使用 `password_hash` 过滤器加密密码
   - 结合 Ansible Vault 保护敏感信息
3. **Shell 限制**：非交互式应用用户使用 `/sbin/nologin` 防止登录
4. **主目录权限**：确保应用用户的主目录权限为 700（仅所有者可访问）
5. **SSH 密钥安全**：
   - SSH 密钥文件权限 600（仅所有者可读写）
   - 定期更新密钥，使用密码保护私钥
6. **sudo 权限**：
   - 谨慎配置 sudoers，仅允许必需命令
   - 启用 sudo 审计日志追踪执行操作

## 环境依赖

### 必需
- 目标主机必须支持 useradd/usermod/userdel 命令
- 必要时需要 root 或 sudo 权限

### 推荐
- python-passlib 库：用于 password_hash 过滤器
- 配置 sudo 时需要 visudo 验证权限

## 常见问题

### 1. 如何以非 root 用户身份创建账号？
需要 become 权限：
```yaml
- name: 创建用户（需要 sudo 权限）
  ansible.builtin.user:
    name: deploy
    state: present
  become: yes
```

### 2. 密码设置失败，提示 "unsupported password format"
需要安装 passlib：`pip install passlib`，并使用正确的哈希格式：
```yaml
password: "{{ 'mypassword' | password_hash('sha512') }}"
```

### 3. 用户已存在但需要修改组信息
使用 `append: yes` 追加组，避免覆盖现有组：
```yaml
- name: 为用户添加 docker 组
  ansible.builtin.user:
    name: deploy
    groups: docker
    append: yes
```

### 4. 删除用户时提示用户有进程运行
使用 `force: yes` 强制删除（谨慎使用）：
```yaml
- name: 强制删除用户
  ansible.builtin.user:
    name: deploy
    state: absent
    force: yes
    remove: yes  # 同时删除主目录
```

## 最佳实践

### 运维账号创建示例
```yaml
- name: 创建运维账号
  ansible.builtin.user:
    name: deploy
    comment: 部署运维账号
    shell: /bin/bash
    home: /home/deploy
    createhome: yes
    uid: 1000
    groups: wheel,docker
    state: present
```

### 应用专用账号示例
```yaml
- name: 创建应用账号
  ansible.builtin.user:
    name: appuser
    comment: 应用服务账号
    shell: /sbin/nologin  # 禁止登录
    home: /opt/app
    createhome: yes
    state: present
```

### SSH 密钥自动化示例
```yaml
- name: 为部署账号生成 SSH 密钥
  ansible.builtin.user:
    name: deploy
    generate_ssh_key: yes
    ssh_key_bits: 4096
    ssh_key_comment: "deploy@{{ inventory_hostname }}"
    state: present
```

## 相关示例
- [group 模块](../group/README.md) - 用户组管理
- [service 模块](../service/README.md) - 服务管理
- [firewalld 模块](../firewalld/README.md) - 防火墙配置（限制用户操作权限）
