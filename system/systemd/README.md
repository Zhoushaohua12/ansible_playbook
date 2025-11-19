# systemd 模块使用指南

## 模块用途
`ansible.posix.systemd` 模块提供底层 systemd 单元管理功能，包括启用/禁用服务、管理单元状态、启用定时器、加载用户级 systemd 单元等。相比 service 模块，systemd 模块提供更细粒度的单元管理控制。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | 单元名称（必需）| nginx.service、timerd.timer、mount_point.mount 等 |
| `state` | str | 单元状态（started 启动，stopped 停止，restarted 重启，reloaded 重载） | started、stopped、restarted、reloaded |
| `enabled` | bool | 是否启用单元开机自启动 | true、false |
| `masked` | bool | 是否 mask（禁用）单元 | true、false |
| `daemon_reload` | bool | 修改 systemd 文件后是否重新加载 daemon | true、false |
| `force` | bool | 是否强制执行操作 | true、false |
| `no_block` | bool | 是否不等待操作完成直接返回 | true、false |
| `scope` | str | 单元作用范围（system 系统级别，user 用户级别） | system、user |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `name` | 单元名称 | nginx.service |
| `state` | 单元当前状态 | started、stopped |
| `enabled` | 是否启用开机自启动 | true/false |
| `status` | 单元详细状态信息 | 完整的 systemctl status 输出 |
| `changed` | 是否修改了单元状态 | true/false |

## 使用情境

### 用户级 systemd 单元管理
**场景**：普通用户运行的持久化服务（如 syncthing、vscode-server）
- 为特定用户启用 systemd 服务
- 管理用户定时任务（user timer）
- 无需 root 权限的服务管理

### 系统定时任务
**场景**：使用 systemd timer 替代 crontab
- 启用定期备份 timer（backup.timer）
- 启用日志轮换 timer（logrotate.timer）
- 更精确的时间控制与日志记录

### 自定义 systemd 单元
**场景**：部署自定义应用 systemd 单元文件
- 上传 .service 文件后重新加载 daemon
- 启用并启动自定义应用
- 管理单元依赖关系与启动顺序

### 单元 mask 与 unmask
**场景**：禁用不需要的系统服务
- Mask 某个服务防止其被意外启动
- Unmask 后恢复服务使用
- 用于在不删除单元文件的情况下禁用服务

## 安全注意事项

1. **权限区分**：
   - `scope: system` 需要 root 权限
   - `scope: user` 可由普通用户执行
2. **daemon_reload**：修改 systemd 单元文件后必须执行 daemon_reload
3. **mask 的风险**：masked 单元无法启动，需谨慎使用
4. **定时器依赖**：timer 可能依赖特定的 service 单元
5. **审计追踪**：关键服务操作应启用 auditd 记录

## 环境依赖

### 必需
- 目标系统必须使用 systemd
- 执行系统级操作需要 root 或 sudo 权限
- ansible.posix collection 已安装

### 推荐
- systemd >= 200（支持大部分特性）
- 了解 systemd 单元文件格式（.service、.timer、.mount 等）

## 常见问题

### 1. daemon_reload 的作用是什么？
修改 systemd 单元文件后必须 daemon_reload 使配置生效：
```yaml
- name: 修改单元文件后重新加载
  ansible.posix.systemd:
    name: myservice
    daemon_reload: true
```

### 2. mask 与 disabled 的区别是什么？
- `disabled`：仅禁用开机自启，但仍可手动启动
- `masked`：彻底禁用，无法启动，必须先 unmask

### 3. scope: user 与 scope: system 的区别？
- `scope: system` 作用于系统级单元，需要 root 权限
- `scope: user` 作用于用户级单元，普通用户可操作

### 4. no_block 什么时候使用？
某些单元启动缓慢，设置 `no_block: true` 不等待启动完成：
```yaml
- name: 启动服务但不等待完成
  ansible.posix.systemd:
    name: myservice
    state: started
    no_block: true
```

## 最佳实践

### 部署自定义 systemd 单元示例
```yaml
- name: 上传自定义 service 文件
  ansible.builtin.copy:
    src: myapp.service
    dest: /etc/systemd/system/

- name: 重新加载 systemd daemon
  ansible.posix.systemd:
    daemon_reload: true

- name: 启用并启动自定义服务
  ansible.posix.systemd:
    name: myapp.service
    state: started
    enabled: true
```

### 管理系统 timer 示例
```yaml
- name: 启用定期备份 timer
  ansible.posix.systemd:
    name: backup.timer
    enabled: true
    state: started
```

### 用户级 systemd 单元示例
```yaml
- name: 为用户启用 systemd 服务
  ansible.posix.systemd:
    name: syncthing.service
    scope: user
    state: started
    enabled: true
  become: yes
  become_user: deploy
```

### Mask 不需要的服务示例
```yaml
- name: Mask 不需要的系统服务
  ansible.posix.systemd:
    name: "{{ item }}"
    masked: true
  loop:
    - bluetooth.service
    - cups.service
```

## 相关示例
- [service 模块](../service/README.md) - 高层服务管理接口
- [handlers_notify 示例](../../advanced/handlers_notify/README.md) - handler 与 notify 机制
