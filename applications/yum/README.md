# yum 模块使用指南

## 模块简介
`ansible.builtin.yum` 模块是专门用于 Red Hat 系列发行版（如 RHEL、CentOS、Fedora）的包管理工具。该模块提供了完整的 RPM 包管理功能，包括安装、更新、删除软件包，以及管理软件源和软件组，是 Red Hat 生态系统中应用部署的核心工具。

## 主要参数

### 基础操作
- `name`：软件包名称，支持字符串或列表格式
- `state`：包状态，可选值：
  - `present`：确保包已安装（默认）
  - `absent`：确保包已删除
  - `latest`：确保包为最新版本
  - `installed`：确保包已安装（同 present）
  - `removed`：确保包已删除（同 absent）

### 缓存管理
- `update_cache`：是否更新 yum 缓存（默认：false）
- `update_cache_retries`：更新缓存重试次数（默认：0）
- `update_cache_retry_max_delay`：更新缓存重试最大延迟（默认：0）

### 版本控制
- `version`：指定要安装的包版本
- `exclude`：排除的包名称或模式
- `disable_gpg_check`：是否禁用 GPG 检查（默认：false）

### 仓库管理
- `enablerepo`：启用的软件仓库
- `disablerepo`：禁用的软件仓库
- `releasever`：指定发行版本

### 软件组管理
- `name` 参数以 `@` 开头表示软件组：
```yaml
- name: 安装开发工具组
  ansible.builtin.yum:
    name: "@Development Tools"
    state: present
```

### 高级选项
- `allow_downgrade`：是否允许降级（默认：false）
- `autoremove`：是否自动移除不需要的依赖（默认：false）
- `bugfix`：是否仅安装 bugfix 更新（默认：false）
- `security`：是否仅安装安全更新（默认：false）

## 返回值
- `changed`：是否执行了变更操作
- `results`：详细的操作结果列表
- `msg`：操作结果描述信息
- `rc`：命令返回码

## 常见使用场景

### 1. 基础软件包安装
```yaml
- name: 安装基础工具包
  ansible.builtin.yum:
    name:
      - vim
      - curl
      - wget
      - unzip
    state: present
    update_cache: true
```

### 2. Web 服务器部署
```yaml
- name: 安装 Nginx Web 服务器
  ansible.builtin.yum:
    name: nginx
    state: present
    enablerepo: epel  # 启用 EPEL 仓库

- name: 确保 Nginx 为最新版本
  ansible.builtin.yum:
    name: nginx
    state: latest
```

### 3. 数据库服务安装
```yaml
- name: 安装 PostgreSQL 数据库
  ansible.builtin.yum:
    name:
      - postgresql-server
      - postgresql-contrib
      - postgresql-devel
    state: present

- name: 安装指定版本的 MariaDB
  ansible.builtin.yum:
    name: MariaDB-server
    version: "10.5.12-1.el7"
    state: present
```

### 4. 开发环境配置
```yaml
- name: 安装开发工具组
  ansible.builtin.yum:
    name: "@Development Tools"
    state: present

- name: 安装 Python 开发环境
  ansible.builtin.yum:
    name:
      - python3
      - python3-pip
      - python3-devel
      - python3-virtualenv
    state: present
```

### 5. 安全更新管理
```yaml
- name: 仅安装安全更新
  ansible.builtin.yum:
    name: "*"
    state: latest
    security: true

- name: 安装特定安全补丁
  ansible.builtin.yum:
    name: openssl
    state: latest
    bugfix: true
```

### 6. 仓库和源管理
```yaml
- name: 从特定仓库安装包
  ansible.builtin.yum:
    name: docker-ce
    state: present
    enablerepo: docker-ce-stable

- name: 禁用默认仓库安装包
  ansible.builtin.yum:
    name: custom-package
    state: present
    disablerepo: "*"
    enablerepo: custom-repo
```

## 软件组管理

### 常用软件组
```yaml
- name: 安装常用软件组
  ansible.builtin.yum:
    name:
      - "@Development Tools"      # 开发工具
      - "@Web Server"            # Web 服务器
      - "@Database Server"       # 数据库服务器
      - "@System Administration Tools"  # 系统管理工具
      - "@Security Tools"        # 安全工具
    state: present
```

### 查看可用软件组
```bash
# 在目标主机上查看可用软件组
yum grouplist
yum groupinfo "Development Tools"
```

## 版本管理策略

### 锁定版本
```yaml
- name: 锁定关键软件包版本
  ansible.builtin.yum:
    name: "{{ item.name }}"
    version: "{{ item.version }}"
    state: present
  loop:
    - { name: "nginx", version: "1.18.0-1.el8" }
    - { name: "postgresql", version: "12.7-1.el8" }
```

### 版本排除
```yaml
- name: 排除特定版本的包
  ansible.builtin.yum:
    name: "*"
    state: latest
    exclude: "kernel*,nginx-*"  # 排除内核和 nginx 更新
```

## 安全注意事项

### GPG 验证
- 保持 GPG 检查启用以确保包完整性
- 定期更新 GPG 密钥
- 对可信仓库可临时禁用检查

### 仓库安全
- 使用官方或受信任的第三方仓库
- 验证仓库配置文件的完整性
- 定期检查仓库可用性和安全性

### 权限控制
- 包管理操作需要 root 权限
- 使用 become 提权时遵循最小权限原则
- 记录所有包管理操作日志

## 最佳实践

### 批量操作
```yaml
- name: 批量安装应用依赖
  ansible.builtin.yum:
    name: "{{ app_dependencies }}"
    state: present
    update_cache: true
```

### 条件安装
```yaml
- name: 根据角色安装软件包
  ansible.builtin.yum:
    name: "{{ web_packages if server_role == 'web' else db_packages }}"
    state: present
  when: server_role in ['web', 'database']
```

### 错误处理
```yaml
- name: 安全安装软件包（忽略不存在的包）
  ansible.builtin.yum:
    name: "{{ item }}"
    state: present
  loop: "{{ packages_list }}"
  ignore_errors: true
  register: yum_result
```

## 性能优化

### 缓存管理
```yaml
- name: 更新 yum 缓存
  ansible.builtin.yum:
    update_cache: true
    update_cache_retries: 3
    update_cache_retry_max_delay: 10
```

### 并发控制
```yaml
- name: 安装软件包（设置超时）
  ansible.builtin.yum:
    name: "{{ package_list }}"
    state: present
  async: 300
  poll: 10
```

## 测试步骤
1. 确认目标系统为 Red Hat 系列发行版
2. 在 `vars/example_vars.yml` 中配置包列表和版本
3. 使用 `--check` 模式预览安装计划
4. 验证包安装后的功能和版本
5. 检查依赖关系和系统兼容性

## 常见问题
- **依赖冲突**：解决版本冲突或使用 `allow_downgrade`
- **网络问题**：检查网络连接和仓库配置
- **GPG 错误**：更新 GPG 密钥或检查仓库配置
- **权限问题**：确认有足够的权限执行操作

## 相关模块
- [package](../package/README.md) - 跨平台包管理
- [apt](../apt/README.md) - Debian 系统包管理
- [dnf](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/dnf_module.html) - Fedora/RHEL 8+ 包管理
- [rpm](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/rpm_module.html) - RPM 包直接管理

## 与现代包管理器的兼容性

### DNF 兼容性
在 RHEL 8+ 和 Fedora 系统上，yum 模块会自动调用 dnf：
```yaml
- name: 在 RHEL 8+ 上安装包（自动使用 dnf）
  ansible.builtin.yum:
    name: nginx
    state: present
```

### 版本检测
```yaml
- name: 根据系统版本选择包管理策略
  ansible.builtin.yum:
    name: "{{ package_name }}"
    state: "{{ 'latest' if ansible_distribution_version is version('8', '>=') else 'present' }}"
```
