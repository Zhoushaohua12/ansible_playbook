# assemble 模块使用指南

## 模块用途
`ansible.builtin.assemble` 模块用于将多个文件片段组装成一个完整的文件。它按照指定顺序读取目录中的文件，将内容合并成单个目标文件。这个模块特别适用于配置文件管理、日志文件合并、证书链组装等场景，能够将分散的配置片段统一管理，提高配置文件的可维护性。

## 主要参数

| 参数 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `src` | str | 源目录路径（包含要组装的文件） | /etc/app/config.d |
| `dest` | str | 目标文件路径 | /etc/app/app.conf |
| `mode` | str | 目标文件权限 | '0644'、'0600' |
| `owner` | str | 目标文件所有者 | root、appuser |
| `group` | str | 目标文件所属组 | root、appgroup |
| `backup` | bool | 是否备份原文件 | true、false |
| `delimiter` | str | 文件间分隔符 | "\n---\n" |
| `regexp` | str | 文件名匹配正则表达式 | '.*\.conf$' |
| `ignore_hidden` | bool | 是否忽略隐藏文件 | true、false |

## 返回值

| 返回值 | 说明 | 示例 |
|--------|------|--------|
| `changed` | 是否组装了新文件 | true/false |
| `dest` | 目标文件路径 | /etc/app/app.conf |
| `checksum` | 组装后文件的校验和 | sha256:abc123... |
| `backup_file` | 备份文件路径 | /etc/app/app.conf.123456 |

## 使用情境

### 配置文件组装
**场景**：将分散的配置片段组装成完整配置文件
- 合并 Nginx 站点配置片段
- 组装应用模块配置
- 统一管理数据库配置片段

### 证书链组装
**场景**：将多个证书文件组装成完整的证书链
- 合并根证书、中间证书和服务器证书
- 组装 CA 证书链
- 创建完整的 SSL 证书文件

### 日志文件合并
**场景**：将多个日志文件合并成统一日志
- 合并应用日志片段
- 组装系统日志报告
- 创建统一的日志归档

## 安全注意事项

1. **文件内容安全**：
   - 确保源文件内容不包含敏感信息
   - 验证文件片段的来源和完整性
   - 避免组装未经验证的配置片段

2. **权限控制**：
   - 设置适当的文件权限保护配置文件
   - 限制配置文件的访问权限
   - 使用最小权限原则

3. **备份策略**：
   - 启用备份功能保护原配置
   - 定期清理旧备份文件
   - 建立配置版本控制机制

4. **顺序控制**：
   - 确保文件组装顺序符合预期
   - 使用命名约定控制文件顺序
   - 验证组装后的配置有效性

## 环境依赖

### 必需
- 源目录具有读取权限
- 目标目录具有写入权限
- Python 标准库（无需额外依赖）

### 推荐
- 文件排序工具（sort 命令）
- 配置验证工具
- 版本控制系统

## 常见问题

### 1. 如何控制文件组装顺序？
使用数字前缀或字母顺序命名：
```
01-basic.conf
02-advanced.conf
03-custom.conf
```

### 2. 组装后配置无效怎么办？
使用 delimiter 参数添加分隔符，便于调试：
```yaml
- name: 组装配置文件
  ansible.builtin.assemble:
    src: /etc/app/config.d
    dest: /etc/app/app.conf
    delimiter: "\n# --- {{ item }} ---\n"
```

### 3. 如何只组装特定类型的文件？
使用 regexp 参数过滤文件：
```yaml
- name: 只组装 .conf 文件
  ansible.builtin.assemble:
    src: /etc/app/config.d
    dest: /etc/app/app.conf
    regexp: '.*\.conf$'
```

### 4. 备份文件如何管理？
启用 backup 并定期清理：
```yaml
- name: 组装配置并备份
  ansible.builtin.assemble:
    src: /etc/app/config.d
    dest: /etc/app/app.conf
    backup: yes
```

## 最佳实践

### 分层配置管理
```yaml
- name: 分层组装应用配置
  block:
    - name: 组装基础配置
      ansible.builtin.assemble:
        src: /etc/app/config.d/base
        dest: /etc/app/base.conf
        mode: '0644'
    
    - name: 组装环境配置
      ansible.builtin.assemble:
        src: "/etc/app/config.d/{{ ansible_environment }}"
        dest: /etc/app/env.conf
        mode: '0644'
    
    - name: 组装完整配置
      ansible.builtin.assemble:
        src: /etc/app/final
        src_content: "{{ lookup('file', '/etc/app/base.conf') }}\n{{ lookup('file', '/etc/app/env.conf') }}"
        dest: /etc/app/app.conf
        mode: '0644'
        backup: yes
```

### 证书链组装
```yaml
- name: 组装 SSL 证书链
  ansible.builtin.assemble:
    src: /etc/ssl/certs/chain.d
    dest: /etc/ssl/certs/fullchain.pem
    mode: '0644'
    owner: root
    group: ssl-cert
    delimiter: "\n"
  notify: restart web server
```

## 相关示例
- [copy 模块](../copy/README.md) - 文件复制操作
- [template 模块](../template/README.md) - 模板文件生成
- [lineinfile 模块](../lineinfile/README.md) - 配置行修改