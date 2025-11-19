# hostname 模块使用指南

## 模块用途
`ansible.builtin.hostname` 模块用于设置 Linux 系统的主机名。支持 systemd、sysvinit 等多种 init 系统，自动修改 `/etc/hostname`、`/etc/hosts` 等配置文件，并通过 `hostnamectl` 命令在运行时应用更改。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | 新主机名（必需） | web-server-01、db-primary、kube-node-1 等 |
| `use` | str | 主机名设置方法（通常自动检测） | systemd、sysvinit、redhat、debian、freebsd 等 |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `name` | 当前主机名 | web-server-01 |
| `changed` | 是否修改了主机名 | true/false |

## 使用情境

### 批量服务器主机名标准化
**场景**：部署新服务器集群时统一命名
- Web 服务器：web-1、web-2、web-3 ...
- 数据库服务器：db-primary、db-secondary ...
- 应用服务器：app-1、app-2 ...
- 监控服务器：monitor-server

### 云环境主机名配置
**场景**：云平台实例默认名称不清晰，需要改为业务相关名称
- 将 EC2 实例 "ip-192-168-1-100" 改为 "api-server-01"
- 将 Azure VM "VMXXXXXX" 改为 "db-01"
- 将容器 ID 改为有意义的业务名称

### 容器与 Kubernetes 集群
**场景**：容器镜像启动时自动配置主机名
- Pod 启动时设置有意义的主机名
- 集群节点命名规范化
- 日志与监控中显示清晰的主机标识

### 灾备与恢复
**场景**：备用主机激活时更新主机名
- 从备用主机切换到生产时更新主机名
- 确保新主机名与 DNS 记录匹配
- 避免双重主机名导致的混淆

## 安全注意事项

1. **主机名规范**：
   - 仅使用小写字母、数字、连字符
   - 不使用特殊字符或大写字母
   - 长度通常不超过 63 字符
2. **DNS 对应**：修改主机名前确保 DNS 记录已更新
3. **应用程序依赖**：某些应用（如数据库）可能依赖主机名，修改前备份配置
4. **集群一致性**：集群环境中主机名必须唯一
5. **日志与审计**：记录主机名修改操作用于审计

## 环境依赖

### 必需
- 目标系统需要 root 或 sudo 权限
- 支持 hostnamectl 或其他主机名管理工具

### 推荐
- systemd 系统（自动检测最优方法）
- 提前准备 DNS A 记录（正向解析）

## 常见问题

### 1. 修改后主机名未生效？
检查是否需要启用 systemd-hostnamed 服务：
```bash
systemctl start systemd-hostnamed
systemctl enable systemd-hostnamed
```

### 2. 修改主机名后 SSH 连接失败？
可能是 SSH 跳转关键字 %h 受影响，检查本地 SSH 配置：
```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null user@host
```

### 3. 容器中修改主机名无效？
容器通常从 docker run --hostname 参数获取主机名，Ansible 模块无法覆盖。需要：
```bash
docker run --hostname mycontainer ...
```

### 4. /etc/hosts 文件需要手动更新吗？
Ansible hostname 模块会自动更新 /etc/hosts，无需手动操作。

## 最佳实践

### 标准化命名规范
```yaml
# 建议的命名规范
# [环境][角色][编号]
# web-prod-01, db-prod-primary, cache-dev-01 等

- name: 设置 Web 服务器主机名
  ansible.builtin.hostname:
    name: "{{ 'web-' + env + '-' + '%02d' | format(inventory_hostname[-2:]) }}"
    # 生成: web-prod-01, web-prod-02 等
```

### 区域数据中心命名
```yaml
- name: 按区域设置主机名
  ansible.builtin.hostname:
    name: "{{ service_type }}-{{ region }}-{{ '%02d' | format(index) }}"
  vars:
    service_type: web
    region: us-east-1
    index: 1
  # 生成: web-us-east-1-01
```

### 修改后验证
```yaml
- name: 修改主机名
  ansible.builtin.hostname:
    name: "{{ new_hostname }}"

- name: 验证主机名修改
  ansible.builtin.command: hostnamectl
  register: hostname_result
  changed_when: false

- name: 显示新主机名
  ansible.builtin.debug:
    msg: "{{ hostname_result.stdout }}"
```

### 与 /etc/hosts 配置结合
```yaml
- name: 修改主机名
  ansible.builtin.hostname:
    name: myserver

- name: 更新 /etc/hosts 确保本机解析
  ansible.builtin.lineinfile:
    path: /etc/hosts
    regexp: '^127\.0\.0\.1'
    line: '127.0.0.1   localhost myserver'
    backup: yes
```

## 常见命名规范参考

### 环境标识
- prod：生产环境
- staging：预发布环境
- dev：开发环境
- test：测试环境

### 服务角色
- web：Web 服务器
- db：数据库服务器
- cache：缓存服务器
- app：应用服务器
- mq：消息队列服务器
- monitor：监控服务器
- log：日志服务器

### 完整示例
```
web-prod-01          # 生产 Web 服务器 1
db-prod-primary      # 生产数据库主节点
db-prod-secondary    # 生产数据库从节点
cache-staging-01     # 预发布缓存服务器
app-dev-local        # 开发应用服务器（本地）
monitor-central      # 中央监控服务器
```

## 相关示例
- [service 模块](../service/README.md) - 服务管理
- [file 模块](../../files/file/README.md) - 文件管理
- [lineinfile 模块](../../files/lineinfile/README.md) - 修改 /etc/hosts 等文件
