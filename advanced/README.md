# 高级特性总览

本章节汇总了在真实生产环境中最常见的 Ansible 高级特性，并配套可运行的 Playbook 示例。每个小节都会说明它要解决的问题、与其他指令的组合方式以及需要避开的陷阱。

## Block / Rescue / Always
- **用途**：将相邻任务组织为一个原子单元，失败时执行补救（rescue），无论结果如何都执行清理（always）。
- **何时使用**：涉及多步变更、需要回滚或清理的场景，如升级服务、批量写配置。
- **示例**：[block_rescue](block_rescue/README.md) 展示了失败回滚、日志标记与最终状态输出的组合。

## 条件判断（when）
- **用途**：在运行时根据变量、事实或表达式选择性执行任务。
- **何时使用**：跨环境部署、按主机标签区分路径或需要跳过冗余步骤时。
- **示例**：[when_conditions](when_conditions/README.md) 通过 `when`、`ansible_facts` 与自定义变量控制服务启停。

## 循环（loop）
- **用途**：对列表、字典或查询结果重复执行任务。
- **何时使用**：批量管理用户、遍历主机列表、配置多端口或多实例。
- **示例**：[loop_iteration](loop_iteration/README.md) 展示如何通过 `loop_control.loop_var` 明确循环变量，避免冲突。

## 变量与 `set_fact`
- **用途**：在 Play 执行过程中生成临时变量或归并计算结果。
- **何时使用**：依赖前置任务输出、根据条件拼装命令、缓存远端信息时。
- **示例**：[set_fact_vars](set_fact_vars/README.md) 通过 `set_fact` 组合结构化变量并注册为 `ansible_facts`。

## Handler 与 Notify
- **用途**：在任务变更后触发一次性处理（重启、刷新缓存等），避免重复执行。
- **何时使用**：配置文件变更、模板渲染、包升级后需统一收尾时。
- **示例**：[handlers_notify](handlers_notify/README.md) 创建多级 notify 链路，展示重启与审计 handler 的协作方式。

## Include Tasks
- **用途**：将 Playbook 切分为更小的模块，按需动态引入。
- **何时使用**：复用通用任务、依据条件加载子任务、保持主 Playbook 精简时。
- **示例**：[include_tasks](include_tasks/README.md) 调用带中文注释的子任务文件，并传入变量定制行为。

## 如何调试/常见错误
1. **善用 `-vvv` 与 `--start-at-task`**：发现 block/rescue 逻辑问题时，直接从出错任务重新执行，观察 rescue 是否被正确触发。
2. **检查变量作用域**：`set_fact` 默认保存在当前主机的 facts 中，跨 Play 使用时需配合 `cacheable` 或重新计算。
3. **循环变量命名**：当 tasks 引用其他变量时务必设置 `loop_control.loop_var`，否则 `item` 可能与现有变量冲突。
4. **Handler 触发时机**：handler 只会在任务标记为 changed 后执行，并且在 Play 末尾统一触发，可用 `meta: flush_handlers` 强制立刻执行。
5. **Include 路径与变量传递**：相对路径以调用任务所在目录为基准，测试文件会帮助你确认子任务已就绪且包含可读注释。