# command 模块使用指南

## 模块用途
`ansible.builtin.command` 模块在目标主机上直接执行命令，不经过 shell 处理。这是最安全的命令执行方式，避免了 shell 注入风险，适用于执行简单的系统命令。

## 主要参数
- `cmd`：要执行的命令（必需参数）
- `chdir`：执行命令前切换的工作目录
- `creates`：当指定文件存在时，跳过任务执行（幂等性控制）
- `removes`：当指定文件不存在时，跳过任务执行（幂等性控制）
- `argv`：以列表形式传递命令参数，避免 shell 解释

## 返回值
- `changed`：命令执行是否导致系统状态变更
- `rc`：命令的返回码（0 表示成功）
- `stdout`：命令的标准输出内容
- `stderr`：命令的错误输出内容
- `cmd`：实际执行的命令字符串

## 安全注意事项
1. **无 Shell 风险**：不经过 shell 处理，避免 shell 注入攻击
2. **参数安全**：使用 `argv` 参数传递复杂参数列表
3. **命令限制**：不支持管道、重定向、环境变量等 shell 特性
4. **幂等性**：配合 `creates`/`removes` 实现安全的幂等操作

## 最佳实践

### 简单命令示例
```yaml
- name: 安全执行系统命令
  ansible.builtin.command: systemctl status nginx
  register: nginx_status
  changed_when: false  # 仅查询状态，不修改系统
```

### 使用 argv 参数示例
```yaml
- name: 使用参数列表执行命令
  ansible.builtin.command:
    argv:
      - /usr/bin/python3
      - -c
      - "import sys; print(sys.version)"
  register: python_version
```

### 幂等性控制示例
```yaml
- name: 仅在文件不存在时创建
  ansible.builtin.command: touch /tmp/app_initialized
  args:
    creates: /tmp/app_initialized
```

## 与 shell 模块的区别
- **安全性**：command 模块更安全，无 shell 注入风险
- **功能限制**：不支持管道、重定向等 shell 特性
- **性能**：直接执行，性能略优于 shell 模块
- **适用场景**：简单命令使用 command，复杂操作使用 shell

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置示例参数
2. 验证命令执行的幂等性
3. 测试 `creates`/`removes` 参数效果
4. 检查返回值和错误处理

## 常见问题
- **为什么不能使用管道？** command 模块不经过 shell 处理，需要管道时请使用 shell 模块
- **如何传递多个参数？** 使用 `argv` 参数列表，避免参数解析问题
- **何时使用 changed_when: false？** 仅查询状态或只读操作时设置
- **creates 和 removes 如何选择？** creates 用于创建文件，removes 用于删除文件

## 相关示例
- [shell 模块](../shell/README.md) - 支持 shell 特性的命令执行
- [raw 模块](../raw/README.md) - 无 Python 环境的命令执行
- [script 模块](../script/README.md) - 本地脚本传输执行