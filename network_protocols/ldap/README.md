# LDAP 协议模块使用指南

## 模块用途
`community.general.ldap_*` 系列模块用于与 LDAP（轻量级目录访问协议）服务器进行交互，支持用户认证、目录查询、条目管理、属性修改等操作。适用于统一身份认证、目录服务管理、用户信息同步等场景。

## 主要模块

### ldap_search 模块
用于搜索 LDAP 目录中的条目。

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `server_uri` | str | LDAP 服务器 URI（必需） | `ldap://ldap.example.com`、`ldaps://ldap.example.com` |
| `bind_dn` | str | 绑定 DN（可选） | `cn=admin,dc=example,dc=com` |
| `bind_pw` | str | 绑定密码（可选） | `{{ vault_ldap_password }}` |
| `dn` | str | 搜索基础 DN（必需） | `ou=users,dc=example,dc=com` |
| `scope` | str | 搜索范围（base、one、sub、children） | `sub` |
| `filter` | str | LDAP 过滤器（必需） | `(objectClass=inetOrgPerson)`、`(uid=username)` |
| `attrs` | list | 要返回的属性列表（可选） | `['uid', 'cn', 'mail']` |
| `sizelimit` | int | 返回结果数量限制（可选） | 100、500 等 |
| `timelimit` | int | 搜索超时时间（秒，可选） | 30、60 等 |

### ldap_entry 模块
用于管理 LDAP 目录条目（创建、修改、删除）。

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `server_uri` | str | LDAP 服务器 URI（必需） | `ldap://ldap.example.com` |
| `bind_dn` | str | 绑定 DN（可选） | `cn=admin,dc=example,dc=com` |
| `bind_pw` | str | 绑定密码（可选） | `{{ vault_ldap_password }}` |
| `dn` | str | 目标条目 DN（必需） | `uid=john,ou=users,dc=example,dc=com` |
| `state` | str | 条目状态（present、absent、exact） | present、absent、exact |
| `attributes` | dict | 条目属性（必需） | `{'objectClass': ['inetOrgPerson'], 'cn': 'John Doe'}` |
| `validate_certs` | bool | 是否验证证书（默认 true） | true、false |

### ldap_attr 模块
用于修改 LDAP 条目的特定属性。

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `server_uri` | str | LDAP 服务器 URI（必需） | `ldap://ldap.example.com` |
| `bind_dn` | str | 绑定 DN（可选） | `cn=admin,dc=example,dc=com` |
| `bind_pw` | str | 绑定密码（可选） | `{{ vault_ldap_password }}` |
| `dn` | str | 目标条目 DN（必需） | `uid=john,ou=users,dc=example,dc=com` |
| `name` | str | 属性名称（必需） | `mail`、`telephoneNumber` |
| `values` | list | 属性值列表（必需） | `['john@example.com']` |
| `state` | str | 属性状态（present、absent、exact） | present、absent、exact |
| `validate_certs` | bool | 是否验证证书（默认 true） | true、false |

### ldap_passwd 模块
用于修改 LDAP 用户密码。

| 参数 | 类型 | 说明 | 常用值 |
|------|------|------|--------|
| `server_uri` | str | LDAP 服务器 URI（必需） | `ldap://ldap.example.com` |
| `bind_dn` | str | 绑定 DN（可选） | `cn=admin,dc=example,dc=com` |
| `bind_pw` | str | 绑定密码（可选） | `{{ vault_ldap_password }}` |
| `dn` | str | 目标用户 DN（必需） | `uid=john,ou=users,dc=example,dc=com` |
| `passwd` | str | 新密码（必需） | `{{ vault_new_password }}` |
| `validate_certs` | bool | 是否验证证书（默认 true） | true、false |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否执行了修改 | true/false |
| `results` | 搜索结果或操作结果 | LDAP 条目列表 |
| `msg` | 操作结果消息 | "Search completed successfully" |
| `count` | 搜索结果数量 | 25 |

## 使用情境

### 用户认证和授权
- **用户登录验证**：验证用户凭据的有效性
- **权限查询**：查询用户组和权限信息
- **单点登录**：集成 SSO 系统进行身份认证
- **密码管理**：批量修改用户密码

### 目录服务管理
- **用户管理**：创建、修改、删除用户账户
- **组织架构**：管理组织单位和部门结构
- **联系人管理**：维护员工联系信息
- **群组管理**：管理用户组和权限分配

### 数据同步和集成
- **HR 系统同步**：与人力资源系统同步员工信息
- **应用集成**：为应用系统提供统一的用户目录
- **数据迁移**：在不同 LDAP 服务器间迁移数据
- **备份恢复**：备份和恢复 LDAP 目录数据

## 安全注意事项

### 连接安全
1. **SSL/TLS 加密**：使用 LDAPS 或 StartTLS 保护连接
2. **证书验证**：启用服务器证书验证
3. **连接超时**：设置合理的连接和操作超时
4. **网络隔离**：限制 LDAP 服务器的网络访问

### 认证安全
1. **强密码策略**：使用强密码并定期更换
2. **最小权限**：绑定账户使用最小必要权限
3. **密码保护**：使用 Ansible Vault 保护密码
4. **审计日志**：启用 LDAP 操作审计日志

### 数据安全
1. **敏感属性**：谨慎处理敏感目录属性
2. **访问控制**：配置适当的 LDAP ACL
3. **数据脱敏**：在日志中隐藏敏感信息
4. **备份加密**：加密 LDAP 数据备份

## 环境依赖

### 必需
- Python ldap 库（`python-ldap` 或 `python3-ldap`）
- LDAP 服务器访问权限
- 目标主机的网络连接

### 推荐
- OpenLDAP 客户端工具
- TLS/SSL 证书配置
- 网络时间同步

## 常见问题

### 1. 连接超时
**可能原因**：
- 网络连接问题
- LDAP 服务器负载过高
- 防火墙阻止连接
- 服务器地址错误

**解决方案**：
```yaml
- name: 增加连接超时时间
  community.general.ldap_search:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "{{ search_base }}"
    filter: "{{ search_filter }}"
    timelimit: 60
    sizelimit: 1000
```

### 2. 认证失败
**可能原因**：
- 绑定 DN 错误
- 密码错误
- 权限不足
- 账户被锁定

**解决方案**：
```yaml
- name: 使用正确的绑定凭据
  community.general.ldap_search:
    server_uri: "{{ ldap_server }}"
    bind_dn: "cn=admin,dc=example,dc=com"
    bind_pw: "{{ vault_admin_password }}"
    dn: "ou=users,dc=example,dc=com"
    filter: "(objectClass=inetOrgPerson)"
```

### 3. 搜索无结果
**可能原因**：
- 搜索基础 DN 错误
- 过滤器语法错误
- 权限不足
- 条目不存在

**解决方案**：
```yaml
- name: 使用正确的搜索语法
  community.general.ldap_search:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "ou=users,dc=example,dc=com"
    filter: "(&(objectClass=inetOrgPerson)(uid={{ username }}))"
    attrs: ["uid", "cn", "mail"]
```

## 最佳实践

### 基础 LDAP 搜索示例
```yaml
- name: 搜索所有用户
  community.general.ldap_search:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "ou=users,dc=example,dc=com"
    filter: "(objectClass=inetOrgPerson)"
    attrs: ["uid", "cn", "mail", "telephoneNumber"]
  register: ldap_users
  no_log: true  # 保护绑定密码

- name: 显示搜索结果
  ansible.builtin.debug:
    msg: "找到 {{ ldap_users.results | length }} 个用户"
```

### 特定用户查询示例
```yaml
- name: 查询特定用户信息
  community.general.ldap_search:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "ou=users,dc=example,dc=com"
    filter: "(&(objectClass=inetOrgPerson)(uid={{ username }}))"
    attrs: ["uid", "cn", "mail", "departmentNumber"]
  register: user_info
  no_log: true

- name: 显示用户信息
  ansible.builtin.debug:
    msg: "用户信息: {{ user_info.results }}"
  when: user_info.results | length > 0
```

### 创建 LDAP 用户示例
```yaml
- name: 创建新的 LDAP 用户
  community.general.ldap_entry:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "uid={{ new_user.uid }},ou=users,dc=example,dc=com"
    state: present
    attributes:
      objectClass:
        - inetOrgPerson
        - organizationalPerson
        - person
        - top
      uid: "{{ new_user.uid }}"
      cn: "{{ new_user.cn }}"
      sn: "{{ new_user.sn }}"
      givenName: "{{ new_user.givenName }}"
      mail: "{{ new_user.mail }}"
      telephoneNumber: "{{ new_user.telephoneNumber }}"
      userPassword: "{{ vault_user_password }}"
  no_log: true
```

### 修改用户属性示例
```yaml
- name: 修改用户邮箱地址
  community.general.ldap_attr:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "uid={{ username }},ou=users,dc=example,dc=com"
    name: mail
    values:
      - "{{ new_email }}"
    state: present
  no_log: true

- name: 修改用户电话号码
  community.general.ldap_attr:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "uid={{ username }},ou=users,dc=example,dc=com"
    name: telephoneNumber
    values:
      - "{{ new_phone }}"
    state: exact  # 替换现有值
  no_log: true
```

### 修改用户密码示例
```yaml
- name: 修改用户密码
  community.general.ldap_passwd:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "uid={{ username }},ou=users,dc=example,dc=com"
    passwd: "{{ vault_new_password }}"
    validate_certs: yes
  no_log: true
  register: password_change

- name: 显示密码修改结果
  ansible.builtin.debug:
    msg: "密码修改: {{ '成功' if password_change.changed else '无变化' }}"
```

### 删除用户示例
```yaml
- name: 删除 LDAP 用户
  community.general.ldap_entry:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "uid={{ username }},ou=users,dc=example,dc=com"
    state: absent
  no_log: true
```

### 批量用户管理示例
```yaml
- name: 批量创建用户
  community.general.ldap_entry:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "uid={{ item.uid }},ou=users,dc=example,dc=com"
    state: present
    attributes:
      objectClass:
        - inetOrgPerson
        - organizationalPerson
        - person
        - top
      uid: "{{ item.uid }}"
      cn: "{{ item.cn }}"
      sn: "{{ item.sn }}"
      mail: "{{ item.mail }}"
      userPassword: "{{ item.password }}"
  loop: "{{ new_users }}"
  no_log: true
  loop_control:
    label: "{{ item.uid }}"
```

### 组管理示例
```yaml
- name: 创建用户组
  community.general.ldap_entry:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "cn={{ group_name }},ou=groups,dc=example,dc=com"
    state: present
    attributes:
      objectClass:
        - groupOfNames
        - top
      cn: "{{ group_name }}"
      description: "{{ group_description }}"
      member:
        - "uid=user1,ou=users,dc=example,dc=com"
        - "uid=user2,ou=users,dc=example,dc=com"
  no_log: true

- name: 向组中添加成员
  community.general.ldap_attr:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "cn={{ group_name }},ou=groups,dc=example,dc=com"
    name: member
    values:
      - "uid={{ new_member }},ou=users,dc=example,dc=com"
    state: present
  no_log: true
```

### SSL/TLS 连接示例
```yaml
- name: 使用安全连接查询 LDAP
  community.general.ldap_search:
    server_uri: "ldaps://{{ ldap_server }}:636"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "ou=users,dc=example,dc=com"
    filter: "(objectClass=inetOrgPerson)"
    validate_certs: yes
    attrs: ["uid", "cn", "mail"]
  register: secure_search
  no_log: true
```

### 条件操作示例
```yaml
- name: 检查用户是否存在
  community.general.ldap_search:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "ou=users,dc=example,dc=com"
    filter: "(uid={{ username }})"
    attrs: ["uid"]
  register: user_check
  no_log: true

- name: 用户存在时更新属性
  community.general.ldap_attr:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "uid={{ username }},ou=users,dc=example,dc=com"
    name: mail
    values:
      - "{{ new_email }}"
    state: present
  no_log: true
  when: user_check.results | length > 0

- name: 用户不存在时创建用户
  community.general.ldap_entry:
    server_uri: "{{ ldap_server }}"
    bind_dn: "{{ ldap_bind_dn }}"
    bind_pw: "{{ vault_ldap_password }}"
    dn: "uid={{ username }},ou=users,dc=example,dc=com"
    state: present
    attributes:
      objectClass:
        - inetOrgPerson
        - organizationalPerson
        - person
        - top
      uid: "{{ username }}"
      cn: "{{ user_cn }}"
      sn: "{{ user_sn }}"
      mail: "{{ user_email }}"
  no_log: true
  when: user_check.results | length == 0
```

## 相关示例
- [uri 模块](../uri/README.md) - HTTP/HTTPS API 调用
- [dns 模块](../dns/README.md) - DNS 查询管理
- [ping 模块](../ping/README.md) - ICMP 连通性检查
- [user 模块](../../system/user/README.md) - 系统用户管理