# raw 模块使用指南

## 模块用途
`ansible.builtin.raw` 模块直接通过 SSH 在目标主机执行命令，完全绕过 Ansible 的模块系统。适用于目标主机没有 Python 环境、系统处于引导阶段或需要执行底层系统维护的场景。

## 主要参数
- `cmd`：要执行的原始命令（必需参数）
- `free_form`：自由格式的命令字符串

## 返回值
- `changed`：命令执行是否导致系统状态变更
- `rc`：命令的返回码
- `stdout`：命令的标准输出内容
- `stderr`：命令的错误输出内容
- `cmd`：实际执行的命令

## 安全注意事项
⚠️ **高风险警告**：raw 模块会绕过 Ansible 的安全机制，请谨慎使用！

1. **绕过安全控制**：不经过 Ansible 的参数验证和权限检查
2. **无幂等性保证**：无法使用 Ansible 的幂等性机制
3. **依赖 SSH**：完全依赖 SSH 连接和目标系统的 shell 环境
4. **调试困难**：错误信息可能不够详细，调试难度较大

## 适用场景
- **无 Python 环境**：目标主机未安装 Python 或 Python 版本不兼容
- **系统引导阶段**：系统启动早期，Python 服务未启动
- **网络设备**：某些网络设备仅支持原始命令执行
- **紧急恢复**：系统故障恢复时的临时操作

## 安全使用建议

### 基础安全措施
```yaml
- name: 安全使用 raw 模块安装 Python
  ansible.builtin.raw: |
    # 仅在 Python 不存在时安装
    which python3 || (
      apt-get update &&
      apt-get install -y python3
    )
  register: python_install
  changed_when: "'Installing' in python_install.stdout"
```

### 条件检查示例
```yaml
- name: 检查 Python 可用性
  ansible.builtin.raw: test -f /usr/bin/python3
  register: python_check
  failed_when: false
  changed_when: false

- name: 使用 raw 模块安装必要软件
  ansible.builtin.raw: yum install -y python3
  when: python_check.rc != 0
```

## 与其他模块的比较
| 特性 | raw | shell | command |
|------|-----|-------|---------|
| Python 依赖 | ❌ 不需要 | ✅ 需要 | ✅ 需要 |
| 安全性 | ⚠️ 低 | ⚠️ 中等 | ✅ 高 |
| Shell 特性 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |
| 幂等性 | ❌ 无 | ✅ 支持 | ✅ 支持 |

## 最佳实践
1. **限制使用场景**：仅在绝对必要时使用 raw 模块
2. **前置检查**：使用条件判断避免重复执行
3. **事后验证**：执行完成后立即验证结果
4. **回退计划**：准备使用其他模块的替代方案

## 测试步骤
1. 在 `vars/example_vars.yml` 中配置测试参数
2. 使用 `--check` 模式预览（raw 模块不支持 check 模式）
3. 在隔离环境中测试命令执行
4. 验证系统状态变更符合预期

## 常见问题
- **为什么 raw 模块不支持 --check？** 因为它绕过 Ansible 系统，无法预测命令效果
- **如何处理 raw 模块的错误？** 检查返回码和错误输出，准备手动恢复方案
- **raw 模块可以执行复杂脚本吗？** 可以，但建议改用 script 模块
- **什么时候必须使用 raw 模块？** 目标主机无 Python 或系统引导阶段

## 相关示例
- [shell 模块](../shell/README.md) - 更安全的 shell 命令执行
- [command 模块](../command/README.md) - 最安全的命令执行方式
- [script 模块](../script/README.md) - 本地脚本传输执行

## 重要提醒
⚠️ **生产环境警告**：raw 模块会绕过 Ansible 的所有安全机制，建议仅在以下情况使用：
1. 目标主机无法安装 Python
2. 系统处于紧急维护状态
3. 网络设备等特殊环境

在常规自动化任务中，请优先选择 shell、command 或 script 模块。