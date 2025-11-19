# group 模块使用指南

## 模块用途
`ansible.builtin.group` 模块用于创建、修改和删除 Linux 用户组，支持指定组 ID (GID)、设置组成员等操作。适用于权限隔离、资源访问控制、与 user 模块协同配置等场景。

## 主要参数

| 参数 | 类型 | 说明 | 常见值 |
|------|------|------|--------|
| `name` | str | 组名称（必需） | wheel、docker、developers 等 |
| `state` | str | 组状态（present 创建/修改，absent 删除） | present、absent |
| `gid` | int | 组 ID（GID），可指定固定值 | 1000、1001、10000 等 |
| `system` | bool | 是否创建为系统组（GID < 1000） | true、false |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `name` | 组名称 | docker |
| `gid` | 组 ID | 1001 |
| `state` | 组状态 | present/absent |
| `changed` | 是否修改了组 | true/false |

## 使用情境

### 创建权限隔离组
**场景**：为不同职能团队创建组，实现细粒度权限控制
- 开发者组：developers，拥有代码仓库的读写权限
- 运维组：ops，拥有配置文件和系统命令的执行权限
- 数据库组：dba，仅数据库管理员可访问数据库文件

### 容器与系统服务访问控制
**场景**：管理特殊系统设备与服务的访问
- docker 组：运行 Docker 容器的用户
- wheel 或 sudo 组：获得 sudo 提权权限
- adm 组：查看系统日志权限
- audio、video 组：多媒体访问权限

### 应用用户的组织
**场景**：为应用创建专用组，隔离数据与权限
- 应用专用组：app_group，关联应用用户与配置文件
- 临时工作组：temp_workers，项目结束后删除

## 安全注意事项

1. **最小权限原则**：仅创建必需的组，避免过度权限
2. **GID 规划**：
   - 系统组：GID < 1000
   - 普通组：GID >= 1000
   - 避免 GID 冲突
3. **组成员管理**：通过 user 模块的 groups 参数添加成员，而非直接修改 /etc/group
4. **删除组前验证**：确保组内没有重要文件或系统依赖
5. **docker 组特殊说明**：docker 组成员可无密码使用 Docker，等同于 root 权限，谨慎使用

## 环境依赖

### 必需
- 目标主机支持 groupadd/groupmod/groupdel 命令
- 必要时需要 root 或 sudo 权限

## 常见问题

### 1. 如何为现有组添加成员？
使用 user 模块而非 group 模块：
```yaml
- name: 为用户添加到 docker 组
  ansible.builtin.user:
    name: deploy
    groups: docker
    append: yes
```

### 2. 删除组时提示组内有成员
需要先删除所有成员，再删除组：
```yaml
- name: 删除用户
  ansible.builtin.user:
    name: "{{ item }}"
    state: absent
  loop: "{{ group_members }}"

- name: 删除组
  ansible.builtin.group:
    name: devops
    state: absent
```

### 3. 不同主机间 GID 冲突
使用固定的 GID 确保多主机一致：
```yaml
- name: 创建一致的组 ID
  ansible.builtin.group:
    name: developers
    gid: 2001
```

## 最佳实践

### 权限隔离组示例
```yaml
- name: 创建开发者组
  ansible.builtin.group:
    name: developers
    gid: 2000
    state: present

- name: 为部署用户加入开发者组
  ansible.builtin.user:
    name: deploy
    groups: developers
    append: yes
```

### 系统组示例
```yaml
- name: 创建系统级应用组
  ansible.builtin.group:
    name: appservice
    system: yes
    state: present
```

### 批量创建组示例
```yaml
- name: 创建多个工作组
  ansible.builtin.group:
    name: "{{ item.name }}"
    gid: "{{ item.gid }}"
    state: present
  loop:
    - { name: 'developers', gid: 2000 }
    - { name: 'sysadmins', gid: 2001 }
    - { name: 'dbadmins', gid: 2002 }
```

## 相关示例
- [user 模块](../user/README.md) - 用户管理与组成员关联
- [file 模块](../../files/file/README.md) - 文件所属组与权限设置
