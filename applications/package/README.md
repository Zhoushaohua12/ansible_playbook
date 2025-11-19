# package 模块使用指南

## 模块简介
`ansible.builtin.package` 模块是跨平台的通用包管理器，能够根据目标操作系统自动选择合适的包管理工具（如 yum、apt、dnf、zypper 等）。该模块提供了一个统一的接口来管理软件包的安装、更新和删除，是实现跨平台自动化部署的理想选择。

## 主要参数

### 基础配置
- `name`：软件包名称，可以是字符串或列表
- `state`：包状态，可选值：
  - `present`：确保包已安装（默认）
  - `absent`：确保包已删除
  - `latest`：确保包是最新版本
  - `installed`：确保包已安装（同 present）
  - `removed`：确保包已删除（同 absent）

### 版本控制
- `version`：指定要安装的包版本
- `use`：强制使用指定的包管理器（如 `apt`、`yum`）

### 高级选项
- `update_cache`：是否更新包缓存（默认：false）
- `update_cache_retries`：更新缓存重试次数
- `update_cache_retry_max_delay`：更新缓存重试最大延迟
- `cache_valid_time`：缓存有效时间（秒）

### 批量操作
- `name` 参数支持列表格式，可同时管理多个包：
```yaml
- name: 安装多个软件包
  ansible.builtin.package:
    name:
      - nginx
      - redis
      - git
    state: present
```

## 返回值
- `changed`：是否执行了变更操作
- `msg`：操作结果描述信息
- `results`：批量操作时的详细结果列表

## 常见使用场景

### 1. 基础软件包安装
```yaml
- name: 安装基础开发工具
  ansible.builtin.package:
    name:
      - git
      - curl
      - wget
      - vim
    state: present
    update_cache: true
```

### 2. Web 服务器部署
```yaml
- name: 安装 Web 服务器软件
  ansible.builtin.package:
    name: "{{ web_server_package }}"
    state: present
    update_cache: true

- name: 确保 Web 服务器为最新版本
  ansible.builtin.package:
    name: "{{ web_server_package }}"
    state: latest
```

### 3. 数据库服务安装
```yaml
- name: 安装数据库服务
  ansible.builtin.package:
    name:
      - "{{ database_package }}"
      - "{{ database_client_package }}"
    state: present
    update_cache: true

- name: 安装指定版本的数据库
  ansible.builtin.package:
    name: "{{ database_package }}"
    version: "13.4"
    state: present
```

### 4. 应用依赖管理
```yaml
- name: 安装 Python 应用依赖
  ansible.builtin.package:
    name:
      - python3
      - python3-pip
      - python3-venv
      - python3-dev
    state: present

- name: 安装 Node.js 应用依赖
  ansible.builtin.package:
    name:
      - nodejs
      - npm
    state: latest
```

### 5. 系统工具和监控
```yaml
- name: 安装系统监控工具
  ansible.builtin.package:
    name:
      - htop
      - iotop
      - nethogs
      - sysstat
    state: present

- name: 安装安全工具
  ansible.builtin.package:
    name:
      - fail2ban
      - ufw
      - rkhunter
    state: present
```

## 支持的包管理器

### Linux 系统
- **Debian/Ubuntu**：apt/apt-get
- **Red Hat/CentOS/Fedora**：yum/dnf
- **SUSE/openSUSE**：zypper
- **Arch Linux**：pacman
- **Alpine Linux**：apk

### 其他系统
- **FreeBSD**：pkg
- **macOS**：homebrew（需要安装）

## 平台差异处理

### 包名称差异
不同系统的包名称可能不同，建议使用变量管理：
```yaml
- name: 安装 Web 服务器（跨平台）
  ansible.builtin.package:
    name: "{{ web_server_packages[ansible_os_family] }}"
    state: present

# 在 vars 中定义
web_server_packages:
  Debian: ["apache2", "libapache2-mod-php"]
  RedHat: ["httpd", "php"]
  Suse: ["apache2", "php7"]
```

### 版本格式差异
不同系统的版本格式可能不同：
```yaml
- name: 安装指定版本（处理平台差异）
  ansible.builtin.package:
    name: "{{ app_package }}"
    version: "{{ app_version[ansible_os_family] }}"
    state: present
```

## 安全注意事项

### 包源安全
- 使用官方或可信的软件源
- 定期更新软件源密钥
- 验证包的完整性签名

### 版本控制
- 锁定关键软件包版本确保稳定性
- 在测试环境验证新版本兼容性
- 建立软件包版本审批流程

### 权限管理
- 包管理操作需要 root 权限
- 使用 become 提权时遵循最小权限原则
- 记录包安装/删除操作日志

## 最佳实践

### 幂等性设计
- 使用 `state: present` 确保包存在
- 避免重复安装已存在的包
- 合理使用 `update_cache` 参数

### 性能优化
- 批量安装多个包减少操作次数
- 合理设置缓存更新频率
- 使用本地镜像源加速下载

### 错误处理
- 处理包不存在的情况
- 处理网络连接问题
- 处理依赖冲突问题

## 测试步骤
1. 确认目标系统的包管理器
2. 在 `vars/example_vars.yml` 中配置包列表
3. 使用 `--check` 模式预览安装计划
4. 验证包安装后的功能
5. 检查包版本和依赖关系

## 常见问题
- **包不存在**：检查包名称和软件源配置
- **版本冲突**：解决依赖关系或使用特定版本
- **网络问题**：检查网络连接和代理设置
- **权限问题**：确认有足够的权限执行包管理

## 相关模块
- [yum](../yum/README.md) - Red Hat 系统包管理
- [apt](../apt/README.md) - Debian 系统包管理
- [pip](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/pip_module.html) - Python 包管理
- [gem](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/gem_module.html) - Ruby 包管理

## 跨平台示例

### 完整的跨平台应用部署
```yaml
- name: 跨平台应用依赖安装
  hosts: all
  become: true
  vars:
    app_packages:
      Debian:
        - python3
        - python3-pip
        - python3-venv
        - nginx
      RedHat:
        - python3
        - python3-pip
        - python3-virtualenv
        - nginx
      Suse:
        - python3
        - python3-pip
        - python3-virtualenv
        - nginx

  tasks:
    - name: 更新包缓存
      ansible.builtin.package:
        update_cache: true
      when: ansible_os_family == "Debian"

    - name: 安装应用依赖包
      ansible.builtin.package:
        name: "{{ app_packages[ansible_os_family] }}"
        state: present
```
