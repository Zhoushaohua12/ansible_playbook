# 数据库模块实践指南

## 章节概述
本目录提供主流数据库系统（MySQL、PostgreSQL、MongoDB）的 Ansible 自动化管理示例，涵盖用户管理、数据库创建、权限授予等常见运维场景。所有示例均通过 check_mode 或 delegate_to 方式运行，适合在本地环境学习和测试。

## 环境要求

### Ansible Collection 依赖
在运行示例前，请先安装对应的 Ansible Collection：

```bash
# MySQL 模块依赖
ansible-galaxy collection install community.mysql

# PostgreSQL 模块依赖
ansible-galaxy collection install community.postgresql

# MongoDB 模块依赖
ansible-galaxy collection install community.mongodb
```

### Python 库依赖
各数据库模块需要在**目标主机**上安装对应的 Python 客户端库：

```bash
# MySQL 客户端库（任选其一）
pip install PyMySQL
# 或
pip install mysqlclient

# PostgreSQL 客户端库
pip install psycopg2-binary

# MongoDB 客户端库
pip install pymongo
```

⚠️ **重要提示**：以上 Python 库需要安装在 **目标数据库主机** 上，而非 Ansible 控制节点。如果使用 delegate_to 或 localhost 模式，则在相应主机上安装。

## 模块列表

### MySQL 用户管理
- **模块**: `community.mysql.mysql_user`
- **文档**: [mysql_user/README.md](mysql_user/README.md)
- **示例**: [mysql_user/playbook.yml](mysql_user/playbook.yml)
- **功能**: 创建/删除 MySQL 用户，授予/撤销权限，管理密码

### MySQL 数据库管理
- **模块**: `community.mysql.mysql_db`
- **文档**: [mysql_db/README.md](mysql_db/README.md)
- **示例**: [mysql_db/playbook.yml](mysql_db/playbook.yml)
- **功能**: 创建/删除数据库，导入/导出 SQL 文件，设置字符集和排序规则

### PostgreSQL 数据库管理
- **模块**: `community.postgresql.postgresql_db`
- **文档**: [postgresql_db/README.md](postgresql_db/README.md)
- **示例**: [postgresql_db/playbook.yml](postgresql_db/playbook.yml)
- **功能**: 创建/删除 PostgreSQL 数据库，设置 owner 和 encoding

### PostgreSQL 用户管理
- **模块**: `community.postgresql.postgresql_user`
- **文档**: [postgresql_user/README.md](postgresql_user/README.md)
- **示例**: [postgresql_user/playbook.yml](postgresql_user/playbook.yml)
- **功能**: 创建/删除 PostgreSQL 用户，授予/撤销权限，管理角色和密码

### MongoDB 用户管理
- **模块**: `community.mongodb.mongodb_user`
- **文档**: [mongodb_user/README.md](mongodb_user/README.md)
- **示例**: [mongodb_user/playbook.yml](mongodb_user/playbook.yml)
- **功能**: 创建/删除 MongoDB 用户，配置角色和权限

## 安全注意事项

### 凭证管理
1. **禁止硬编码密码**：所有示例使用占位符变量，实际使用时应配合 Ansible Vault 加密
2. **最小权限原则**：为不同应用创建专用数据库用户，限制权限范围
3. **定期轮换密码**：建立定期更新数据库密码的流程
4. **审计日志**：使用 `no_log: true` 防止敏感信息写入 Ansible 日志

### 连接安全
1. **使用加密连接**：生产环境建议启用 SSL/TLS 连接
2. **限制访问源**：通过防火墙和数据库配置限制访问 IP 范围
3. **专用管理账号**：使用专门的自动化管理账号，避免使用 root 或超级用户

### 变更管理
1. **测试优先**：所有变更应先在测试环境验证
2. **使用 check_mode**：执行前使用 `--check` 预览变更内容
3. **备份保障**：重要操作前先备份数据库
4. **版本控制**：将 Playbook 和变量文件纳入版本控制系统

## 使用方式

### 本地 check_mode 测试
适用于学习和语法验证，不会实际连接数据库：

```bash
ansible-playbook database/mysql_user/playbook.yml --check
```

### 使用 delegate_to 远程管理
在 playbook 中使用 `delegate_to` 指定数据库服务器：

```yaml
- name: 创建 MySQL 用户
  community.mysql.mysql_user:
    name: app_user
    password: "{{ db_password }}"
    priv: "appdb.*:ALL"
  delegate_to: db.example.com
```

### 配合 vars_prompt 交互输入
使用 `vars_prompt` 在运行时输入敏感信息：

```yaml
- name: 数据库用户管理
  hosts: localhost
  vars_prompt:
    - name: db_password
      prompt: "请输入数据库密码"
      private: true
  tasks:
    - name: 创建用户
      community.mysql.mysql_user:
        name: "{{ db_user }}"
        password: "{{ db_password }}"
```

## 快速开始

### 1. 安装依赖
```bash
# 安装 Ansible Collection
ansible-galaxy collection install community.mysql community.postgresql community.mongodb

# 在目标主机安装 Python 库（示例：MySQL）
pip install PyMySQL
```

### 2. 配置变量
编辑 `vars/example_vars.yml`，替换占位符为实际值（建议使用 Ansible Vault 加密）。

### 3. 语法检查
```bash
ansible-playbook database/mysql_user/playbook.yml --syntax-check
```

### 4. 预览变更
```bash
ansible-playbook database/mysql_user/playbook.yml --check
```

### 5. 执行部署
```bash
ansible-playbook database/mysql_user/playbook.yml
```

## 常见问题

### 连接失败
- 检查数据库服务是否启动
- 验证防火墙规则和端口开放（MySQL:3306, PostgreSQL:5432, MongoDB:27017）
- 确认 Python 客户端库已安装在目标主机
- 检查数据库配置允许远程连接（bind_address、pg_hba.conf 等）

### 权限不足
- 确认 Ansible 使用的数据库账号具有管理权限
- MySQL 需要 GRANT 权限，PostgreSQL 需要 SUPERUSER 或 CREATEROLE 权限
- MongoDB 需要 userAdminAnyDatabase 或相应角色

### 模块未找到
- 运行 `ansible-galaxy collection list` 检查 collection 是否已安装
- 确认使用正确的 FQCN（如 community.mysql.mysql_user）
- 更新 Ansible 到最新版本：`pip install --upgrade ansible`

## 相关链接
- [MySQL 用户管理](mysql_user/README.md) - MySQL 用户创建和权限管理
- [MySQL 数据库管理](mysql_db/README.md) - MySQL 数据库和表管理
- [PostgreSQL 数据库管理](postgresql_db/README.md) - PostgreSQL 数据库管理
- [PostgreSQL 用户管理](postgresql_user/README.md) - PostgreSQL 用户和角色管理
- [MongoDB 用户管理](mongodb_user/README.md) - MongoDB 用户和角色管理
- [监控模块总览](../monitoring/README.md) - 配合数据库监控使用
- [应用管理指南](../applications/README.md) - 应用部署与数据库集成
