# service 模块使用指南

## 模块用途
`ansible.builtin.service` 模块用于在 Linux 系统上管理服务的启动、停止、重启和自启动配置。支持 systemd、sysvinit 等多种 init 系统，是跨发行版服务管理的通用解决方案。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | 服务名称（必需） | nginx、httpd、mysql、redis 等 |
| `state` | str | 服务状态（started 启动，stopped 停止，restarted 重启，reloaded 重载） | started、stopped、restarted、reloaded |
| `enabled` | bool | 是否启用开机自启动 | true、false |
| `use` | str | 强制使用特定 init 系统（通常自动检测，不需指定） | systemd、sysvinit、openrc 等 |
| `pattern` | str | 进程匹配模式（某些 init 系统使用） | (进程名或模式) |
| `runlevel` | str | 目标运行级别（sysvinit 使用） | 2-5 等 |
| `sleep` | int | 重启前等待时间（秒） | 1、2、5 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `name` | 服务名称 | nginx |
| `state` | 当前服务状态 | started、stopped |
| `enabled` | 是否启用自启动 | true、false |
| `status` | 服务详细状态（systemd） | 完整的 systemctl status 输出 |
| `changed` | 是否变更了服务状态 | true/false |

## 使用情境

### 应用服务生命周期管理
**场景**：部署后自动启动应用服务
- 启动 Nginx、Apache、Tomcat 等 Web 服务
- 确保服务在系统启动时自动运行
- 在更新配置后重载服务而无需重启

### 数据库与缓存服务管理
**场景**：管理数据库服务的启停与自启动
- 启动并启用 MySQL、PostgreSQL 自启动
- 启动 Redis、Memcached 缓存服务
- 定期重启清理内存（通过 cron + Ansible）

### 系统服务停止与健康检查
**场景**：维护前停止服务，完成后重启
- 停止 syslog、rsyslog 进行日志轮换
- 临时停止网络服务进行网络维护
- 与 wait_for 结合检查服务启动状态

### 零停机更新（蓝绿部署）
**场景**：通过服务重载实现无中断配置更新
- 修改 Nginx 配置后使用 reloaded 重新加载
- 更新应用配置后软重启应用进程
- 避免完整重启带来的服务中断

## 安全注意事项

1. **权限检查**：service 模块操作需要 root 或 sudo 权限
2. **服务依赖**：了解服务启动顺序与依赖关系
   - 数据库应在应用前启动
   - 网络服务应在防火墙配置后启动
3. **健康检查**：启动服务后应验证其可用性
   - 使用 wait_for 检查端口就绪
   - 使用 stat 检查进程文件
4. **日志审计**：重启关键服务前应备份日志
5. **生产环保**：在生产环境进行服务重启前应：
   - 通知相关人员
   - 准备回滚方案
   - 选择低流量时段执行

## 环境依赖

### 必需
- 目标系统必须支持 service 命令（通过 systemd 或 sysvinit）
- 目标系统必须已安装相应的服务软件包
- 执行操作需要 root 或 sudo 权限

### 推荐
- systemd：现代 Linux 系统标准
- sysvinit：较旧系统兼容
- 结合 wait_for 模块进行服务就绪检查

## 常见问题

### 1. 无法启动服务，显示 "Unit not found"
服务未安装或命名不同：
```bash
# 查看已安装的服务
systemctl list-unit-files | grep SERVICE_NAME
```

### 2. stopped 状态后立即重启失败
可能需要等待进程完全关闭，使用 sleep 参数：
```yaml
- name: 重启服务（带等待）
  ansible.builtin.service:
    name: nginx
    state: restarted
    sleep: 2
```

### 3. 在容器中运行 service 模块失败
容器通常不运行 systemd，需要：
- 在镜像中安装 systemd
- 或使用容器相关的模块（如 docker_container）
- 或在主机上使用 systemd

### 4. reloaded 与 restarted 的区别是什么？
- `restarted`：完整重启服务，会断开所有连接
- `reloaded`：重新加载配置，不中断现有连接
- 并非所有服务都支持 reloaded（某些不支持会失败）

## 最佳实践

### 基础服务启动示例
```yaml
- name: 启动并启用 Nginx
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
```

### 配置更新后重载示例
```yaml
- name: 更新 Nginx 配置
  ansible.builtin.lineinfile:
    path: /etc/nginx/nginx.conf
    regexp: '^worker_processes'
    line: 'worker_processes auto;'

- name: 重载 Nginx 配置
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

### 与健康检查结合示例
```yaml
- name: 启动服务
  ansible.builtin.service:
    name: nginx
    state: started

- name: 等待服务启动完成
  ansible.builtin.wait_for:
    port: 80
    delay: 2
    timeout: 30
```

### 多服务依赖管理示例
```yaml
- name: 按顺序启动依赖服务
  ansible.builtin.service:
    name: "{{ item }}"
    state: started
    enabled: true
  loop:
    - postgresql  # 数据库先启
    - redis       # 缓存次之
    - myapp       # 应用最后
```

## 相关示例
- [systemd 模块](../systemd/README.md) - 更底层的 systemd 单元管理
- [wait_for 模块](../../network/wait_for/README.md) - 服务就绪监控
- [firewalld 模块](../firewalld/README.md) - 防火墙配置
