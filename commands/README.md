# 命令执行模块指南

## 章节概览
本章节介绍 Ansible 中五个核心命令执行模块的使用差异、安全风险与最佳实践。这些模块允许在目标主机上执行命令和脚本（包含交互式输入场景），但各自有不同的适用场景和安全考虑。所有示例均包含中文注释，并强调幂等性和安全防护措施。

## 模块对比

| 模块 | Shell 环境支持 | Python 依赖 | 安全风险 | 适用场景 |
|------|----------------|-------------|----------|----------|
| `shell` | ✅ 完整支持 | ✅ 需要 | ⚠️ 中等（Shell 注入风险） | 需要管道、重定向、环境变量的复杂命令 |
| `command` | ❌ 无 Shell | ✅ 需要 | ✅ 低（直接执行） | 安全的简单命令执行 |
| `raw` | ✅ 完整支持 | ❌ 不需要 | ⚠️ 高（绕过 Ansible） | 无 Python 环境或系统引导阶段 |
| `script` | ✅ 依赖脚本 | ✅ 需要 | ⚠️ 中等（脚本内容风险） | 传输并执行本地脚本文件 |
| `expect` | ✅ 交互式支持 | ✅ 需要 | ⚠️ 高（敏感信息泄露） | 自动响应交互式提示（密码、确认等） |

## 涉及模块
- [shell 模块](shell/README.md)：通过系统 shell 执行命令，支持管道和重定向
- [command 模块](command/README.md)：安全执行命令，不经过 shell 处理
- [raw 模块](raw/README.md)：直接 SSH 执行，适用于无 Python 环境
- [script 模块](script/README.md)：传输本地脚本到远程主机执行
- [expect 模块](expect/README.md)：自动回应交互式提示，适用于密码输入、确认流程等场景

## 安全使用建议

### 通用安全原则
1. **最小权限原则**：仅在受控主机上运行命令执行模块
2. **幂等性设计**：使用 `creates`、`removes`、`changed_when` 确保幂等
3. **输入验证**：避免将用户输入直接传递给命令参数
4. **审计日志**：重要操作应记录到系统日志

### 模块特定注意事项
- **shell 模块**：设置 `warn: false` 或在脚本中使用 `set -e`
- **command 模块**：优先选择，避免 shell 注入风险
- **raw 模块**：谨慎使用，会绕过 Ansible 的安全机制
- **script 模块**：审查脚本内容，避免硬编码敏感信息
- **expect 模块**：务必使用 `no_log: true` 和 Ansible Vault 保护敏感信息

## 测试与验证策略
1. **中文文档校验**：确保所有 README 和 playbook 包含中文注释
2. **安全检查**：验证 shell 模块包含安全说明，command 模块未启用 shell
3. **幂等性验证**：检查 creates/removes 参数的使用
4. **pytest 校验**：`tests/commands/test_commands.py` 自动检查文档结构和安全规范

## 文件结构
```
commands/
├── README.md                # 本说明文档
├── shell/                   # shell 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── command/                 # command 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── raw/                     # raw 模块示例
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
├── expect/                  # expect 模块示例（交互式）
│   ├── README.md
│   ├── playbook.yml
│   └── vars/example_vars.yml
└── script/                  # script 模块示例
    ├── README.md
    ├── playbook.yml
    ├── vars/example_vars.yml
    └── files/example.sh
```

## 快速开始
1. 进入目标模块目录，例如 `commands/shell/`。
2. 按需修改 `vars/example_vars.yml` 中的示例参数。
3. 执行：
   ```bash
   ansible-playbook playbook.yml -i hosts.ini --check
   ```
4. 验证输出，确认命令执行符合预期后再正式运行。

## 常见问题
- **何时使用 shell vs command？** 需要管道、重定向时用 shell，简单命令用 command
- **raw 模块为什么风险高？** 绕过 Ansible 的模块系统，直接执行 SSH 命令
- **如何确保幂等性？** 使用 creates/removes 参数，或设置 changed_when 条件
- **脚本传输失败怎么办？** 检查文件权限和路径，确保脚本可读且目标路径可写

## 相关链接
- [Ansible Command Module 官方文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/command_module.html)
- [Ansible Shell Module 官方文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/shell_module.html)
- [Ansible Raw Module 官方文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/raw_module.html)
- [Ansible Script Module 官方文档](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/script_module.html)