# get_url 模块使用指南

## 模块用途
`ansible.builtin.get_url` 模块用于从 HTTP、HTTPS 或 FTP 服务器下载文件到远程主机。它支持多种下载方式，包括基本认证、自定义头部、校验和验证等功能。在软件包下载、配置文件获取、资源文件部署等场景中，这是实现文件远程获取的核心工具。

## 主要参数

| 参数 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `url` | str | 下载文件的 URL 地址 | https://example.com/file.tar.gz |
| `dest` | str | 目标文件路径（远程主机） | /tmp/file.tar.gz |
| `mode` | str | 文件权限模式 | '0644'、'0755' |
| `owner` | str | 文件所有者 | root、www-data |
| `group` | str | 文件所属组 | root、www-data |
| `checksum` | str | 文件校验和验证 | sha256:abc123... |
| `timeout` | int | 下载超时时间（秒） | 60 |
| `headers` | dict | 自定义 HTTP 头部 | {'Authorization': 'Bearer token'} |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否下载了新文件 | true/false |
| `dest` | 目标文件路径 | /tmp/file.tar.gz |
| `checksum_dest` | 下载文件的校验和 | sha256:abc123... |
| `msg` | 操作结果消息 | Download completed |
| `state` | 文件状态 | file、absent |

## 使用情境

### 软件包下载
**场景**：从官方仓库下载软件包进行安装
- 下载应用程序二进制文件
- 获取软件包压缩文件
- 支持断点续传和校验和验证

### 配置文件获取
**场景**：从配置中心获取最新配置文件
- 下载应用配置文件
- 获取证书文件
- 支持认证和加密传输

### 资源文件部署
**场景**：部署静态资源和依赖文件
- 下载前端静态资源
- 获取依赖库文件
- 支持批量下载和版本控制

## 安全注意事项

1. **URL 安全性**：
   - 使用 HTTPS 协议确保传输安全
   - 验证服务器证书有效性
   - 避免使用不安全的 HTTP 下载敏感文件

2. **文件完整性验证**：
   - 始终使用校验和验证文件完整性
   - 使用 SHA-256 或更强的哈希算法
   - 定期更新校验和值

3. **认证和授权**：
   - 安全存储认证凭据（使用 Ansible Vault）
   - 使用最小权限原则配置访问权限
   - 定期轮换访问令牌和密钥

4. **目标路径安全**：
   - 确保目标目录具有适当的权限
   - 避免覆盖重要系统文件
   - 使用临时目录进行下载验证

## 环境依赖

### 必需
- 目标主机具有网络连接
- Python urllib3 库（通常已包含）
- 目标目录具有写入权限

### 推荐
- curl 或 wget 命令（用于备用下载）
- 足够的磁盘空间存储下载文件
- 稳定的网络连接

## 常见问题

### 1. 下载失败如何处理？
检查网络连接、URL 有效性、认证信息：
```yaml
- name: 下载文件并处理错误
  ansible.builtin.get_url:
    url: https://example.com/file
    dest: /tmp/file
    timeout: 30
  register: download_result
  retries: 3
  delay: 5
```

### 2. 如何验证文件完整性？
使用 checksum 参数验证：
```yaml
- name: 下载并验证文件
  ansible.builtin.get_url:
    url: https://example.com/file
    dest: /tmp/file
    checksum: sha256:{{ expected_checksum }}
```

### 3. 大文件下载超时怎么办？
增加 timeout 参数或使用分块下载：
```yaml
- name: 下载大文件
  ansible.builtin.get_url:
    url: https://example.com/large-file
    dest: /tmp/large-file
    timeout: 600
```

### 4. 如何处理认证？
使用 headers 参数或 URL 中包含认证信息：
```yaml
- name: 使用认证下载
  ansible.builtin.get_url:
    url: https://api.example.com/file
    dest: /tmp/file
    headers:
      Authorization: "Bearer {{ access_token }}"
```

## 最佳实践

### 安全下载配置
```yaml
- name: 安全下载应用软件包
  ansible.builtin.get_url:
    url: "{{ app_download_url }}"
    dest: "{{ app_download_path }}"
    checksum: "{{ app_checksum }}"
    mode: '0644'
    owner: "{{ app_user }}"
    group: "{{ app_group }}"
    timeout: 300
    headers:
      User-Agent: "Ansible/{{ ansible_version }}"
  become: yes
  register: download_result
  retries: 3
  delay: 10
```

### 批量文件下载
```yaml
- name: 批量下载依赖文件
  ansible.builtin.get_url:
    url: "{{ item.url }}"
    dest: "{{ item.dest }}"
    checksum: "{{ item.checksum }}"
    mode: '0644'
  loop: "{{ download_files }}"
  register: batch_download
```

### 下载验证和清理
```yaml
- name: 下载并验证软件包
  block:
    - name: 下载软件包
      ansible.builtin.get_url:
        url: "{{ package_url }}"
        dest: "/tmp/{{ package_name }}"
        checksum: "{{ package_checksum }}"
      register: package_download
    
    - name: 验证下载文件
      ansible.builtin.stat:
        path: "/tmp/{{ package_name }}"
      register: package_stat
    
    - name: 清理下载文件
      ansible.builtin.file:
        path: "/tmp/{{ package_name }}"
        state: absent
      when: cleanup_after_install | default(false)
```

## 相关示例
- [copy 模块](../copy/README.md) - 本地文件复制
- [template 模块](../template/README.md) - 模板文件部署
- [unarchive 模块](../unarchive/README.md) - 压缩文件解压