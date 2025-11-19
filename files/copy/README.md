# copy 模块使用指南

## 模块用途
`ansible.builtin.copy` 模块用于将文件从控制节点复制到远程主机，或在远程主机内部复制文件。它是最基础的文件分发模块，适用于静态文件传输场景。

## 主要参数
- `src`：源文件路径（控制节点本地文件）或源目录
- `dest`：目标文件路径（远程主机）- 必需参数
- `content`：直接指定文件内容（替代 src 参数）
- `backup`：覆盖前备份目标文件（默认 false）
- `owner`：设置文件所有者
- `group`：设置文件所属组
- `mode`：设置文件权限（如 '0644'）
- `remote_src`：设为 true 时从远程主机复制（而非控制节点）
- `force`：目标文件存在时是否强制覆盖（默认 true）
- `validate`：复制后运行验证命令（如配置文件语法检查）

## 返回值
- `changed`：文件是否被复制或修改
- `dest`：目标文件的完整路径
- `checksum`：文件的 SHA1 校验和
- `size`：文件大小（字节）
- `owner`：文件所有者
- `group`：文件所属组
- `mode`：文件权限

## 使用场景

### 配置文件分发
将应用配置文件、服务配置、脚本等从控制节点统一分发到多台服务器。

### 证书和密钥部署
安全地传输 SSL 证书、SSH 密钥等敏感文件，并设置正确的权限。

### 静态资源发布
部署 HTML、CSS、JavaScript、图片等 Web 静态资源。

### 备份和归档
在远程主机内部复制文件用于备份（需使用 `remote_src: yes`）。

## 最佳实践

### 文件权限设置
```yaml
# 部署应用配置文件并设置权限
- name: 复制应用配置文件
  ansible.builtin.copy:
    src: files/app_config.yml
    dest: /opt/app/config/app_config.yml
    owner: appuser
    group: appgroup
    mode: '0640'
```

### 备份原文件
```yaml
# 覆盖前自动备份
- name: 更新配置文件（备份旧版本）
  ansible.builtin.copy:
    src: files/nginx.conf
    dest: /etc/nginx/nginx.conf
    backup: yes
  notify: 重新加载 Nginx
```

### 配置文件验证
```yaml
# 复制后验证配置文件语法
- name: 部署 Nginx 配置并验证
  ansible.builtin.copy:
    src: files/nginx.conf
    dest: /etc/nginx/nginx.conf
    validate: /usr/sbin/nginx -t -c %s
```

### 直接指定内容
```yaml
# 使用 content 参数直接写入内容
- name: 创建简单配置文件
  ansible.builtin.copy:
    content: |
      # 应用配置
      APP_ENV=production
      DEBUG=false
    dest: /etc/app/environment
    mode: '0644'
```

### 目录复制
```yaml
# 复制整个目录
- name: 复制静态资源目录
  ansible.builtin.copy:
    src: files/static/
    dest: /var/www/html/static/
    owner: www-data
    group: www-data
    mode: '0755'
```

## 注意事项

### 编码问题
- 确保控制节点和远程主机使用相同的文件编码（推荐 UTF-8）
- 包含中文的配置文件应保存为 UTF-8 编码（无 BOM）

### 幂等性
- copy 模块默认使用 checksum 比较文件内容
- 仅当文件内容实际变化时才会报告 changed
- 多次执行相同的 copy 任务不会触发不必要的变更

### 性能考虑
- 复制大文件或大量文件时，考虑使用 `synchronize` 模块（基于 rsync）
- `copy` 模块适用于中小型文件和精确控制权限的场景

### 权限提升
- 复制到系统目录（如 /etc）需要 `become: yes`
- 设置 owner/group 也需要 root 权限

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置文件路径和权限参数
2. 准备待复制的示例文件到 `files/` 目录
3. 使用 `--check` 模式预览操作
4. 使用 `--diff` 查看文件内容差异
5. 实际执行并验证文件权限和内容

## 常见问题
- **为什么文件没有被复制？** 检查 `force: false` 是否导致跳过已存在的文件
- **如何在远程主机之间复制文件？** 使用 `remote_src: yes` 并指定远程路径
- **如何只复制变化的文件？** copy 默认就是幂等的，会自动比较 checksum
- **如何复制包含变量的配置文件？** 使用 `template` 模块而非 `copy`

## 与其他模块的比较
- **copy vs template**：copy 用于静态文件，template 用于需要变量替换的文件
- **copy vs synchronize**：copy 适合单文件或小规模分发，synchronize 适合大规模目录同步
- **copy vs file**：file 用于创建空文件、目录、符号链接，copy 用于传输文件内容

## 相关示例
- [template 模块](../template/README.md) - 动态配置文件生成
- [file 模块](../file/README.md) - 文件系统基础操作
- [synchronize 模块](../synchronize/README.md) - 高效目录同步
