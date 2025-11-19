# shell 模块使用指南

## 模块用途
`ansible.builtin.shell` 模块通过目标主机的系统 shell 执行命令，支持管道符、重定向、环境变量等 shell 特性。适用于需要复杂 shell 操作的场景，但需要注意 shell 注入风险。

## 主要参数
- `cmd`：要执行的 shell 命令，支持管道、重定向等 shell 特性
- `chdir`：执行命令前切换的工作目录
- `creates`：当指定文件存在时，跳过任务执行（幂等性控制）
- `removes`：当指定文件不存在时，跳过任务执行（幂等性控制）
- `warn`：设为 false 可禁用 shell 命令警告（推荐在脚本中使用 set -e）
- `executable`：指定使用的 shell 程序（默认为 /bin/sh）

## 返回值
- `changed`：命令执行是否导致系统状态变更
- `rc`：命令的返回码（0 表示成功）
- `stdout`：命令的标准输出内容
- `stderr`：命令的错误输出内容
- `cmd`：实际执行的命令字符串

## 安全注意事项
1. **Shell 注入防护**：避免将用户输入直接拼接到命令中
2. **错误处理**：在复杂脚本中使用 `set -e` 确保错误时退出
3. **禁用警告**：设置 `warn: false` 并在脚本中处理错误
4. **幂等性**：使用 `creates`/`removes` 参数避免重复执行

## 最佳实践

### 多行命令示例
```yaml
- name: 多行 shell 命令执行
  ansible.builtin.shell: |
    set -e  # 遇到错误立即退出
    source /etc/environment
    echo "开始处理配置文件" >> /var/log/setup.log
    cp /etc/origin.conf /etc/backup.conf
    sed -i 's/old_value/new_value/g' /etc/origin.conf
  args:
    creates: /etc/backup.conf
    warn: false
```

### 管道和重定向示例
```yaml
- name: 使用管道处理日志
  ansible.builtin.shell: |
    grep "ERROR" /var/log/app.log | wc -l > /tmp/error_count.txt
  args:
    warn: false
```

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置示例参数
2. 使用 `--check` 模式预览命令执行计划
3. 验证 `creates`/`removes` 参数的幂等性效果
4. 检查标准输出和错误输出内容

## 常见问题
- **为什么不推荐直接使用 shell？** 存在 shell 注入风险，优先使用 command 模块
- **如何处理命令失败？** 使用 `set -e` 或检查返回码 `failed_when: rc != 0`
- **何时需要设置 warn: false？** 当命令包含特殊字符或已内置错误处理时
- **creates 和 removes 有什么区别？** creates 检查文件存在，removes 检查文件不存在

## 相关示例
- [command 模块](../command/README.md) - 更安全的命令执行方式
- [raw 模块](../raw/README.md) - 无 Python 环境的命令执行
- [script 模块](../script/README.md) - 本地脚本传输执行