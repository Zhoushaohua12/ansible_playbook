# Block / Rescue / Always

Block 允许你把一组任务视为一个逻辑单元。当其中任一任务失败时，rescue 分支会被触发；无论成功或失败，always 分支都会执行，用于清理或记录状态。

## 语法
```yaml
- name: 升级并验证
  block:
    - name: 关键任务
      ansible.builtin.command: /path/to/action
  rescue:
    - name: 回滚
      ansible.builtin.command: /path/to/rollback
  always:
    - name: 收尾
      ansible.builtin.debug:
        msg: "完成"
```

## 参数
- `block`：必填，包含任意数量的任务；支持 `when`、`vars` 等常规关键字。
- `rescue`：可选，只有当 block 中至少一个任务失败时才会执行。
- `always`：可选，总会执行，常用来清理临时文件或记录日志。

## 返回值
Block 本身不返回独立结果，但可以在子任务中 `register`。Ansible 会沿用最后一个 task 的状态来判定整个 block 是否 changed。

## 常见陷阱
1. **忽略失败上下文**：rescue 中获取不到失败任务的 stdout/stderr，若需要请在失败任务中使用 `register`。
2. **跳过条件**：在 block 定义 `when` 能一口气跳过 block/rescue/always；如需单独控制 rescue，请在 rescue 里再次编写条件。
3. **错误回滚顺序**：rescue 任务默认与普通任务一样串行执行，必要时可再次使用 block 保证顺序。

## 如何调试/常见错误
- 使用 `--limit` 与 `--start-at-task` 仅在出错主机、出错任务重新触发，快速验证 rescue 是否被执行。
- 如果回滚步骤也可能失败，可在 rescue 内再嵌套一层 block/rescue 捕获二次错误，避免 Play 直接中止。

详细示例请参见 [playbook.yml](playbook.yml)。