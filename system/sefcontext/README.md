# sefcontext 模块使用指南

## 模块用途
`ansible.posix.sefcontext` 模块用于管理 SELinux 文件安全上下文映射，定义文件和目录的默认 SELinux 安全标签。通过配置文件上下文映射，可以确保新创建的文件自动获得正确的 SELinux 上下文，或修改现有文件的上下文映射规则。在需要自定义应用文件安全策略、配置非标准目录结构、或修复文件上下文问题时，这个模块是必不可少的工具。

## 主要参数

| 参数 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `target` | str | 文件或目录路径模式（支持通配符） | /opt/myapp(/.*)? |
| `setype` | str | 设置 SELinux 类型 | httpd_sys_content_t、var_log_t |
| `seuser` | str | 设置 SELinux 用户 | system_u、root |
| `serange` | str | 设置 SELinux 范围 | s0、s0-s15:c0.c1023 |
| `state` | str | 上下文状态（present/absent） | present、absent |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否修改了上下文映射 | true/false |
| `target` | 目标路径模式 | /opt/myapp(/.*)? |
| `setype` | 设置的类型 | httpd_sys_content_t |

## 使用情境

### Web 应用目录配置
**场景**：为自定义 Web 应用目录设置正确的 SELinux 上下文
- 配置 /opt/myapp 目录为 httpd_sys_content_t
- 设置日志目录为 httpd_log_t
- 确保临时文件目录为 httpd_tmp_t

### 应用数据目录管理
**场景**：为应用数据目录设置适当的安全上下文
- 配置数据库数据目录为 mysqld_db_t
- 设置应用配置文件为 etc_t
- 配置上传目录为 httpd_sys_rw_content_t

### 日志文件管理
**场景**：为自定义日志目录设置日志文件上下文
- 配置应用日志目录为 var_log_t
- 设置审计日志为 auditd_log_t
- 确保日志轮转目录正确标记

## 安全注意事项

1. **上下文映射影响范围**：
   - 文件上下文映射影响所有匹配路径的文件
   - 新创建的文件会自动获得映射的上下文
   - 现有文件需要使用 restorecon 更新上下文

2. **路径模式设计**：
   - 使用精确的路径模式避免误匹配
   - 通配符 (/.*)? 可以匹配子目录
   - 测试路径模式确保覆盖预期范围

3. **权限最小化**：
   - 只配置应用必需的文件上下文
   - 避免过度宽松的安全上下文
   - 定期审查上下文映射的必要性

4. **变更影响评估**：
   - 评估上下文变更对现有文件的影响
   - 在测试环境验证配置效果
   - 准备回滚方案

## 环境依赖

### 必需
- 目标主机支持 SELinux（RHEL、CentOS、Fedora 等）
- selinux-policy-targeted 或相关策略包
- policycoreutils 包（包含 semanage 命令）
- 需要 root 或 sudo 权限

### 推荐
- policycoreutils-python-utils 包
- setools-console 包（用于上下文分析）
- restorecon 命令（用于应用上下文）

## 常见问题

### 1. 如何查看当前文件上下文？
使用 ls -Z 或 stat 命令查看：
```bash
ls -Z /path/to/file
stat -c %C /path/to/file
```

### 2. 上下文映射何时生效？
映射立即生效，但现有文件需要运行 restorecon 应用新上下文。

### 3. 如何查看所有上下文映射？
使用 semanage fcontext -l 命令：
```bash
semanage fcontext -l
```

### 4. 路径模式中的通配符是什么意思？
- (/.*)? 匹配当前目录和所有子目录
- /.* 匹配所有子目录但不包含当前目录
- 普通路径只匹配精确路径

## 最佳实践

### 分阶段配置应用上下文
```yaml
- name: 分阶段配置应用 SELinux 上下文
  block:
    - name: 第一阶段：配置应用主目录
      ansible.posix.sefcontext:
        target: /opt/myapp(/.*)?
        setype: httpd_sys_content_t
        state: present
      become: yes
      
    - name: 第二阶段：配置日志目录
      ansible.posix.sefcontext:
        target: /var/log/myapp(/.*)?
        setype: var_log_t
        state: present
      become: yes
      
    - name: 第三阶段：应用上下文到现有文件
      ansible.builtin.command: restorecon -R /opt/myapp
      become: yes
      when: apply_context_immediately | default(false)
```

### 上下文验证和修复
```yaml
- name: 验证文件上下文配置
  block:
    - name: 检查文件上下文
      ansible.builtin.shell: ls -Z /opt/myapp
      register: current_context
      changed_when: false
      
    - name: 修复不正确的上下文
      ansible.builtin.command: restorecon -R /opt/myapp
      become: yes
      when: "'httpd_sys_content_t' not in current_context.stdout"
```

## 相关示例
- [selinux 模块](../selinux/README.md) - SELinux 整体配置管理
- [seboolean 模块](../seboolean/README.md) - SELinux 布尔值管理
- [file 模块](../../files/file/README.md) - 文件系统基础操作