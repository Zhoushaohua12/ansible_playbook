# script 模块使用指南

## 模块用途
`ansible.builtin.script` 模块将本地脚本文件传输到远程主机并执行。适用于需要执行复杂脚本逻辑的场景，同时保持脚本的可维护性和版本控制。

## 主要参数
- `cmd`：本地脚本的路径（必需参数）
- `chdir`：执行脚本前切换的工作目录
- `creates`：当指定文件存在时，跳过脚本执行（幂等性控制）
- `removes`：当指定文件不存在时，跳过脚本执行（幂等性控制）
- `executable`：指定脚本解释器（默认为脚本 shebang 或 /bin/sh）

## 返回值
- `changed`：脚本执行是否导致系统状态变更
- `rc`：脚本的返回码（0 表示成功）
- `stdout`：脚本的标准输出内容
- `stderr`：脚本的错误输出内容
- `cmd`：实际执行的脚本路径和参数

## 安全注意事项
1. **脚本审查**：确保脚本内容安全，避免恶意代码
2. **权限控制**：脚本文件需要有可读权限，执行权限由模块自动处理
3. **路径安全**：使用相对路径或 Ansible 变量，避免硬编码绝对路径
4. **错误处理**：在脚本中包含适当的错误处理逻辑

## 最佳实践

### 基础脚本执行示例
```yaml
- name: 执行本地部署脚本
  ansible.builtin.script: files/deploy_app.sh
  args:
    creates: /opt/app/deployed
```

### 带参数的脚本示例
```yaml
- name: 执行带参数的配置脚本
  ansible.builtin.script: files/configure.sh --env production --port 8080
  args:
    chdir: /opt/app
```

### 幂等性控制示例
```yaml
- name: 仅在未初始化时执行初始化脚本
  ansible.builtin.script: files/init_system.sh
  args:
    creates: /etc/system_initialized
```

## 脚本文件组织
```
script/
├── files/
│   ├── setup.sh          # 系统初始化脚本
│   ├── deploy.sh         # 应用部署脚本
│   └── backup.sh         # 备份脚本
├── vars/
│   └── example_vars.yml  # 脚本参数配置
├── playbook.yml          # 示例 playbook
└── README.md            # 本说明文档
```

## 脚本编写规范

### 脚本头部模板
```bash
#!/bin/bash
# 应用部署脚本
# 作者: Ansible 示例
# 用途: 演示 script 模块的使用

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 脚本内容...
```

### 错误处理示例
```bash
#!/bin/bash

# 错误处理函数
error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 检查必要条件
[ -f /etc/os-release ] || error_exit "无法检测操作系统类型"

# 主要逻辑
echo "开始执行脚本..."
# 执行具体操作
echo "脚本执行完成"
```

## 与其他模块的比较
| 特性 | script | shell | command | raw |
|------|--------|-------|---------|-----|
| 脚本来源 | 本地文件 | 内联命令 | 内联命令 | 内联命令 |
| 复杂逻辑 | ✅ 支持 | ✅ 支持 | ❌ 不支持 | ✅ 支持 |
| 版本控制 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 |
| 幂等性 | ✅ 支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |

## 测试步骤
1. 在 `files/` 目录下创建测试脚本
2. 在 `vars/example_vars.yml` 中配置脚本参数
3. 使用 `--check` 模式预览脚本执行（脚本模块支持 check 模式）
4. 验证脚本执行结果和系统状态变更

## 常见问题
- **脚本文件找不到？** 检查文件路径是否相对于 playbook 目录
- **脚本执行权限问题？** script 模块会自动设置执行权限
- **如何传递参数？** 在 cmd 参数后直接添加参数
- **脚本输出如何查看？** 使用 register 变量捕获 stdout 和 stderr

## 相关示例
- [shell 模块](../shell/README.md) - 内联 shell 命令执行
- [command 模块](../command/README.md) - 安全的简单命令执行
- [raw 模块](../raw/README.md) - 无 Python 环境的命令执行

## 脚本开发建议
1. **可测试性**：脚本应支持 dry-run 或测试模式
2. **幂等性**：脚本应能重复执行而不产生副作用
3. **日志记录**：提供详细的执行日志，便于调试
4. **参数化**：使用环境变量或参数传递配置信息