# apt 模块使用指南

## 模块简介
`ansible.builtin.apt` 模块是专门用于 Debian 系列发行版（如 Debian、Ubuntu、Linux Mint）的包管理工具。该模块提供了完整的 DEB 包管理功能，包括安装、更新、删除软件包，以及管理软件源和软件依赖，是 Debian 生态系统中应用部署的核心工具。

## 主要参数

### 基础操作
- `name`：软件包名称，支持字符串、列表或字典格式
- `state`：包状态，可选值：
  - `present`：确保包已安装（默认）
  - `absent`：确保包已删除
  - `latest`：确保包为最新版本
  - `installed`：确保包已安装（同 present）
  - `removed`：确保包已删除（同 absent）
  - `build-dep`：安装构建依赖

### 缓存管理
- `update_cache`：是否更新 apt 缓存（默认：false）
- `cache_valid_time`：缓存有效时间（秒，默认：0）
- `update_cache_retries`：更新缓存重试次数（默认：0）
- `update_cache_retry_max_delay`：更新缓存重试最大延迟（默认：0）

### 版本控制
- `version`：指定要安装的包版本
- `default_release`：指定默认发行版
- `install_recommends`：是否安装推荐的包（默认：true）
- `only_upgrade`：仅升级已安装的包

### 仓库管理
- `deb`：添加 DEB 仓库源
- `state=present` 与 `deb` 参数配合添加仓库源

### 高级选项
- `allow_unauthenticated`：是否允许未认证的包（默认：false）
- `autoremove`：是否自动移除不需要的依赖（默认：false）
- `autoclean`：是否自动清理缓存（默认：false）
- `purge`：是否完全删除包（包括配置文件）
- `dpkg_options`：dpkg 选项

### 高级包选择
```yaml
# 使用字典格式指定版本
- name: 安装指定版本的包
  ansible.builtin.apt:
    name:
      nginx: "1.18.0-0ubuntu1"
      php: "7.4.25"
    state: present

# 安装构建依赖
- name: 安装软件包的构建依赖
  ansible.builtin.apt:
    name: nginx
    state: build-dep
```

## 返回值
- `changed`：是否执行了变更操作
- `stdout`：apt 命令的标准输出
- `stderr`：apt 命令的错误输出
- `cache_update_time`：缓存更新时间
- `msg`：操作结果描述信息

## 常见使用场景

### 1. 基础软件包安装
```yaml
- name: 更新 apt 缓存并安装基础工具
  ansible.builtin.apt:
    name:
      - vim
      - curl
      - wget
      - unzip
    state: present
    update_cache: true
    cache_valid_time: 3600
```

### 2. Web 服务器部署
```yaml
- name: 安装 Nginx Web 服务器
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: true

- name: 确保 Nginx 为最新版本
  ansible.builtin.apt:
    name: nginx
    state: latest
    update_cache: true

- name: 安装 Apache 和 PHP
  ansible.builtin.apt:
    name:
      - apache2
      - php7.4
      - libapache2-mod-php7.4
    state: present
```

### 3. 数据库服务安装
```yaml
- name: 安装 PostgreSQL 数据库
  ansible.builtin.apt:
    name:
      - postgresql
      - postgresql-contrib
      - postgresql-client
    state: present
    update_cache: true

- name: 安装指定版本的 MariaDB
  ansible.builtin.apt:
    name: mariadb-server
    version: "1:10.5.12-0ubuntu0.21.04.1"
    state: present
```

### 4. 开发环境配置
```yaml
- name: 安装构建工具
  ansible.builtin.apt:
    name:
      - build-essential
      - cmake
      - git
      - make
    state: present

- name: 安装 Python 开发环境
  ansible.builtin.apt:
    name:
      - python3
      - python3-pip
      - python3-dev
      - python3-venv
      - python3-setuptools
    state: present
    install_recommends: false
```

### 5. 仓库源管理
```yaml
- name: 添加 Docker 官方仓库
  ansible.builtin.apt:
    name: "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
    state: present
    update_cache: true

- name: 添加 PPA 仓库
  ansible.builtin.apt_repository:
    repo: ppa:ondrej/php
    state: present
    update_cache: true
```

### 6. 系统更新管理
```yaml
- name: 更新所有软件包
  ansible.builtin.apt:
    name: "*"
    state: latest
    update_cache: true
    autoremove: true
    autoclean: true

- name: 仅升级安全更新
  ansible.builtin.apt:
    upgrade: dist
    update_cache: true
    only_upgrade: true
```

## 仓库源管理

### 添加软件源
```yaml
- name: 添加第三方软件源
  ansible.builtin.apt:
    deb: "deb https://packages.example.com/ubuntu focal main"
    state: present

- name: 添加带签名的软件源
  ansible.builtin.apt:
    deb: "deb [signed-by=/usr/share/keyrings/example-archive-keyring.gpg] https://packages.example.com/ubuntu focal main"
    state: present
```

### 使用 apt_repository 模块
```yaml
- name: 添加 NodeSource 仓库
  ansible.builtin.apt_repository:
    repo: "deb https://deb.nodesource.com/node_16.x focal main"
    state: present
    update_cache: true

- name: 添加 PPA 仓库
  ansible.builtin.apt_repository:
    repo: "ppa:deadsnakes/ppa"
    state: present
```

## 版本管理策略

### 锁定版本
```yaml
- name: 锁定关键软件包版本
  ansible.builtin.apt:
    name:
      nginx: "1.18.0-0ubuntu1"
      php7.4: "7.4.25-1ubuntu1.1"
    state: present
```

### 包状态管理
```yaml
- name: 完全删除软件包（包括配置文件）
  ansible.builtin.apt:
    name: old-package
    state: absent
    purge: true
    autoremove: true
```

## 安全注意事项

### 包验证
- 保持 GPG 验证启用以确保包完整性
- 定期更新仓库密钥
- 对可信仓库可临时禁用验证

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
  ansible.builtin.apt:
    name: "{{ app_dependencies }}"
    state: present
    update_cache: true
    cache_valid_time: 3600
```

### 条件安装
```yaml
- name: 根据发行版安装软件包
  ansible.builtin.apt:
    name: "{{ ubuntu_packages if ansible_distribution == 'Ubuntu' else debian_packages }}"
    state: present
```

### 缓存优化
```yaml
- name: 智能缓存更新
  ansible.builtin.apt:
    update_cache: true
    cache_valid_time: 3600  # 仅在缓存过期时更新
  when: apt_cache_update_needed | default(true)
```

## 性能优化

### 网络优化
```yaml
- name: 配置 apt 镜像源
  ansible.builtin.template:
    src: sources.list.j2
    dest: /etc/apt/sources.list
    backup: true
  notify: update apt cache
```

### 并发控制
```yaml
- name: 安装软件包（设置超时）
  ansible.builtin.apt:
    name: "{{ package_list }}"
    state: present
  async: 300
  poll: 10
```

## 测试步骤
1. 确认目标系统为 Debian 系列发行版
2. 在 `vars/example_vars.yml` 中配置包列表和版本
3. 使用 `--check` 模式预览安装计划
4. 验证包安装后的功能和版本
5. 检查依赖关系和系统兼容性

## 常见问题
- **依赖冲突**：解决版本冲突或使用 `allow_unauthenticated`
- **网络问题**：检查网络连接和仓库配置
- **GPG 错误**：更新 GPG 密钥或检查仓库签名
- **权限问题**：确认有足够的权限执行操作
- **锁文件问题**：检查是否有其他 apt 进程在运行

## 相关模块
- [package](../package/README.md) - 跨平台包管理
- [yum](../yum/README.md) - Red Hat 系统包管理
- [apt_repository](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_repository_module.html) - APT 仓库管理
- [apt_key](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_key_module.html) - APT 密钥管理

## 发行版兼容性

### Ubuntu 版本支持
```yaml
- name: 根据 Ubuntu 版本选择软件包
  ansible.builtin.apt:
    name: "{{ ubuntu_packages[ansible_distribution_version] }}"
    state: present

# 在 vars 中定义
ubuntu_packages:
  "20.04": ["nginx", "php7.4"]
  "22.04": ["nginx", "php8.1"]
  "24.04": ["nginx", "php8.3"]
```

### Debian 版本支持
```yaml
- name: 根据 Debian 版本选择软件包
  ansible.builtin.apt:
    name: "{{ debian_packages[ansible_distribution_major_version] }}"
    state: present

# 在 vars 中定义
debian_packages:
  "10": ["nginx", "php7.3"]
  "11": ["nginx", "php7.4"]
  "12": ["nginx", "php8.2"]
```

## 与现代包管理工具的集成

### Snap 包支持
```yaml
- name: 安装 snap 包
  community.general.snap:
    name: docker
    classic: true
```

### Flatpak 包支持
```yaml
- name: 安装 flatpak 包
  community.general.flatpak:
    name: org.mozilla.firefox
    state: present
```
