# Block / Rescue / Always 组合进阶

Block 允许把多条任务当作原子单元执行，搭配 `rescue` 和 `always` 可以在失败时执行补救并保证收尾逻辑始终运行。本示例在同一个 block 内结合 `when` 条件、循环和日志清理，展示真实生产场景常见的回滚流程。

## 适用场景
- 多步骤配置修改：更新多个配置文件或服务，要求要么全部成功，要么回滚
- 动态批量操作：通过 `loop` 遍历多条命令，任意一步失败都触发回滚
- 故障收集与清理：在 `always` 中上传日志或清理临时文件，确保环境一致

## 示例亮点
1. **Block 入口条件**：在 block 上使用 `when` 控制整个原子操作是否执行
2. **循环任务**：通过 `loop` 批量执行危险操作，结合 `loop_control.loop_var` 避免变量冲突
3. **Rescue 回滚**：捕获失败信息，使用 `ansible_failed_result` 打印出错原因并执行回滚命令
4. **Always 收尾**：无论成功与否都清理日志文件/临时目录，防止残留状态

## 最佳实践
- 使用 `register` 收集 block 中关键任务的状态，rescue 可以读取同名变量判断回滚策略
- 在 block/rescue 中保持相同的变量命名，方便通过 `ansible_failed_task.name` 快速定位故障
- 在 `always` 中避免再次抛出错误，可用 `failed_when: false` 或 `ignore_errors: true` 确保收尾顺利

## 常见陷阱
1. **rescue 缺乏上下文**：需要提前通过 `register` 保存关键信息
2. **always 未处理错误**：清理动作仍可能失败，必要时再次套一个 block 捕获错误
3. **when 写在子任务而非 block**：如果希望整组任务跳过，需要把条件写在 block 顶层

完整 Playbook 请查看 [playbook.yml](playbook.yml)，示例变量见 [vars/example_vars.yml](vars/example_vars.yml)。
